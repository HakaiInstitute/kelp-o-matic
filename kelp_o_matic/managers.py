import warnings
from pathlib import Path
from typing import Union

import rasterio
import torch
from rich import print
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn

from kelp_o_matic.geotiff_io import GeotiffReader, GeotiffWriter
from kelp_o_matic.hann import TorchMemoryRegister, BartlettHannKernel
from kelp_o_matic.models import _Model
from kelp_o_matic.utils import all_same


class GeotiffSegmentationManager:
    """Class for configuring data io and efficient segmentation of Geotiff imagery."""

    def __init__(
        self,
        model: "_Model",
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        crop_size: int = 1024,
    ):
        """Create the segmentation object.

        Args:
            model: A callable module that accepts a batch of torch.Tensor data and
                returns classifications.
            input_path: The path to the input geotiff image.
            output_path: The destination file path for the output segmentation data.
            crop_size: The size of image crop to classify iteratively until the entire
                image is classified.
        """
        self.model = model
        self.crop_size = crop_size
        self.input_path = str(Path(input_path).expanduser().resolve())
        self.output_path = str(Path(output_path).expanduser().resolve())

        self.reader = GeotiffReader(
            self.input_path,
            crop_size=crop_size,
            stride=crop_size // 2,
        )
        self.writer = GeotiffWriter.from_reader(
            self.output_path,
            self.reader,
            count=1,
            dtype="uint8",
            nodata=0,
        )
        self.kernel = BartlettHannKernel(crop_size, self.model.device)
        self.register = TorchMemoryRegister(
            self.input_path, self.model.register_depth, crop_size, self.model.device
        )

    def __call__(self):
        """Run the segmentation task."""
        self.on_start()
        self._run_checks()

        with rasterio.Env():
            for index, batch in enumerate(self.reader):
                crop, read_window = batch

                if self.model.transform:
                    crop = self.model.transform(crop)

                if torch.all(crop == 0):
                    logits = self.model.shortcut(self.reader.crop_size)
                else:
                    # Zero pad to correct shape
                    _, h, w = crop.shape
                    crop = torch.nn.functional.pad(
                        crop, (0, self.crop_size - w, 0, self.crop_size - h), value=0
                    )
                    logits = self.model(crop.unsqueeze(0))[0]

                logits = self.kernel(
                    logits,
                    top=self.reader.is_top_window(read_window),
                    bottom=self.reader.is_bottom_window(read_window),
                    left=self.reader.is_left_window(read_window),
                    right=self.reader.is_right_window(read_window),
                )
                write_logits, write_window = self.register.step(logits, read_window)
                labels = self.model.post_process(write_logits)

                # Write outputs
                self.writer.write_window(labels, write_window)
                self.on_tile_write(index)
        self.on_end()

    def _no_data_check(self):
        if self.reader.nodata is None:
            warnings.warn(
                "Define a nodata value on the input raster to speed up processing.",
                UserWarning,
            )

    def _byte_type_check(self):
        dtype = self.reader.profile["dtype"]
        if dtype != "uint8":
            raise AssertionError(
                f"Input image has incorrect data type {dtype}. "
                f"Only uint8 (aka Byte) images are supported."
            )

    def _band_count_check(self):
        if self.reader.count < 3:
            raise AssertionError(
                "Input image has less than 3 bands. "
                "The image should have at least 3 bands, with the first three in RGB "
                "order."
            )

    def _block_tiles_check(self):
        if not all_same(self.reader.block_shapes):
            warnings.warn("Input image bands have different sized blocks.", UserWarning)

        crop_shape = self.reader.crop_size
        y_shape, x_shape = self.reader.block_shapes[0]
        if y_shape == 1:
            warnings.warn(
                "The input image is not a tiled tif. Processing will be "
                "significantly faster for tiled images.",
                UserWarning,
            )
        elif crop_shape % y_shape != 0 or crop_shape % x_shape != 0:
            warnings.warn(
                "Suboptimal crop_size and padding were specified. Performance "
                "will be degraded. The detected block shape for this band is "
                "({y_shape}, {x_shape}). Faster performance may be achieved by setting "
                "the crop_size and the padding such that (crop_size + 2*padding) is a "
                "multiple of {y_shape}.",
                UserWarning,
            )

    def _run_checks(self):
        """Run image checks."""
        self._no_data_check()
        self._byte_type_check()
        self._band_count_check()
        self._block_tiles_check()

    def on_start(self):
        """Hook that runs before image processing."""
        pass

    def on_end(self):
        """Hook that runs after image processing."""
        pass

    def on_tile_write(self, batch_idx: int):
        """
        Hook that runs for each batch of data, immediately after classification.

        Args:
            batch_idx: The batch index being processed.
        """
        pass


class RichSegmentationManager(GeotiffSegmentationManager):
    """Run the segmentation with Rich progress bars and logging."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.progress = Progress(
            SpinnerColumn("earth"), *Progress.get_default_columns(), TimeElapsedColumn()
        )
        self.processing_task = self.progress.add_task(
            description="Processing", total=len(self.reader)
        )

    def __call__(self):
        with self.progress:
            super().__call__()

    def on_start(self):
        device_emoji = ":rocket:" if self.model.device.type == "cuda" else ":snail:"
        print(f"Running with [magenta]{self.model.device} {device_emoji}")

    def on_tile_write(self, index: int):
        self.progress.update(self.processing_task, completed=index)

    def on_end(self):
        self.progress.update(self.processing_task, completed=len(self.reader))
        print("[bold italic green]:tada: Segmentation complete! :tada:[/]")
