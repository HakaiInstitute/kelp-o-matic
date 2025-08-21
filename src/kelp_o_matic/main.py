from __future__ import annotations

from pathlib import Path
from typing import Annotated

import humanize
from cyclopts import App, Parameter
from rich.panel import Panel
from rich.prompt import Confirm
from rich.table import Table
from rich.traceback import install

from kelp_o_matic.registry import model_registry
from kelp_o_matic.utils import (
    get_local_model_dir,
    console,
    is_url,
    get_local_model_path,
)

# Install rich traceback formatting
install(show_locals=True, max_frames=5)

app = App()


@app.command
def models() -> None:
    """
    List all available models with their latest revisions.
    """
    table = Table(title="[bold green]Available Models[/bold green]")
    table.add_column("Model Name", style="cyan", no_wrap=True)
    table.add_column("Revision", style="magenta")
    table.add_column("Description", style="white")
    table.add_column("Status", style="green")

    # Show only the latest revision of each model
    model_names = model_registry.list_model_names()
    for model_name in sorted(model_names):
        try:
            # Get the latest revision of this model
            latest_revision = model_registry.get_latest_revision(model_name)
            model = model_registry[model_name]  # Gets latest revision
            cfg = model.cfg

            # Check if model is cached locally
            local_path = get_local_model_path(cfg)
            if is_url(cfg.model_path):
                status = (
                    "[green]Cached[/green]"
                    if local_path.exists()
                    else "[yellow]Available[/yellow]"
                )
            else:
                status = (
                    "[green]Local[/green]"
                    if local_path.exists()
                    else "[red]Missing[/red]"
                )

            table.add_row(
                model_name, latest_revision, cfg.description or "No description", status
            )
        except Exception as e:
            error_panel = Panel(
                f"[red]Error loading model '{model_name}': {e}[/red]",
                title="[bold red]Model Error[/bold red]",
                border_style="red",
            )
            console.print(error_panel)
            table.add_row(
                model_name,
                "Error",
                "Failed to load model configuration",
                "[red]Error[/red]",
            )

    console.print(table)


@app.command
def revisions(
    model_name: str,
) -> None:
    """
    List all available revisions for a specific model.
    """
    # Check if model exists
    if model_name not in model_registry:
        available_models = ", ".join(sorted(model_registry.list_model_names()))
        error_panel = Panel(
            f"[red]Model '{model_name}' not found.\n\nAvailable models: {available_models}[/red]",
            title="[bold red]Model Error[/bold red]",
            border_style="red",
        )
        console.print(error_panel)
        return

    table = Table(title=f"[bold green]Revisions for {model_name}[/bold green]")
    table.add_column("Revision", style="magenta")
    table.add_column("Latest", style="bright_yellow", justify="center")
    table.add_column("Description", style="white")
    table.add_column("Status", style="green")

    try:
        # Get all revisions for this model
        models_by_revision = model_registry._models[model_name]
        latest_revision = model_registry.get_latest_revision(model_name)

        for revision in sorted(models_by_revision.keys(), reverse=True):
            model = models_by_revision[revision]
            cfg = model.cfg

            # Check if model is cached locally
            local_path = get_local_model_path(cfg)
            if is_url(cfg.model_path):
                status = (
                    "[green]Cached[/green]"
                    if local_path.exists()
                    else "[yellow]Available[/yellow]"
                )
            else:
                status = (
                    "[green]Local[/green]"
                    if local_path.exists()
                    else "[red]Missing[/red]"
                )

            # Mark latest revision
            is_latest = "✓" if revision == latest_revision else ""

            table.add_row(
                revision, is_latest, cfg.description or "No description", status
            )
    except Exception as e:
        error_panel = Panel(
            f"[red]Error loading revisions for model '{model_name}': {e}[/red]",
            title="[bold red]Model Error[/bold red]",
            border_style="red",
        )
        console.print(error_panel)
        return

    console.print(table)


@app.command
def clean() -> None:
    """
    Empty the Kelp-O-Matic model cache to free up space. Models will be re-downloaded as needed.
    """
    model_dir = get_local_model_dir()
    files = list(model_dir.glob("*.onnx"))
    if not files:
        panel = Panel(
            "[yellow]Model cache is already empty.[/yellow]",
            title="[bold blue]Cache Status[/bold blue]",
            border_style="blue",
        )
        console.print(panel)
        return

    total_size = sum(file.stat().st_size for file in files)

    if not Confirm.ask(
        f"[yellow]Are you sure you want to clear the model cache? "
        f"This will free up {humanize.naturalsize(total_size)}.[/yellow]",
        default=False,
    ):
        console.print("[yellow]Model cache clearing aborted.[/yellow]")
        return

    console.print("[blue]Clearing model cache...[/blue]")
    for file in model_dir.glob("*.onnx"):
        file.unlink()

    panel = Panel(
        f"[green]✓ Cleared model cache at {model_dir}.\nFreed {humanize.naturalsize(total_size)}[/green]",
        title="[bold green]Cache Cleared[/bold green]",
        border_style="green",
    )
    console.print(panel)


