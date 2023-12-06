import typer

from kelp_o_matic import __version__
from kelp_o_matic.managers import RichSegmentationManager
from kelp_o_matic.models import (
    KelpPresenceSegmentationModel,
    KelpSpeciesSegmentationModel,
    MusselPresenceSegmentationModel,
)

cli = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]})


@cli.command()
def find_kelp(
    source: str = typer.Argument(..., help="Input image with Byte data type."),
    dest: str = typer.Argument(..., help="File path location to save output to."),
    species: bool = typer.Option(
        False,
        "--species/--presence",
        help="Segment to species or presence/absence level.",
    ),
    crop_size: int = typer.Option(
        512,
        help="The data window size to run through the segmentation model.",
    ),
    use_gpu: bool = typer.Option(
        True, "--gpu/--no-gpu", help="Enable or disable GPU, if available."
    ),
):
    """
    Detect kelp in image at path SOURCE and output the resulting classification raster
    to file at path DEST.
    """
    model = (
        KelpSpeciesSegmentationModel(use_gpu=use_gpu)
        if species
        else KelpPresenceSegmentationModel(use_gpu=use_gpu)
    )
    manager = RichSegmentationManager(model, source, dest, crop_size=crop_size)
    manager()


@cli.command()
def find_mussels(
    source: str = typer.Argument(..., help="Input image with Byte data type."),
    dest: str = typer.Argument(..., help="File path location to save output to."),
    crop_size: int = typer.Option(
        512,
        help="The data window size to run through the segmentation model.",
    ),
    use_gpu: bool = typer.Option(
        True, "--gpu/--no-gpu", help="Enable or disable GPU, if available."
    ),
):
    """
    Detect mussels in image at path SOURCE and output the resulting classification
    raster to file at path DEST.
    """
    model = MusselPresenceSegmentationModel(use_gpu=use_gpu)
    manager = RichSegmentationManager(model, source, dest, crop_size=crop_size)
    manager()


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"Kelp-O-Matic {__version__}")
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
