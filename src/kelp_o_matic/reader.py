"""Abstract image reader interface and implementations for multiple file formats."""

from __future__ import annotations

import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

import rasterio
from loguru import logger

if TYPE_CHECKING:
    import numpy as np
    from rasterio.windows import Window


class ImageReader(ABC):
    """Abstract base class for reading image data in tiles."""

    @property
    @abstractmethod
    def height(self) -> int:
        """Height of the image in pixels."""
        pass

    @property
    @abstractmethod
    def width(self) -> int:
        """Width of the image in pixels."""
        pass

    @property
    @abstractmethod
    def num_bands(self) -> int:
        """Number of bands in the image."""
        pass

    @property
    @abstractmethod
    def dtype(self) -> str:
        """Data type of the image (e.g., 'uint8', 'uint16')."""
        pass

    @property
    def crs(self) -> object:
        """Coordinate Reference System of the image.

        Returns:
            CRS object or None for non-georeferenced data.
        """
        return None

    @property
    def transform(self) -> object:
        """Geospatial affine transform.

        Returns:
            Affine transform object or None for non-georeferenced data.
        """
        return None

    @abstractmethod
    def read_window(
        self,
        window: Window,
        band_order: list[int] | None = None,
        boundless: bool = True,
        fill_value: int = 0,
    ) -> np.ndarray:
        """Read a rectangular window of data from the image.

        Args:
            window: Rasterio Window object specifying the region to read
            band_order: List of band indices (1-based) to read. If None, reads all bands in order
            boundless: If True, allows reading outside image bounds (padded with fill_value)
            fill_value: Value used for out-of-bounds pixels when boundless=True

        Returns:
            Numpy array of shape [bands, height, width] containing the image data
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the reader and release resources."""
        pass

    def __enter__(self) -> ImageReader:
        """Context manager entry.

        Returns:
            Self for use in with statement.
        """
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> None:
        """Context manager exit.

        Args:
            exc_type: Exception type if raised in context.
            exc_val: Exception value if raised in context.
            exc_tb: Exception traceback if raised in context.
        """
        self.close()


class TIFFReader(ImageReader):
    """Reader for GeoTIFF and standard TIFF files using Rasterio."""

    def __init__(
        self,
        file_path: str | Path,
        **kwargs: object,
    ) -> None:
        """Initialize TIFFReader.

        Args:
            file_path: Path to the TIFF file.
            **kwargs: Additional keyword arguments (ignored for compatibility).

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"TIFF file not found: {self.file_path}")

        self._src = rasterio.open(self.file_path)

    @property
    def height(self) -> int:
        """Height of the raster in pixels."""
        return self._src.height

    @property
    def width(self) -> int:
        """Width of the raster in pixels."""
        return self._src.width

    @property
    def num_bands(self) -> int:
        """Number of bands in the raster."""
        return self._src.count

    @property
    def dtype(self) -> str:
        """Data type of the raster."""
        return self._src.dtypes[0]

    @property
    def crs(self) -> object:
        """Coordinate Reference System of the raster.

        Returns:
            CRS object from rasterio dataset.
        """
        return self._src.crs

    @property
    def transform(self) -> object:
        """Geospatial affine transform of the raster.

        Returns:
            Affine transform object from rasterio dataset.
        """
        return self._src.transform

    @property
    def profile(self) -> dict[str, object]:
        """Full rasterio profile for the dataset."""
        return self._src.profile

    def read_window(
        self,
        window: Window,
        band_order: list[int] | None = None,
        boundless: bool = True,
        fill_value: int = 0,
    ) -> np.ndarray:
        """Read a window of data from the TIFF file.

        Args:
            window: Rasterio Window object specifying the region to read.
            band_order: List of band indices (1-based) to read. If None, reads all bands.
            boundless: If True, allows reading outside image bounds.
            fill_value: Value used for out-of-bounds pixels.

        Returns:
            Numpy array of shape [bands, height, width].
        """
        if band_order is None:
            # Read all bands
            data = self._src.read(window=window, boundless=boundless, fill_value=fill_value)
        else:
            # Validate band indices
            if any(b < 1 or b > self.num_bands for b in band_order):
                logger.error(
                    f"Band order {band_order} is invalid for image with {self.num_bands} bands.\n "
                    "Please specify band indices between 1 and the number of bands in the image (GDAL indexing)."
                )
                sys.exit(1)

            # Read selected bands in the specified order
            data = self._src.read(indexes=band_order, window=window, boundless=boundless, fill_value=fill_value)

        return data

    def close(self) -> None:
        """Close the rasterio dataset."""
        if self._src is not None:
            self._src.close()
