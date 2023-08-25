import typer
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn
from rich import print

from kelp_o_matic import GeotiffSegmentationManager, __version__
from kelp_o_matic.models import (
    KelpPresenceSegmentationModel,
    KelpSpeciesSegmentationModel,
    MusselPresenceSegmentationModel,
)

cli = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]})


class _CLISegmentationManager(GeotiffSegmentationManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.progress = Progress(
            SpinnerColumn("earth"), *Progress.get_default_columns(), TimeElapsedColumn()
        )
        self.processing_task = self.progress.add_task(
            description="Processing", total=len(self.reader)
        )

    def __call__(self):
        with self.progress:
            super().__call__()

    def on_start(self):
        device_emoji = ":rocket:" if self.model.device.type == "cuda" else ":snail:"
        print(f"Running with [magenta]{self.model.device} {device_emoji}")

    def on_chip_write_end(self, index: int):
        self.progress.update(self.processing_task, completed=index)

    def on_end(self):
        self.progress.update(self.processing_task, completed=len(self.reader))
        print("[bold italic green]:tada: Segmentation complete! :tada:[/]")


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
    model = (
        KelpSpeciesSegmentationModel(use_gpu=use_gpu)
        if species
        else KelpPresenceSegmentationModel(use_gpu=use_gpu)
    )
    manager = _CLISegmentationManager(
        model, source, dest, crop_size=crop_size, padding=padding, batch_size=batch_size
    )
    manager()


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
    model = MusselPresenceSegmentationModel(use_gpu=use_gpu)
    manager = _CLISegmentationManager(
        model, source, dest, crop_size=crop_size, padding=padding, batch_size=batch_size
    )
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
