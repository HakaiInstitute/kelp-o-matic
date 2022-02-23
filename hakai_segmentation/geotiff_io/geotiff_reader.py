"""
Created by: Taylor Denouden
Organization: Hakai Institute
Date: 2021-02-22
Description: A Pytorch Dataset for geotiff images that dynamically crops the image.
"""

import itertools
from pathlib import Path
from typing import Callable, List, Optional, Tuple, Union

import numpy as np
import rasterio
from torch.utils.data import IterableDataset


class GeotiffReader(IterableDataset):
    def __init__(self, img_path: Union[str, 'Path'], crop_size: int, padding: Optional[int] = 0,
                 fill_value: Optional[Union[int, float]] = None, transform: Optional[Callable] = None,
                 filter_: Optional[Callable] = None):
        """A Pytorch dataset that returns cropped segments of a tif image file.

        Args:
            img_path: The path to the image file to make the dataset from.
            crop_size: The desired edge length for each cropped section. Returned images will be square.
            padding: The amount of padding to add around each crop section from the adjacent image areas.
                Defaults to 0.
            fill_value: The value to fill in border regions of nodata areas of the image.
                Defaults to image nodata value.
            transform: Optional Pytorch style data transform to apply to each cropped section.
            filter: Optional function to filter a chip out from the iteratlor.
                Must have signature `(img: np.array) -> bool`
        """
        super().__init__()

        self.img_path = img_path
        self.crop_size = crop_size
        self.padding = padding

        self.raster = rasterio.open(img_path, 'r')

        if fill_value is not None:
            self.fill_value = fill_value
        elif hasattr(self.raster, "nodata") and self.raster.nodata:
            self.fill_value = self.raster.nodata
        else:
            self.fill_value = 0

        self.transform = transform
        self.filter = filter_

        _y0s = range(0, self.raster.height, self.crop_size)
        _x0s = range(0, self.raster.width, self.crop_size)
        self.y0x0 = list(itertools.product(_y0s, _x0s))

        self.idx = 0

    def __len__(self) -> int:
        return len(self.y0x0)

    def _get_crop(self, idx: int) -> np.ndarray:
        y0, x0 = self.y0x0[idx]

        # Read the image section
        window = ((y0 - self.padding, y0 + self.crop_size + self.padding),
                  (x0 - self.padding, x0 + self.crop_size + self.padding))
        crop = self.raster.read(window=window, masked=True, boundless=True,
                                fill_value=self.fill_value)

        # Fill nodata values
        crop = crop.filled(self.fill_value)

        if len(crop.shape) == 3:
            crop = np.moveaxis(crop, 0, 2)  # (c, h, w) => (h, w, c)
            if crop.shape[2] == 1:
                crop = np.squeeze(crop, axis=2)  # (h, w, c) => (h, w)

        return crop

    def __getitem__(self, idx: int) -> np.ndarray:
        crop = self._get_crop(idx)

        if self.transform:
            crop = self.transform(crop)

        return crop

    def __iter__(self):
        self.idx = 0
        return self

    def __next__(self) -> Tuple[np.ndarray, int]:
        # Assumes single worker process
        if self.idx < len(self):

            if self.filter is not None:
                # Get crops until one meets the filter criteria
                while self.idx < len(self):
                    # and not self.filter(
                    crop = self._get_crop(self.idx)
                    self.idx += 1

                    unpadded = crop[self.padding:self.crop_size + self.padding, self.padding:self.crop_size + self.padding]
                    if self.filter is None or self.filter(unpadded):
                        break

            if self.transform:
                crop = self.transform(crop)

            return crop, self.idx - 1

        else:
            raise StopIteration

    @property
    def y0(self) -> List[int]:
        return [a[0] for a in self.y0x0]

    @property
    def x0(self) -> List[int]:
        return [a[1] for a in self.y0x0]

    def close(self):
        self.raster.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
