"""
Created by: Taylor Denouden
Organization: Hakai Institute
Date: 2021-02-22
Description: A Pytorch Dataset for geotiff images that dynamically crops the image.
"""

import itertools
from pathlib import Path
from typing import Union

import numpy as np
import rasterio

from hakai_segmentation.geotiff_io import GeotiffReader


class GeotiffWriter:
    def __init__(self, img_path: Union[str, 'Path'], profile: dict, crop_size: int, padding: int = 0, **kwargs):
        """Write a tif file in small sections.

        Args:
            img_path: The path to save the output file to.
            profile: Profile to pass to rasterio with crs and geo-transform information.
            crop_size: The size of each section being written.
            padding: Padding data to remove from each write data section.
            **kwargs: All other kwargs are passed to the geotiff profile, to override params.
        """
        super().__init__()
        self.img_path = img_path
        self.crop_size = crop_size
        self.padding = padding

        profile.update(blockxsize=crop_size, blockysize=crop_size, tiled=True, **kwargs)

        # Create the file and get the indices of the write locations
        self.raster = rasterio.open(self.img_path, 'w', **profile)
        self.height = self.raster.height
        self.width = self.raster.width
        self.profile = self.raster.profile

        _y0s = range(0, self.height, self.crop_size)
        _x0s = range(0, self.width, self.crop_size)
        self.y0x0 = list(itertools.product(_y0s, _x0s))

    @classmethod
    def from_reader(cls, img_path: Union[str, 'Path'], reader: 'GeotiffReader', **kwargs):
        """Create a CropDatasetWriter using a CropDatasetReader instance.
            Defines the geo-referencing, cropping, and size parameters using an existing raster image.

        Args:
            img_path: Path to the file you want to create.
            reader: An instance of a CropDatasetReader from which to copy geo-referencing parameters.
            **kwargs: All other kwargs are passed to the geotiff profile, to override params.

        Returns:
            CropDatasetWriter
        """
        self = cls(img_path, profile=reader.profile, crop_size=reader.crop_size,
                   padding=reader.padding, **kwargs)
        self.y0x0 = reader.y0x0
        return self

    def write_index(self, write_data: np.ndarray, idx: int):
        y0, x0 = self.y0x0[idx]

        # Read the image section
        window = ((y0, min(y0 + self.crop_size, self.height)),
                  (x0, min(x0 + self.crop_size, self.width)))

        # Remove padding information
        write_data = write_data[self.padding:-self.padding, self.padding:-self.padding]

        # Remove data that goes past the boundaries
        dh = window[0][1] - window[0][0]
        dw = window[1][1] - window[1][0]

        # Write the data
        write_data = write_data[:dh, :dw].astype(self.profile['dtype'])
        self.raster.write(write_data, 1, window=window)

    def __del__(self):
        self.raster.close()
