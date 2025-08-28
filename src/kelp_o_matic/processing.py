"""High-level image processing with tiled segmentation and post-processing."""

from __future__ import annotations

import math
import sys
from typing import TYPE_CHECKING

import cv2
import numpy as np
import rasterio
from rasterio.windows import Window
from rich.progress import (
    BarColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

from kelp_o_matic.config import ProcessingConfig
from kelp_o_matic.hann import BartlettHannKernel, NumpyMemoryRegister
from kelp_o_matic.utils import batched, console

if TYPE_CHECKING:
    from collections.abc import Generator, Iterable
    from pathlib import Path

    from kelp_o_matic.model import ONNXModel


class ImageProcessor:
    """High-level image processor that orchestrates model inference and tiled processing."""

    def __init__(self, model: ONNXModel) -> None:
        """Initialize the ImageProcessor.

        Args:
            model: The ONNXModel instance to use for inference

        """
        self.model = model

    def process(
        self,
        img_path: str | Path,
        output_path: str | Path,
        *,
        batch_size: int = 1,
        crop_size: int | None = None,
        blur_kernel_size: int = 5,
        morph_kernel_size: int = 0,
        band_order: list[int] | None = None,
    ) -> None:
        """Process an image using tiled segmentation with overlap handling.

        Args:
            img_path: Path to input raster
            output_path: Path to output segmentation raster
            batch_size: Batch size for processing
            crop_size: Tile size for processing (uses model's preferred size if None)
            blur_kernel_size: Size of median blur kernel (must be odd)
            morph_kernel_size: Size of morphological kernel (0 to disable)
            band_order: Band order for rearranging input image bands

        """
        # Determine tile size
        if crop_size is None:
            # Default to 1024 if model does not specify
            crop_size = self.model.input_size or 1024
        elif self.model.input_size is not None and crop_size != self.model.input_size:
            from rich.panel import Panel

            warning_panel = Panel(
                f"[yellow]Specified tile size {crop_size} does not match model preferred size {self.model.input_size}. "
                f"Using model preferred size of {self.model.input_size}.[/yellow]",
                title="[bold yellow]Tile Size Warning[/bold yellow]",
                border_style="yellow",
            )
            console.print(warning_panel)
            crop_size = self.model.input_size

        # Create processing configuration
        if band_order is None:
            band_order = [i + 1 for i in range(self.model.cfg.input_channels)]

        config = ProcessingConfig(
            crop_size=crop_size,
            batch_size=batch_size,
            blur_kernel_size=blur_kernel_size,
            morph_kernel_size=morph_kernel_size,
            band_order=band_order,
        )

        # Process using tiled approach
        self._process_raster(img_path, output_path, config)

    def _process_raster(
        self,
        img_path: str | Path,
        output_path: str | Path,
        config: ProcessingConfig,
    ) -> None:
        """Process a raster file with tiled segmentation.

        Args:
            img_path: Path to input raster
            output_path: Path to output segmentation raster
            config: Processing configuration

        Raises:
            RuntimeError: If the window generation fails to provide full coverage of the image.
        """
        register = None

        with rasterio.open(img_path) as src:
            # Get raster properties
            height, width = src.height, src.width
            dtype = src.dtypes[0]
            profile = src.profile.copy()

            if self.model.cfg.max_pixel_value == "auto":
                # Automatically determine max pixel value based on dtype
                if dtype == "uint8":
                    self.model.cfg.max_pixel_value = 255
                elif dtype == "uint16":
                    self.model.cfg.max_pixel_value = 65535
                elif dtype in ["float16", "float32", "float64"]:
                    # Warn that float types should be normalized
                    console.print(
                        "[yellow]Warning: Input image has float data type. "
                        "Ensure pixel values are in range [0,1] to avoid unexpected results.[/yellow]",
                    )
                    self.model.cfg.max_pixel_value = 1.0
                else:
                    console.print(
                        f"[red]Unsupported image data type {dtype} for model. "
                        f"Convert your image to uint8 or uint16 before processing.[/red]",
                    )
                    sys.exit(0)

            # Update profile for output
            profile.update({"dtype": "uint8", "count": 1, "compress": "lzw"})

            # Calculate extended dimensions to accommodate full tiles
            extended_height, extended_width = self._calculate_extended_dimensions(
                height,
                width,
                config,
            )

            # Generate tiles and process in batches
            windows = list(
                self._generate_windows(extended_height, extended_width, config),
            )

            # Validate that we have full coverage of the original image
            if not self._validate_full_coverage(height, width, windows):
                raise RuntimeError(
                    f"Window generation failed to provide full coverage of image "
                    f"(original: {height}x{width}, extended: {extended_height}x{extended_width})",
                )

            window_batches = list(batched(windows, n=config.batch_size))

            with rasterio.open(output_path, "w", **profile) as dst:
                with Progress(
                    TextColumn("[bold blue]Segmenting"),
                    BarColumn(),
                    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                    TimeElapsedColumn(),
                    TimeRemainingColumn(),
                    console=console,
                ) as progress:
                    task = progress.add_task("Processing", total=len(window_batches))
                    for window_batch in window_batches:
                        # Read tile data from source raster
                        input_batch = self._load_batch(src, window_batch, config)

                        # Shortcut to write zeros if all pixels have the same value in each img
                        for i, (window, img) in enumerate(zip(window_batch, input_batch)):
                            if np.all(img == img.flatten()[0]):
                                clipped_window = self._clip_window_to_image_bounds(window, height, width)

                                # Skip windows that are completely outside the image bounds
                                if clipped_window is not None:
                                    data = np.zeros((clipped_window.height, clipped_window.width), dtype=np.uint8)
                                    dst.write(data, 1, window=clipped_window)

                                # Remove from batch
                                window_batch = list(window_batch)
                                window_batch.pop(i)
                                window_batch = tuple(window_batch)
                                input_batch = np.delete(input_batch, i, axis=0)

                        # If all windows were removed, skip processing and update progress
                        if len(window_batch) == 0:
                            progress.update(task, advance=1, refresh=True)
                            continue

                        # Process batch through model
                        result_batch = self.model._predict(input_batch)

                        if register is None:
                            num_classes = result_batch.shape[1]
                            register = NumpyMemoryRegister(
                                image_width=width,
                                register_depth=num_classes,
                                window_size=config.crop_size,
                                kernel=BartlettHannKernel,
                            )

                        # Apply post-processing to each result
                        for read_window, model_output in zip(
                            window_batch,
                            result_batch,
                            strict=False,
                        ):
                            clipped_window = self._clip_window_to_image_bounds(read_window, height, width)

                            # Skip windows that are completely outside the image bounds
                            if clipped_window is None:
                                continue

                            # Edge detection based on clipped window
                            is_top = clipped_window.row_off == 0
                            is_bottom = clipped_window.row_off + clipped_window.height >= height
                            is_left = clipped_window.col_off == 0
                            is_right = clipped_window.col_off + clipped_window.width >= width

                            data, write_window = register._step(
                                model_output,
                                clipped_window,
                                top=is_top,
                                bottom=is_bottom,
                                left=is_left,
                                right=is_right,
                            )
                            data = self.model._postprocess(data)
                            dst.write(data, 1, window=write_window)

                        progress.update(task, advance=1, refresh=True)

            # Apply final post-processing
            self._apply_final_postprocessing(output_path, config)

    def _clip_window_to_image_bounds(
        self,
        window: Window,
        height: int,
        width: int,
    ) -> Window | None:
        """Clip a window to fit within image bounds.

        Args:
            window: The original window.
            height: Height of the image.
            width: Width of the image.

        Returns:
            A new Window object clipped to the image bounds or None if the window is completely outside the image.
        """
        clipped_height = max(0, min(window.height, height - window.row_off))
        clipped_width = max(0, min(window.width, width - window.col_off))

        # Test if windows is completely outside the image bounds
        if clipped_height <= 0 or clipped_width <= 0 or window.row_off >= height or window.col_off >= width:
            return None

        return Window(
            col_off=window.col_off,
            row_off=window.row_off,
            height=clipped_height,
            width=clipped_width,
        )

    @staticmethod
    def _load_batch(
        src: rasterio.io.DatasetReader,
        windows: Iterable[Window],
        config: ProcessingConfig,
    ) -> np.ndarray:
        """Load a batch of tiles from the source raster using boundless reading.

        Args:
            src: Rasterio dataset reader for the source raster.
            windows: Iterable of windows to load.
            config: Processing configuration.

        Returns:
            Numpy array of shape [batch_size, channels, height, width] containing the tile data.
        """
        tile_data = []
        for window in windows:
            # Use boundless reading to handle out-of-bounds areas with fill_value=0
            tile_img = src.read(window=window, boundless=True, fill_value=0)
            _, th, tw = tile_img.shape

            # Pad out to tile size if needed (shouldn't be necessary with boundless reading)
            if th < config.crop_size or tw < config.crop_size:
                tile_img = np.pad(
                    tile_img,
                    (
                        (0, 0),
                        (0, config.crop_size - th),
                        (0, config.crop_size - tw),
                    ),
                    mode="constant",
                    constant_values=0,
                )

            # Rearrange/select bands
            try:
                tile_img = tile_img[[b - 1 for b in config.band_order], ...]
            except IndexError:
                console.print(
                    f"[bold red]Band order {config.band_order} is invalid for image with {src.count} bands.\n"
                    f"You may be using a model intended for images with a {len(config.band_order)} bands.",
                )
                sys.exit(1)
            tile_data.append(tile_img)

        # Stack into batch array [b, c, h, w]
        return np.stack(tile_data, axis=0)

    @staticmethod
    def _calculate_extended_dimensions(
        height: int,
        width: int,
        config: ProcessingConfig,
    ) -> tuple[int, int]:
        """Calculate extended dimensions to fit complete tiles.

        Args:
            height: Original height of the image.
            width: Original width of the image.
            config: Processing configuration.

        Returns:
            Tuple of (extended_height, extended_width) that ensures full tile coverage.
        """
        tile_size = config.crop_size
        stride = config.stride

        # Calculate number of tiles needed using same logic as _generate_windows
        if height <= tile_size:
            tiles_y = 1
        else:
            tiles_y = math.ceil((height - tile_size) / stride) + 1

        if width <= tile_size:
            tiles_x = 1
        else:
            tiles_x = math.ceil((width - tile_size) / stride) + 1

        # Calculate extended dimensions to ensure full coverage
        extended_height = (tiles_y - 1) * stride + tile_size
        extended_width = (tiles_x - 1) * stride + tile_size

        return max(extended_height, height), max(extended_width, width)

    @staticmethod
    def _validate_full_coverage(
        height: int,
        width: int,
        windows: list[Window],
    ) -> bool:
        """Validate that the generated windows provide full coverage of the image.

        Args:
            height: Original height of the image.
            width: Original width of the image.
            windows: Iterable of windows to validate.

        Returns:
            True if all pixels are covered, False otherwise.
        """
        # Create a coverage map to track which pixels are covered
        coverage = np.zeros((height, width), dtype=bool)

        for window in windows:
            row_start = max(0, window.row_off)
            row_end = min(height, window.row_off + window.height)
            col_start = max(0, window.col_off)
            col_end = min(width, window.col_off + window.width)

            coverage[row_start:row_end, col_start:col_end] = True

        # Check if all pixels are covered
        return np.all(coverage)

    @staticmethod
    def _generate_windows(
        height: int,
        width: int,
        config: ProcessingConfig,
        tile_size: int = None,
        stride: int = None,
    ) -> Generator[Window]:
        """Generate tile windows for processing.

        Args:
            height: Original height of the image.
            width: Original width of the image.
            config: Processing configuration.
            tile_size: Size of each tile (defaults to config.crop_size).
            stride: Size of each tile stride (defaults to config.stride).

        Yields:
            Window objects for each tile.
        """
        tile_size = tile_size or config.crop_size
        stride = stride or config.stride

        # Calculate number of tiles needed to ensure full coverage
        # Use ceiling division to handle cases where dimensions don't align perfectly with stride
        if height <= tile_size:
            tiles_y = 1
        else:
            tiles_y = math.ceil((height - tile_size) / stride) + 1

        if width <= tile_size:
            tiles_x = 1
        else:
            tiles_x = math.ceil((width - tile_size) / stride) + 1

        for y in range(tiles_y):
            for x in range(tiles_x):
                row_start = y * stride
                col_start = x * stride
                row_end = row_start + tile_size
                col_end = col_start + tile_size

                # Skip windows that would be entirely outside the image bounds
                if row_start >= height or col_start >= width:
                    continue

                yield Window.from_slices(
                    rows=(row_start, row_end),
                    cols=(col_start, col_end),
                )

    @staticmethod
    def _generate_windows_for_postprocessing(
        height: int,
        width: int,
        tile_size: int,
        stride: int,
    ) -> Generator[Window]:
        """Generate tile windows for post-processing, clipped to image bounds.

        Args:
            height: Original height of the image.
            width: Original width of the image.
            tile_size: Size of each tile (defaults to config.crop_size).
            stride: Size of each tile stride (defaults to config.stride).

        Yields:
            Window objects for post-processing tiles.
        """
        # Calculate number of tiles needed to ensure full coverage
        if height <= tile_size:
            tiles_y = 1
        else:
            tiles_y = math.ceil((height - tile_size) / stride) + 1

        if width <= tile_size:
            tiles_x = 1
        else:
            tiles_x = math.ceil((width - tile_size) / stride) + 1

        for y in range(tiles_y):
            for x in range(tiles_x):
                row_start = y * stride
                col_start = x * stride
                # For post-processing, clip to actual image bounds
                row_end = min(row_start + tile_size, height)
                col_end = min(col_start + tile_size, width)

                # Skip windows that would be entirely outside the image bounds
                if row_start >= height or col_start >= width:
                    continue

                # Ensure we have a valid window size
                if row_end <= row_start or col_end <= col_start:
                    continue

                yield Window.from_slices(
                    rows=(row_start, row_end),
                    cols=(col_start, col_end),
                )

    @staticmethod
    def _place_window_result(
        dst: rasterio.io.BufferedDatasetWriter,
        window: Window,
        tile_result: np.ndarray,
        overlap: int,
    ) -> None:
        """Place tile result into the full result array using overlap strategy.

        Args:
            dst: Destination rasterio dataset writer.
            window: Window object defining the region to write.
            tile_result: Result array from the model for the tile.
            overlap: Overlap size to handle edge cases.
        """
        # Calculate the region to copy (excluding overlap except at image boundaries)
        copy_row_start = window.row_off
        copy_col_start = window.col_off
        copy_row_end = window.row_off + window.height
        copy_col_end = window.col_off + window.width

        # Exclude overlap regions except at image boundaries
        if window.row_off > 0:  # Not top edge
            copy_row_start += overlap
        if window.col_off > 0:  # Not left edge
            copy_col_start += overlap
        if window.row_off + window.height < dst.height:  # Not bottom edge
            copy_row_end -= overlap
        if window.col_off + window.width < dst.width:  # Not right edge
            copy_col_end -= overlap

        # Calculate corresponding region in tile result
        tile_row_start = copy_row_start - window.row_off
        tile_col_start = copy_col_start - window.col_off
        tile_row_end = tile_row_start + (copy_row_end - copy_row_start)
        tile_col_end = tile_col_start + (copy_col_end - copy_col_start)

        result = tile_result[tile_row_start:tile_row_end, tile_col_start:tile_col_end]
        write_window = Window(
            col_off=copy_col_start,
            row_off=copy_row_start,
            width=copy_col_end - copy_col_start,
            height=copy_row_end - copy_row_start,
        )

        dst.write(result, 1, window=write_window)

    def _apply_final_postprocessing(
        self,
        dst_path: str,
        config: ProcessingConfig,
    ) -> None:
        """Apply final post-processing using tiled approach for large rasters.

        Args:
            dst_path: Destination rasterio dataset writer.
            config: ProcessingConfig object.
        """
        if not (config.apply_median_blur or config.apply_morphological_ops):
            return  # No processing needed

        # Calculate required overlap for operations
        blur_overlap = (config.blur_kernel_size - 1) // 2 if config.apply_median_blur else 0
        morph_overlap = (config.morph_kernel_size - 1) // 2 if config.apply_morphological_ops else 0
        overlap = max(blur_overlap, morph_overlap)

        if overlap == 0:
            return

        # Process in tiles with overlap
        with rasterio.open(dst_path, "r+") as dst:
            height, width = dst.height, dst.width

            # Use smaller tiles for post-processing to manage memory
            tile_size = min(512, config.crop_size)
            # Calculate stride to create overlapping tiles
            stride = tile_size - 2 * overlap

            # Generate overlapping windows for post-processing
            windows = self._generate_windows_for_postprocessing(
                height,
                width,
                tile_size,
                stride,
            )

            windows_list = list(windows)
            if windows_list:  # Only show progress if there are windows to process
                with Progress(
                    TextColumn("[bold green]Post-processing"),
                    BarColumn(),
                    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                    TimeElapsedColumn(),
                    console=console,
                ) as progress:
                    task = progress.add_task("Post-processing", total=len(windows_list))
                    for window in windows_list:
                        # Read tile with overlap
                        tile_data = dst.read(1, window=window)

                        # Apply median blur (key for quality improvement)
                        if config.apply_median_blur:
                            blur_size = config.blur_kernel_size
                            if blur_size % 2 == 0:
                                blur_size += 1  # Ensure odd size
                            tile_data = cv2.medianBlur(tile_data, blur_size)

                        # Apply morphological operations if enabled
                        if config.morph_kernel_size > 0:
                            kernel_size = config.morph_kernel_size
                            kernel = np.ones((kernel_size, kernel_size), np.uint8)

                            # Opening (remove noise)
                            tile_data = cv2.morphologyEx(
                                tile_data,
                                cv2.MORPH_OPEN,
                                kernel,
                            )
                            # Closing (fill gaps)
                            tile_data = cv2.morphologyEx(
                                tile_data,
                                cv2.MORPH_CLOSE,
                                kernel,
                            )

                        # Place result, removing overlap except at boundaries
                        self._place_window_result(dst, window, tile_data, overlap)
                        progress.update(task, advance=1, refresh=True)
