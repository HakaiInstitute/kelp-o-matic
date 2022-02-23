import warnings
from pathlib import Path
from typing import Union

import fire
import numpy as np
import torch
from torch.utils.data import DataLoader
from torchvision import transforms
from tqdm.auto import tqdm

from hakai_segmentation.geotiff_io import GeotiffReader, GeotiffWriter
from hakai_segmentation.models import KelpPresenceSegmentationModel, \
    MusselPresenceSegmentationModel, _Model


class GeotiffSegmentation:
    def __init__(self, model: '_Model', input_path: Union[str, 'Path'], output_path: Union[str, 'Path'], crop_size: int = 256,
                 padding: int = 128, batch_size: int = 2):
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
        _img = np.clip(img, 0, 255)
        is_blank = np.all((_img == 0) | (_img == 255))
        return not is_blank

    def __call__(self):
        self.on_start()

        for batch_idx, batch in enumerate(self._dataloader):
            self.on_batch_start(batch_idx)

            crops, indices = batch
            predictions = self.model(crops)
            for pred, idx in zip(predictions, indices):
                label = torch.argmax(pred, dim=0).detach().cpu().numpy()
                self.writer[int(idx)] = label
                self.on_chip_write_end(int(idx))

            self.on_batch_end(batch_idx)
        self.on_end()

    def on_start(self):
        # Check data type assumptions
        if self.reader.raster.nodata is None:
            warnings.warn("Define the correct nodata value on the input raster to speed up processing.", UserWarning)
        if (dtype := self.reader.raster.dtypes[0]) != 'uint8':
            raise AssertionError(f"Input image has incorrect data type {dtype}. Only uint8 (aka Byte) images are supported.")
        if self.reader.raster.count < 3:
            raise AssertionError("Input image has less than 3 bands. "
                                 "The image should have at least 3 bands, with the first three being in RGB order.")

        # Setup progress bar
        self.progress = tqdm(
            colour="CYAN",
            total=len(self.reader),
            desc="Processing"
        )

    def on_end(self):
        self.progress.close()
        self.progress = None

    def on_batch_start(self, batch_idx: int):
        pass

    def on_batch_end(self, batch_idx: int):
        pass

    def on_chip_write_end(self, index: int):
        self.progress.update(index + 1 - self.progress.n)


def find_mussels(source: str, dest: str,
                 crop_size: int = 256, padding: int = 128, batch_size: int = 2):
    """Detect mussels in source image and output the resulting classification raster to dest.

    :param source: Input image with Byte data type.
    :param dest: File path location to save output to.
    :param crop_size: The size of cropped image square run through the segmentation model.
    :param padding: The number of context pixels added to each side of the cropped image squares.
    :param batch_size: The batch size of cropped image sections to process together.
    """

    model = MusselPresenceSegmentationModel()
    GeotiffSegmentation(model, source, dest,
                        crop_size=crop_size, padding=padding, batch_size=batch_size)()


def find_kelp(source: str, dest: str,
              crop_size: int = 256, padding: int = 128, batch_size: int = 2):
    """Detect kelp in source image and output the resulting classification raster to dest.

    :param source: Input image with Byte data type.
    :param dest: File path location to save output to.
    :param crop_size: The size of cropped image square run through the segmentation model.
    :param padding: The number of context pixels added to each side of the cropped image squares.
    :param batch_size: The batch size of cropped image sections to process together.
    """
    model = KelpPresenceSegmentationModel()
    GeotiffSegmentation(model, source, dest,
                        crop_size=crop_size, padding=padding, batch_size=batch_size)()


def cli():
    fire.Fire({
        "find-mussels": find_mussels,
        "find-kelp": find_kelp
    })


if __name__ == '__main__':
    cli()
