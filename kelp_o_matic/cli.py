from pathlib import Path
from typing import Annotated, Optional

import torch
import typer

from kelp_o_matic import (
    __version__,
    find_kelp as find_kelp_,
    find_mussels as find_mussels_,
)

cli = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]}, add_completion=False)


@cli.command()
def find_kelp(
    source: Annotated[
        Path,
        typer.Argument(
            exists=True,
            dir_okay=False,
            file_okay=True,
            readable=True,
            help="Input image with Byte data type.",
        ),
    ],
    dest: Annotated[
        Path,
        typer.Argument(
            exists=False,
            dir_okay=False,
            file_okay=True,
            writable=True,
            help="File path location to save output to.",
        ),
    ],
    species: Annotated[
        bool,
        typer.Option(
            "--species/--presence",
            help="Segment to species or presence/absence level.",
        ),
    ] = False,
    crop_size: Annotated[
        int,
        typer.Option(
            help="The data window size to run through the segmentation model.",
        ),
    ] = 1024,
    use_nir: Annotated[
        bool,
        typer.Option(
            "--rgbi/--rgb",
            help="Use RGB and NIR bands for classification. Assumes RGBI ordering.",
        ),
    ] = False,
    band_order: Annotated[
        Optional[list[int]],
        typer.Option(
            "-b",
            help="GDAL-style band re-ordering flag. Defaults to RGB or RGBI order. "
            "To e.g., reorder a BGRI image at runtime, pass flags `-b 3 -b 2 -b 1 -b 4`.",
        ),
    ] = None,
    use_gpu: Annotated[
        bool,
        typer.Option("--gpu/--no-gpu", help="Enable or disable GPU, if available."),
    ] = True,
    use_tta: Annotated[
        bool,
        typer.Option(
            "--tta/--no-tta",
            help="Use test time augmentation to improve accuracy at the cost of "
            "processing time.",
        ),
    ] = False,
):
    """
    Detect kelp in image at path SOURCE and output the resulting classification raster
    to file at path DEST.
    """
    find_kelp_(source, dest, species, crop_size, use_nir, band_order, use_gpu, use_tta)


@cli.command()
def find_mussels(
    source: Annotated[
        Path,
        typer.Argument(
            exists=True,
            dir_okay=False,
            file_okay=True,
            readable=True,
            help="Input image with Byte data type.",
        ),
    ],
    dest: Annotated[
        Path,
        typer.Argument(
            exists=False,
            dir_okay=False,
            file_okay=True,
            writable=True,
            help="File path location to save output to.",
        ),
    ],
    crop_size: Annotated[
        int,
        typer.Option(
            help="The data window size to run through the segmentation model.",
        ),
    ] = 1024,
    band_order: Annotated[
        Optional[list[int]],
        typer.Option(
            "-b",
            help="GDAL-style band re-ordering flag. Defaults to RGB or RGBI order. "
            "To e.g., reorder a BGRI image at runtime, pass flags `-b 3 -b 2 -b 1 -b 4`.",
        ),
    ] = None,
    use_gpu: Annotated[
        bool,
        typer.Option("--gpu/--no-gpu", help="Enable or disable GPU, if available."),
    ] = True,
    use_tta: Annotated[
        bool,
        typer.Option(
            "--tta/--no-tta",
            help="Use test time augmentation to improve accuracy at the cost of "
            "processing time.",
        ),
    ] = False,
):
    """
    Detect mussels in image at path SOURCE and output the resulting classification
    raster to file at path DEST.
    """
    find_mussels_(source, dest, crop_size, band_order, use_gpu, use_tta)


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"Kelp-O-Matic {__version__}")
        raise typer.Exit()


def gpu_callback(value: bool) -> None:
    if value:
        typer.echo(f"GPU detected: {torch.cuda.is_available()}")
        raise typer.Exit()


@cli.callback()
def main(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-v",
            callback=version_callback,
            is_eager=True,
            help="Show version and exit.",
        ),
    ] = False,
    gpu_test: Annotated[
        bool,
        typer.Option(
            "--gpu-test",
            callback=gpu_callback,
            is_eager=True,
            help="Test if GPU is detected and exit.",
        ),
    ] = False,
):
    return


if __name__ == "__main__":
    cli()
