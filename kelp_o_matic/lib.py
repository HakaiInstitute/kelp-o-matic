from pathlib import Path
from typing import Union

from kelp_o_matic.managers import RichSegmentationManager
from kelp_o_matic.models import (
    KelpPresenceSegmentationModel,
    KelpSpeciesSegmentationModel,
    MusselPresenceSegmentationModel,
)


def _validate_paths(source: Path, dest: Path):
    def is_tif(p: Path):
        return p.suffix.lower() in [".tif", ".tiff"]

    def file_exists(p: Path):
        return p.exists() and p.is_file()

    def dir_exists(p: Path):
        return p.exists() and p.is_dir()

    # Check that input and output paths are tif files
    if not is_tif(source):
        raise ValueError("The source must be a tif file.")
    if not is_tif(dest):
        raise ValueError("The dest must be a tif file.")
    # Check that input path exists
    if not file_exists(source):
        raise ValueError("The source file does not exist.")
    # Check that output path parent exists
    if not dir_exists(dest.parent):
        raise ValueError("The directory for path dest does not exist.")
    # Check that input and output paths are different
    if source == dest:
        raise ValueError(
            "The source and dest paths must be different. "
            "Please specify a different dest."
        )


def find_kelp(
    source: Union[str, Path],
    dest: Union[str, Path],
    species: bool = False,
    crop_size: int = 1024,
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
        use_gpu: Disable Cuda GPU usage and run on CPU only.
    """
    _validate_paths(Path(source), Path(dest))
    if species:
        model = KelpSpeciesSegmentationModel(use_gpu=use_gpu)
    else:
        model = KelpPresenceSegmentationModel(use_gpu=use_gpu)
    RichSegmentationManager(model, Path(source), Path(dest), crop_size=crop_size)()


def find_mussels(
    source: Union[str, Path],
    dest: Union[str, Path],
    crop_size: int = 1024,
    use_gpu: bool = True,
):
    """
    Detect mussels in image at path `source` and output the resulting classification
    raster to file at path `dest`.

    Args:
        source: Input image with Byte data type.
        dest: File path location to save output to.
        crop_size: The size of cropped image square run through the segmentation model.
        use_gpu: Disable Cuda GPU usage and run on CPU only.
    """
    _validate_paths(Path(source), Path(dest))
    model = MusselPresenceSegmentationModel(use_gpu=use_gpu)
    RichSegmentationManager(model, Path(source), Path(dest), crop_size=crop_size)()
