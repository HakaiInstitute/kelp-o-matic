import typer

from kelp_o_matic import lib

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
    padding: int = typer.Option(
        256, help="The number of context pixels added to each side of the image crops."
    ),
    batch_size: int = typer.Option(
        1, help="The batch size of cropped image sections to process together."
    ),
    use_gpu: bool = typer.Option(
        True, "--gpu/--no-gpu", help="Enable or disable GPU, if available."
    ),
):
    """
    Detect kelp in image at path SOURCE and output the resulting classification raster
    to file at path DEST.
    """
    lib.find_kelp(
        source=source,
        dest=dest,
        species=species,
        crop_size=crop_size,
        padding=padding,
        batch_size=batch_size,
        use_gpu=use_gpu,
    )


@cli.command()
def find_mussels(
    source: str = typer.Argument(..., help="Input image with Byte data type."),
    dest: str = typer.Argument(..., help="File path location to save output to."),
    crop_size: int = typer.Option(
        512,
        help="The data window size to run through the segmentation model.",
    ),
    padding: int = typer.Option(
        256, help="The number of context pixels added to each side of the image crops."
    ),
    batch_size: int = typer.Option(
        1, help="The batch size of cropped image sections to process together."
    ),
    use_gpu: bool = typer.Option(
        True, "--gpu/--no-gpu", help="Enable or disable GPU, if available."
    ),
):
    """
    Detect mussels in image at path SOURCE and output the resulting classification
    raster to file at path DEST.
    """
    lib.find_mussels(
        source=source,
        dest=dest,
        crop_size=crop_size,
        padding=padding,
        batch_size=batch_size,
        use_gpu=use_gpu,
    )


if __name__ == "__main__":
    cli()