@app.command
def segment(
    model_name: Annotated[
        str,
        Parameter(
            help="The name of the model to run. Run `kom models` to see options",
            name=["--model", "-m"],
        ),
    ],
    img_path: Annotated[
        Path,
        Parameter(
            help="Path to input 8 band PlanetScope raster file", name=["--input", "-i"]
        ),
    ],
    output_path: Annotated[
        Path,
        Parameter(
            help="Path to the output raster that will be created",
            name=["--output", "-o"],
        ),
    ],
    revision: Annotated[
        str,
        Parameter(
            help="The revision of the model to use. Run `kom revisions <model_name>` to see options",
            name=["--revision", "--rev"],
        ),
    ] = "latest",
    batch_size: Annotated[
        int,
        Parameter(
            help="Batch size for processing",
            validator=lambda _, x: x > 0,
            name=["--batch-size"],
            alias="--batch",
        ),
    ] = 1,
    crop_size: Annotated[
        int | None,
        Parameter(
            help="Tile size for processing (must be even). Defaults to the 1024 or to the size required by the model",
            validator=lambda _, x: (x is None) or (x % 2 == 0 and x > 0),
            name=["--crop-size", "-z"],
            alias="--size",
        ),
    ] = None,
    blur_kernel_size: Annotated[
        int,
        Parameter(
            help="Size of median blur kernel (must be odd)",
            validator=lambda _, x: x % 2 == 1 and x > 0,
            name=["--blur-kernel"],
            alias="--blur",
        ),
    ] = 5,
    morph_kernel_size: Annotated[
        int,
        Parameter(
            help="Size of morphological kernel (must be odd, 0 to disable)",
            validator=lambda _, x: x % 2 == 1 or x == 0,
            name=["--morph-kernel"],
            alias="--morph",
        ),
    ] = 0,
    band_order: Annotated[
        list[int] | None,
        Parameter(
            help="Band reordering flag for rearranging bands into RGB(+NIR) order when necessary.",
            validator=lambda _, x: x is None or all([a > 1 for a in x]),
            name=["--band-order", "-b"],
        ),
    ] = None,
) -> None:
    """Apply a segmentation model to an input raster and save the output."""
    try:
        # Validate input file exists
        input_file = Path(img_path).expanduser()
        if not input_file.exists():
            error_panel = Panel(
                f"[red]Input file not found: {input_file}[/red]",
                title="[bold red]File Error[/bold red]",
                border_style="red",
            )
            console.print(error_panel)
            return

        # Validate model exists
        if model_name not in model_registry:
            available_models = ", ".join(model_registry.list_model_names())
            error_panel = Panel(
                f"[red]Model '{model_name}' not found.\n\nAvailable models: {available_models}[/red]",
                title="[bold red]Model Error[/bold red]",
                border_style="red",
            )
            console.print(error_panel)
            return

        # Handle revision retrieval
        try:
            if revision == "latest":
                model = model_registry[model_name]  # Gets latest revision
                actual_revision = model_registry.get_latest_revision(model_name)
            else:
                model = model_registry[model_name, revision]  # Gets specific revision
                actual_revision = revision
        except KeyError as e:
            error_panel = Panel(
                f"[red]{e}[/red]",
                title="[bold red]Revision Error[/bold red]",
                border_style="red",
            )
            console.print(error_panel)
            return

        # Show processing info in a panel
        info_panel = Panel(
            f"[blue]Model:[/blue] {model_name}\n"
            f"[blue]Revision:[/blue] {actual_revision}\n"
            f"[blue]Input:[/blue] {input_file}\n"
            f"[blue]Output:[/blue] {Path(output_path).expanduser()}",
            title="[bold blue]Processing Configuration[/bold blue]",
            border_style="blue",
        )
        console.print(info_panel)

        model.process(
            img_path=input_file,
            output_path=Path(output_path).expanduser(),
            batch_size=batch_size,
            crop_size=crop_size,
            blur_kernel_size=blur_kernel_size,
            morph_kernel_size=morph_kernel_size,
            band_order=band_order,
        )

        # Show a success message
        success_panel = Panel(
            f"[green]✓ Successfully processed {input_file.name}\n"
            f"Output saved to: {Path(output_path).expanduser()}[/green]",
            title="[bold green]Processing Complete[/bold green]",
            border_style="green",
        )
        console.print(success_panel)

    except KeyboardInterrupt:
        console.print("\n[yellow]Processing interrupted by user[/yellow]")
    except Exception as e:
        error_panel = Panel(
            f"[red]Processing failed: {e}[/red]\n\n"
            f"[dim]Use --help for usage information[/dim]",
            title="[bold red]Processing Error[/bold red]",
            border_style="red",
        )
        console.print(error_panel)
        raise  # Re-raise to show full traceback with Rich formatting


if __name__ == "__main__":
    app()
