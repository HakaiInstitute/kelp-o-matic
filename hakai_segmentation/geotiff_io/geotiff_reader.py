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
            filter_: Optional function to filter a chip out from the iterator.
                Must have signature `(img: np.array) -> bool`
        """
        super().__init__()

        self.img_path = img_path
        self.crop_size = crop_size
        self.padding = padding

        with rasterio.open(img_path, 'r') as src:
            self.height = src.height
            self.width = src.width
            self.nodata = src.nodata if hasattr(src, 'nodata') else None
            self.count = src.count
            self.profile = src.profile

        if fill_value is not None:
            self.fill_value = fill_value
        elif self.nodata is not None:
            self.fill_value = self.nodata
        else:
            self.fill_value = 0

        self.transform = transform
        self.filter = filter_

        _y0s = range(0, self.height, self.crop_size)
        _x0s = range(0, self.width, self.crop_size)
        self.y0x0 = list(itertools.product(_y0s, _x0s))

        self.idx = 0

    def __len__(self) -> int:
        return len(self.y0x0)

    def _get_crop(self, idx: int) -> np.ndarray:
        y0, x0 = self.y0x0[idx]

        # Read the image section
        window = ((y0 - self.padding, y0 + self.crop_size + self.padding),
                  (x0 - self.padding, x0 + self.crop_size + self.padding))

        with rasterio.open(self.img_path, 'r') as src:
            crop = src.read(window=window, boundless=True, fill_value=self.fill_value)

        if len(crop.shape) == 3:
            crop = np.moveaxis(crop, 0, 2)  # (c, h, w) => (h, w, c)
            if crop.shape[2] == 1:
                crop = np.squeeze(crop, axis=2)  # (h, w, 1) => (h, w)

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
            crop = self._get_crop(self.idx)
            self.idx += 1
        else:
            raise StopIteration

        if self.filter is not None:
            # Get crops until one meets the filter criteria
            while True:
                if self.filter(crop[self.padding:self.crop_size + self.padding, self.padding:self.crop_size + self.padding]):
                    break
                elif self.idx < len(self):
                    crop = self._get_crop(self.idx)
                    self.idx += 1
                else:
                    raise StopIteration

        if self.transform:
            crop = self.transform(crop)

        return crop, self.idx - 1

    @property
    def y0(self) -> List[int]:
        return [a[0] for a in self.y0x0]

    @property
    def x0(self) -> List[int]:
        return [a[1] for a in self.y0x0]
