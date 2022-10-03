import typer

from hakai_segmentation import lib

cli = typer.Typer()


@cli.command()
def find_kelp(
        source: str = typer.Argument(..., help="Input image with Byte data type."),
        dest: str = typer.Argument(..., help="File path location to save output to."),
        species: bool = typer.Option(False, "--species/--presence", help="Segment to species or presence/absence level."),
        crop_size: int = typer.Option(256, help="The size for the cropped image squares run through the segmentation model."),
        padding: int = typer.Option(128, help="The number of context pixels added to each side of the image crops."),
        batch_size: int = typer.Option(2, help="The batch size of cropped image sections to process together."),
        use_gpu: bool = typer.Option(True, "--gpu/--no-gpu", help="Enable or disable GPU, if available."),
        reload_model_on_batch: bool = typer.Option(False, "--reload-model-on-batch/--no-reload-model-on-batch",
                                                   help="Experimental flag to reload the model for each data batch. May resolve memory issues.")
):
    """Detect kelp in image at path SOURCE and output the resulting classification raster to file at path DEST."""
    lib.find_kelp(source=source, dest=dest, species=species,
                  crop_size=crop_size, padding=padding, batch_size=batch_size, use_gpu=use_gpu,
                  reload_model_on_batch=reload_model_on_batch)


@cli.command()
def find_mussels(
        source: str = typer.Argument(..., help="Input image with Byte data type."),
        dest: str = typer.Argument(..., help="File path location to save output to."),
        crop_size: int = typer.Option(256, help="The size for the cropped image squares run through the segmentation model."),
        padding: int = typer.Option(128, help="The number of context pixels added to each side of the image crops."),
        batch_size: int = typer.Option(2, help="The batch size of cropped image sections to process together."),
        use_gpu: bool = typer.Option(True, "--gpu/--no-gpu", help="Enable or disable GPU, if available."),
        reload_model_on_batch: bool = typer.Option(False, "--reload-model-on-batch/--no-reload-model-on-batch",
                                                   help="Experimental flag to reload the model for each data batch. May resolve memory issues.")
):
    """Detect mussels in image at path SOURCE and output the resulting classification raster to file at path DEST."""
    lib.find_mussels(source=source, dest=dest,
                     crop_size=crop_size, padding=padding, batch_size=batch_size, use_gpu=use_gpu,
                     reload_model_on_batch=reload_model_on_batch)


if __name__ == '__main__':
    cli()
