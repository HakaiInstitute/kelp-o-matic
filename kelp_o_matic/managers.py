from pathlib import Path
from typing import Union

import numpy as np
import rasterio
from rich import print
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn
from torch.utils.data import DataLoader
from torchvision import transforms

from kelp_o_matic.geotiff_io import GeotiffReader, GeotiffWriter
from kelp_o_matic.models import _Model
from kelp_o_matic.utils import all_same


class GeotiffSegmentation:
    """Class for configuring data io and efficient segmentation of Geotiff imagery."""

    def __init__(
        self,
        model: "_Model",
        input_path: Union[str, "Path"],
        output_path: Union[str, "Path"],
        crop_size: int = 512,
        padding: int = 256,
        batch_size: int = 1,
    ):
        """Create the segmentation object.

        Args:
            model: A callable module that accepts a batch of torch.Tensor data and
                returns classifications.
            input_path: The path to the input geotiff image.
            output_path: The destination file path for the output segmentation data.
            crop_size: The size of image crop to classify iteratively until the entire
                image is classified.
            padding: The number of context pixels to add to each side of an image crop
                to improve outputs.
            batch_size: The number of crops to classify at a time using the model.
        """
        self.model = model

        tran = transforms.Compose(
            [
                transforms.ToTensor(),
                transforms.Lambda(lambda img: img[:3, :, :]),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        )
        self.reader = GeotiffReader(
            Path(input_path).expanduser().resolve(),
            transform=tran,
            crop_size=crop_size,
            padding=padding,
            filter_=self._should_keep,
        )
        self._dataloader = DataLoader(
            self.reader,
            shuffle=False,
            batch_size=batch_size,
            pin_memory=True,
            num_workers=0,
        )

        self.writer = GeotiffWriter.from_reader(
            Path(output_path).expanduser().resolve(),
            self.reader,
            count=1,
            dtype="uint8",
            nodata=0,
        )

        self.progress = Progress(
            SpinnerColumn(), *Progress.get_default_columns(), TimeElapsedColumn()
        )
        self.processing_task = self.progress.add_task(
            description="Processing", total=len(self.reader)
        )

    @staticmethod
    def _should_keep(img: "np.ndarray") -> bool:
        """Determines if an image crop should be classified or discarded.

        Args:
            img: The image crop, with padding removed.

        Returns:
             Flag to indicate if crop should be discarded.
        """
        _img = np.clip(img, 0, 255)
        return bool(np.any(_img % 255))

    def __call__(self):
        """Run the segmentation task."""
        with self.progress:
            self.on_start()

            with rasterio.Env():
                for batch_idx, batch in enumerate(self._dataloader):
                    self.on_batch_start(batch_idx)

                    crops, indices = batch
                    labels = self.model(crops).detach().cpu().numpy()

                    # Write outputs
                    for label, idx in zip(labels, indices):
                        self.writer.write_index(label, int(idx))
                        self.on_chip_write_end(int(idx))

                    del crops, indices, labels, batch

                    self.on_batch_end(batch_idx)
            self.on_end()

    def _no_data_check(self):
        if self.reader.nodata is None:
            print(
                "[italic yellow]:warning: Define a nodata value on the input raster to "
                "speed up processing.[/]"
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
            print(
                "[bold italic red]:skull: Input image bands have different sized "
                "blocks."
            )

        crop_shape = self.reader.crop_size + 2 * self.reader.padding
        y_shape, x_shape = self.reader.block_shapes[0]
        if y_shape == 1:
            print(
                "[bold italic red]:skull: The input image is not a tiled tif. "
                "Processing will be significantly faster for tiled images.[/]"
            )
        elif crop_shape % y_shape != 0 or crop_shape % x_shape != 0:
            print(
                "[italic yellow]:warning: Suboptimal crop_size and padding were "
                "specified. Performance will be degraded. The detected block shape for "
                "this band is [bold cyan]({y_shape}, {x_shape})[/bold cyan]. Faster "
                "performance may be achieved by setting the crop_size and the padding "
                "such that [green](crop_size + 2*padding)[/green] is a multiple of "
                "[cyan]{y_shape}[/cyan].[/]"
            )

    def on_start(self):
        """Hook that runs before image processing.

        By default, runs image checks and sets up a tqdm progress bar.
        """
        self._no_data_check()
        self._byte_type_check()
        self._band_count_check()
        self._block_tiles_check()

    def on_end(self):
        """
        Hook that runs after image processing.
        """
        self.progress.update(self.processing_task, completed=len(self.reader))
        print("[bold italic green]:tada: Segmentation complete! :tada:[/]")

    def on_batch_start(self, batch_idx: int):
        """
        Hook that runs for each batch of data, immediately before classification.

        Args:
            batch_idx: The batch index being processed.
        """
        pass

    def on_batch_end(self, batch_idx: int):
        """
        Hook that runs for each batch of data, immediately after classification.

        Args:
            batch_idx: The batch index being processed.
        """
        pass

    def on_chip_write_end(self, index: int):
        """
        Hook that runs for each crop of data, immediately after classification.
        By default, increments a tqdm progress bar.

        Args:
            index: The index of the image crop that was processed.
        """
        self.progress.update(self.processing_task, completed=index)
