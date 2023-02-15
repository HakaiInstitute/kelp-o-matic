import warnings
from pathlib import Path
from typing import Union, Optional

import numpy as np
import rasterio
import torch
from torch.utils.data import DataLoader
from torchvision import transforms
from tqdm.auto import tqdm

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
        crop_size: Optional[int] = None,
        padding: int = 256,
        batch_size: int = 1,
    ):
        """Create the segmentation object.

        Args:
            model: A callable module that accepts a batch of torch.Tensor data and returns classifications.
            input_path: The path to the input geotiff image.
            output_path: The destination file path for the output segmentation data.
            crop_size: The size of image crop to classify iteratively until the entire image is classified.
                If `None`, uses the largest crop size possible.
            padding: The number of context pixels to add to each side of an image crop to improve outputs.
            batch_size: The number of crops to classify at a time using the model.
        """
        self.model = model
        self.input_path = Path(input_path).expanduser().resolve()
        self.output_path = Path(output_path).expanduser().resolve()
        self.padding = padding
        self.batch_size = batch_size
        self.crop_size = (
            crop_size if crop_size is not None else self._find_max_crop_size()
        )

        self.tran = transforms.Compose(
            [
                transforms.ToTensor(),
                transforms.Lambda(lambda img: img[:3, :, :]),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        )
        self.reader = GeotiffReader(
            self.input_path,
            transform=self.tran,
            crop_size=self.crop_size,
            padding=self.padding,
            filter_=self._should_keep,
        )
        self._dataloader = DataLoader(
            self.reader,
            shuffle=False,
            batch_size=self.batch_size,
            pin_memory=True,
            num_workers=0,
        )

        self.writer = GeotiffWriter.from_reader(
            self.output_path,
            self.reader,
            count=1,
            dtype="uint8",
            nodata=0,
        )

        self.progress = None

    @staticmethod
    def _should_keep(img: "np.ndarray") -> bool:
        """Determines if an image crop should be classified or discarded.

        Args:
            img: The image crop, with padding removed.

        Returns:
             Flag to indicate if crop should be discarded.
        """
        _img = np.clip(img, 0, 255)
        return np.any(_img % 255)

    def __call__(self):
        """Run the segmentation task."""
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
            warnings.warn(
                "Define the correct nodata value on the input raster to speed up processing.",
                UserWarning,
            )

    def _byte_type_check(self):
        dtype = self.reader.profile["dtype"]
        if dtype != "uint8":
            raise AssertionError(
                f"Input image has incorrect data type {dtype}. Only uint8 (aka Byte) images are supported."
            )

    def _band_count_check(self):
        if self.reader.count < 3:
            raise AssertionError(
                "Input image has less than 3 bands. "
                "The image should have at least 3 bands, with the first three being in RGB order."
            )

    def _block_tiles_check(self):
        if not all_same(self.reader.block_shapes):
            warnings.warn(
                "Input image bands have different sized blocks.",
                UserWarning,
            )

        crop_shape = self.reader.crop_size + 2 * self.reader.padding
        y_shape, x_shape = self.reader.block_shapes[0]
        if y_shape == 1:
            warnings.warn(
                f"The input image is not a tiled tif. Processing will be significantly faster for tiled images.",
                UserWarning,
            )
        elif crop_shape % y_shape != 0 or crop_shape % x_shape != 0:
            warnings.warn(
                "Suboptimal crop_size and padding were specified. Performance will be degraded. "
                f"The detected block shape for this band is ({y_shape}, {x_shape}). "
                f"Faster performance may be achieved by setting the crop_size and the padding such"
                f"that (crop_size + 2*padding) is a multiple of {y_shape}.",
                UserWarning,
            )

    def _find_max_crop_size(self) -> int:
        channels = 3
        crop_size = 12800  # Max tested crop size

        while crop_size > 1:
            effective_crop_size = crop_size + 2 * self.padding
            crop = torch.zeros(
                (self.batch_size, channels, effective_crop_size, effective_crop_size),
                device=self.model.device,
            )
            try:
                # If this succeeds then crop_size is found
                self.model(crop)
                break
            except RuntimeError as err:
                msg = str(err)
                if "out of memory" in msg or "could not create a primitive" in msg:
                    # Not enough memory
                    crop_size //= 2
                else:
                    # Some other issue so re-raise error
                    raise err
            finally:
                del crop

        return crop_size

    def on_start(self):
        """Hook that runs before image processing.

        By default, runs image checks and sets up a tqdm progress bar.
        """
        self._no_data_check()
        self._byte_type_check()
        self._band_count_check()
        self._block_tiles_check()

        # Setup progress bar
        self.progress = tqdm(total=len(self.reader), desc="Processing")

    def on_end(self):
        """Hook that runs after image processing. By default, tears down the tqdm progress bar."""
        self.progress.update(len(self.reader) - self.progress.n)
        self.progress.close()
        self.progress = None

    def on_batch_start(self, batch_idx: int):
        """
        Hook that runs for each batch of data, immediately before classification by the model.

        Args:
            batch_idx: The batch index being processed.
        """
        pass

    def on_batch_end(self, batch_idx: int):
        """
        Hook that runs for each batch of data, immediately after classification by the model.

        Args:
            batch_idx: The batch index being processed.
        """
        pass

    def on_chip_write_end(self, index: int):
        """
        Hook that runs for each crop of data, immediately after classification by the model.
        By default, increments a tqdm progress bar.

        Args:
            index: The index of the image crop that was processed.
        """
        self.progress.update(index + 1 - self.progress.n)
