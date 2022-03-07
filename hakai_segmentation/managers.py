import warnings
from pathlib import Path
from typing import Union

import numpy as np
import torch
from torch.utils.data import DataLoader
from torchvision import transforms
from tqdm.auto import tqdm

from hakai_segmentation.geotiff_io import GeotiffReader, GeotiffWriter
from hakai_segmentation.models import _Model


class GeotiffSegmentation:
    """Class for configuring data io and efficient segmentation of Geotiff imagery."""

    def __init__(self, model: '_Model', input_path: Union[str, 'Path'], output_path: Union[str, 'Path'], crop_size: int = 256,
                 padding: int = 128, batch_size: int = 2):
        """
        Create the segmentation object.

        :param model: A callable module that accepts a batch of torch.Tensor data and returns classifications.
        :param input_path: The path to the input geotiff image.
        :param output_path: The destination file path for the output segmentation data.
        :param crop_size: The size of image crop to classify iteratively until the entire image is classified.
        :param padding: The number of context pixels to add to each side of an image crop to improve outputs.
        :param batch_size: The number of crops to classify at a time using the model.
        """
        self.model = model

        tran = transforms.Compose([
            transforms.ToTensor(),
            transforms.Lambda(lambda img: img[:3, :, :]),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
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

        self.writer = GeotiffWriter.from_reader(Path(output_path).expanduser().resolve(),
                                                self.reader, count=1, dtype="uint8", nodata=0)

        self.progress = None

    @staticmethod
    def _should_keep(img: 'np.ndarray') -> bool:
        """
        Determines if an image crop should be classified or discarded.

        :param img: The image crop, with padding removed.
        :return: Flag to indicate if crop should be discarded.
        """
        _img = np.clip(img, 0, 255)
        is_blank = np.all((_img == 0) | (_img == 255))
        return not is_blank

    def __call__(self):
        """Run the segmentation task."""
        self.on_start()

        for batch_idx, batch in enumerate(self._dataloader):
            self.on_batch_start(batch_idx)

            crops, indices = batch
            predictions = self.model(crops)
            labels = torch.argmax(predictions, dim=1).detach().cpu().numpy()

            # Write outputs
            for label, idx in zip(labels, indices):
                self.writer.write_index(label, int(idx))
                self.on_chip_write_end(int(idx))

            self.on_batch_end(batch_idx)
        self.on_end()

    def on_start(self):
        """Hook that runs before image processing. By default, sets up a tqdm progress bar."""
        # Check data type assumptions
        if self.reader.nodata is None:
            warnings.warn("Define the correct nodata value on the input raster to speed up processing.", UserWarning)

        dtype = self.reader.profile['dtype']
        if dtype != 'uint8':
            raise AssertionError(f"Input image has incorrect data type {dtype}. Only uint8 (aka Byte) images are supported.")
        if self.reader.count < 3:
            raise AssertionError("Input image has less than 3 bands. "
                                 "The image should have at least 3 bands, with the first three being in RGB order.")

        # Setup progress bar
        self.progress = tqdm(
            colour="CYAN",
            total=len(self.reader),
            desc="Processing"
        )

    def on_end(self):
        """Hook that runs after image processing. By default, tears down the tqdm progress bar."""
        self.progress.update(len(self.reader) - self.progress.n)
        self.progress.close()
        self.progress = None

    def on_batch_start(self, batch_idx: int):
        """
        Hook that runs for each batch of data, immediately before classification by the model.

        :param batch_idx: The batch index being processed.
        """
        pass

    def on_batch_end(self, batch_idx: int):
        """
        Hook that runs for each batch of data, immediately after classification by the model.

        :param batch_idx: The batch index being processed.
        """
        pass

    def on_chip_write_end(self, index: int):
        """
        Hook that runs for each crop of data, immediately after classification by the model.
        By default, increments a tqdm progress bar.

        :param index: The index of the image crop that was processed.
        """
        self.progress.update(index + 1 - self.progress.n)
