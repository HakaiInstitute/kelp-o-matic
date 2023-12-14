import warnings
from pathlib import Path
from typing import Union, Optional

import rasterio

from kelp_o_matic.managers import RichSegmentationManager
from kelp_o_matic.models import (
    KelpRGBPresenceSegmentationModel,
    KelpRGBSpeciesSegmentationModel,
    MusselRGBPresenceSegmentationModel,
    KelpRGBIPresenceSegmentationModel,
)


def _validate_paths(source: Path, dest: Path):
    drivers = rasterio.drivers.raster_driver_extensions()

    def is_supported_file_type(p: Path):
        try:
            drivers.get(p.suffix[1:])
            return True
        except KeyError:
            return False

    def file_exists(p: Path):
        return p.exists() and p.is_file()

    def dir_exists(p: Path):
        return p.exists() and p.is_dir()

    # Check that input and output paths are tif files
    # Check that input path exists
    if not file_exists(source):
        raise ValueError("The source file does not exist.")
    # Check that output path parent exists
    if not dir_exists(dest.parent):
        raise ValueError("The directory for path dest does not exist.")
    if not is_supported_file_type(source):
        raise ValueError("The specified source file is not supported by GDAL.")
    if not is_supported_file_type(dest):
        raise ValueError("The specified dest file is not supported by GDAL.")
    # Check that input and output paths are different
    if source == dest:
        raise ValueError(
            "The source and dest paths must be different. "
            "Please specify a different dest."
        )


def _validate_band_order(band_order: list[int], use_nir: bool = False):
    if use_nir:
        assert len(band_order) >= 4, "RGBI ordering requires 4 bands."
        if len(band_order) > 4:
            warnings.warn(
                f"RGBI models only uses the first 4 bands. Received {len(band_order)}."
            )
    else:
        assert len(band_order) >= 3, "RGB ordering requires 3 bands."
        if len(band_order) > 3:
            warnings.warn(
                f"RGB models only uses the first 3 bands. Received {len(band_order)}."
            )


def find_kelp(
    source: Union[str, Path],
    dest: Union[str, Path],
    species: bool = False,
    crop_size: int = 1024,
    use_nir: bool = False,
    band_order: Optional[list[int]] = None,
    use_gpu: bool = True,
):
    """
    Detect kelp in image at path `source` and output the resulting classification raster
    to file at path `dest`.

    Args:
        source: Input image with Byte data type.
        dest: File path location to save output to.
        species: Do species classification instead of presence/absence.
        crop_size: The size of cropped image square run through the segmentation model.
        use_nir: Use NIR band for classification. Assumes RGBI ordering.
        band_order: GDAL-style band re-ordering. Defaults to RGB or RGBI order.
            e.g. to reorder a BGRI image at runtime, pass `[3,2,1,4]`.
        use_gpu: Disable Cuda GPU usage and run on CPU only.
    """
    if not band_order:
        band_order = [1, 2, 3]
        if use_nir:
            band_order.append(4)

    _validate_band_order(band_order, use_nir)
    _validate_paths(Path(source), Path(dest))
    use_nir = len(band_order) == 4

    if use_nir and species:
        raise NotImplementedError("RGBI species classification not yet available.")
    elif use_nir:
        model = KelpRGBIPresenceSegmentationModel(use_gpu=use_gpu)
    elif species:
        model = KelpRGBSpeciesSegmentationModel(use_gpu=use_gpu)
    else:
        model = KelpRGBPresenceSegmentationModel(use_gpu=use_gpu)
    RichSegmentationManager(
        model, Path(source), Path(dest), band_order=band_order, crop_size=crop_size
    )()


def find_mussels(
    source: Union[str, Path],
    dest: Union[str, Path],
    crop_size: int = 1024,
    band_order: Optional[list[int]] = None,
    use_gpu: bool = True,
):
    """
    Detect mussels in image at path `source` and output the resulting classification
    raster to file at path `dest`.

    Args:
        source: Input image with Byte data type.
        dest: File path location to save output to.
        crop_size: The size of cropped image square run through the segmentation model.
        band_order: GDAL-style band re-ordering flag. Defaults to RGB order.
            e.g. to reorder a BGR image at runtime, pass `[3,2,1]`.
        use_gpu: Disable Cuda GPU usage and run on CPU only.
    """
    if not band_order:
        band_order = [1, 2, 3]

    _validate_band_order(band_order)
    _validate_paths(Path(source), Path(dest))
    model = MusselRGBPresenceSegmentationModel(use_gpu=use_gpu)
    RichSegmentationManager(
        model, Path(source), Path(dest), band_order=band_order, crop_size=crop_size
    )()
