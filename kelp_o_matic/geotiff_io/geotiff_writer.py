"""
Created by: Taylor Denouden
Organization: Hakai Institute
Date: 2021-02-22
Description: A Pytorch Dataset for geotiff images that dynamically crops the image.
"""
from pathlib import Path
from typing import Union

import numpy as np
import rasterio
from rasterio.windows import Window

from kelp_o_matic.geotiff_io import GeotiffReader


class GeotiffWriter:
    def __init__(
        self, img_path: Union[str, "Path"], profile: dict, crop_size: int, **kwargs
    ):
        """Write a tif file in small sections.

        Args:
            img_path: The path to save the output file to.
            profile: Profile to pass to rasterio with crs and geo-transform information.
            crop_size: The size of each section being written.
            **kwargs: All other kwargs are passed to the geotiff rasterio profile.
        """
        super().__init__()
        self.img_path = img_path
        self.crop_size = crop_size

        profile = profile.copy()
        profile.update(blockxsize=crop_size, blockysize=crop_size, tiled=True, **kwargs)

        # Create the file and get the indices of write locations
        with rasterio.open(self.img_path, "w", **profile) as dst:
            self.height = dst.height
            self.width = dst.width
            self.profile = dst.profile

    @classmethod
    def from_reader(
        cls, img_path: Union[str, "Path"], reader: "GeotiffReader", **kwargs
    ):
        """Create a CropDatasetWriter using a CropDatasetReader instance.
            Defines the geo-referencing, cropping, and size parameters using an
            existing raster image.

        Args:
            img_path: Path to the file you want to create.
            reader: An instance of a CropDatasetReader from which to copy
                geo-referencing parameters.
            **kwargs: All other kwargs are passed to the geotiff rasterio profile.

        Returns:
            CropDatasetWriter
        """
        return cls(
            img_path, profile=reader.profile, crop_size=reader.crop_size, **kwargs
        )

    def write_window(self, write_data: np.ndarray, window: Window):
        # Remove data that goes past the boundaries
        write_data = write_data[: window.height, : window.width].astype(
            self.profile["dtype"]
        )

        # Write the data
        with rasterio.open(self.img_path, "r+") as dst:
            dst.write(write_data, 1, window=window)
