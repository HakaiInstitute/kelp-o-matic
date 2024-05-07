"""
Created by: Taylor Denouden
Organization: Hakai Institute
Date: 2021-02-22
Description: A Pytorch Dataset for geotiff images that dynamically crops the image.
"""

import itertools
from pathlib import Path
from typing import List, Optional, Union

import numpy as np
import rasterio
from rasterio.windows import Window
from torch.utils.data import IterableDataset


class GeotiffReader(IterableDataset):
    def __init__(
        self,
        img_path: Union[str, "Path"],
        crop_size: int,
        stride: Optional[int] = None,
    ):
        """A Pytorch dataset that returns cropped segments of a tif image file.

        Args:
            img_path: The path to the image file to make the dataset from.
            crop_size: The desired edge length for each cropped section.
                Returned images will be square.
            stride: The stride to use when cropping the image. Defaults to `crop_size`.
        """
        super().__init__()

        self.img_path = img_path
        self.crop_size = crop_size
        self.stride = stride if stride is not None else crop_size

        with rasterio.open(img_path, "r") as src:
            self.height = src.height
            self.width = src.width
            self.nodata = src.nodata if hasattr(src, "nodata") else None
            self.count = src.count
            self.profile = src.profile
            self.block_shapes = src.block_shapes

        self._y0s = list(range(0, self.height - self.stride + 1, self.stride))
        self._x0s = list(range(0, self.width - self.stride + 1, self.stride))
        self.y0x0 = list(itertools.product(self._y0s, self._x0s))

    def __len__(self) -> int:
        return len(self.y0x0)

    def get_window(self, idx: int) -> Window:
        y0, x0 = self.y0x0[idx]
        return Window.from_slices(
            (y0, min(y0 + self.crop_size, self.height)),
            (x0, min(x0 + self.crop_size, self.width)),
        )

    def is_top_window(self, window: Window):
        return window.row_off == 0

    def is_bottom_window(self, window: Window):
        return window.row_off + window.height >= self.height

    def is_left_window(self, window: Window):
        return window.col_off == 0

    def is_right_window(self, window: Window):
        return window.col_off + window.width >= self.width

    def __getitem__(self, idx: int) -> ("np.ndarray", Window):
        window = self.get_window(idx)

        with rasterio.open(self.img_path, "r") as src:
            crop = src.read(window=window)

        if len(crop.shape) == 3:
            crop = np.moveaxis(crop, 0, 2)  # (c, h, w) => (h, w, c)

        return crop, window

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    @property
    def y0(self) -> List[int]:
        return self._y0s

    @property
    def x0(self) -> List[int]:
        return self._x0s
