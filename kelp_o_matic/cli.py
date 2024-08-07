from pathlib import Path
from typing import Optional

import typer

from kelp_o_matic import (
    __version__,
    find_kelp as find_kelp_,
    find_mussels as find_mussels_,
)

cli = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]})


@cli.command()
def find_kelp(
    source: Path = typer.Argument(..., help="Input image with Byte data type."),
    dest: Path = typer.Argument(..., help="File path location to save output to."),
    species: bool = typer.Option(
        False,
        "--species/--presence",
        help="Segment to species or presence/absence level.",
    ),
    crop_size: int = typer.Option(
        1024,
        help="The data window size to run through the segmentation model.",
    ),
    use_nir: bool = typer.Option(
        False,
        "--rgbi/--rgb",
        help="Use RGB and NIR bands for classification. Assumes RGBI ordering.",
    ),
    band_order: Optional[list[int]] = typer.Option(
        None,
        "-b",
        help="GDAL-style band re-ordering flag. Defaults to RGB or RGBI order. "
        "To e.g., reorder a BGRI image at runtime, pass flags `-b 3 -b 2 -b 1 -b 4`.",
    ),
    use_gpu: bool = typer.Option(
        True, "--gpu/--no-gpu", help="Enable or disable GPU, if available."
    ),
    use_tta: bool = typer.Option(
        False,
        "--tta/--no-tta",
        help="Use test time augmentation to improve accuracy at the cost of "
        "processing time.",
    ),
):
    """
    Detect kelp in image at path SOURCE and output the resulting classification raster
    to file at path DEST.
    """
    find_kelp_(source, dest, species, crop_size, use_nir, band_order, use_gpu, use_tta)


@cli.command()
def find_mussels(
    source: Path = typer.Argument(..., help="Input image with Byte data type."),
    dest: Path = typer.Argument(..., help="File path location to save output to."),
    crop_size: int = typer.Option(
        1024,
        help="The data window size to run through the segmentation model.",
    ),
    band_order: Optional[list[int]] = typer.Option(
        None,
        "-b",
        help="GDAL-style band re-ordering flag. Defaults to RGB order. "
        "To e.g., reorder a BGR image at runtime, pass flags `-b 3 -b 2 -b 1`.",
    ),
    use_gpu: bool = typer.Option(
        True, "--gpu/--no-gpu", help="Enable or disable GPU, if available."
    ),
    use_tta: bool = typer.Option(
        False,
        "--tta/--no-tta",
        help="Use test time augmentation to improve accuracy at the cost of "
        "processing time.",
    ),
):
    """
    Detect mussels in image at path SOURCE and output the resulting classification
    raster to file at path DEST.
    """
    find_mussels_(source, dest, crop_size, band_order, use_gpu, use_tta)


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"Kelp-o-Matic {__version__}")
        raise typer.Exit()


@cli.callback()
def main(
    version: bool = typer.Option(
        None, "--version", "-v", callback=version_callback, is_eager=True
    ),
):
    return


if __name__ == "__main__":
    cli()
