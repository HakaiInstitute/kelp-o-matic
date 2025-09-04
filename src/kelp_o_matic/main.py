"""Kelp-O-Matic CLI for managing and using segmentation models."""

from __future__ import annotations

import os
from importlib.metadata import version
from pathlib import Path
from typing import Annotated

import deprecation
import humanize
from cyclopts import App, Parameter
from cyclopts.types import ExistingFile, File, PositiveInt  # noqa: TC002
from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.table import Table
from rich.traceback import install

from kelp_o_matic.registry import model_registry
from kelp_o_matic.utils import (
    get_local_model_dir,
    get_local_model_path,
    is_url,
)

app = App()
console = Console()


def _log_formatter(record: dict) -> str:
    """Log message formatter.

    Returns:
        Formatting string for log messages logged with Rich console
    """
    color_map = {
        "TRACE": "dim blue",
        "DEBUG": "cyan",
        "INFO": "bold",
        "SUCCESS": "green",
        "WARNING": "yellow",
        "ERROR": "bold red",
        "CRITICAL": "bold white on red",
    }
    lvl_color = color_map.get(record["level"].name, "cyan")
    return f"[not bold cyan]{{time:YYYY-MM-DD HH:mm:ss}}[/not bold cyan] | [{lvl_color}]{{message}}[/{lvl_color}]"


DEBUG = bool(os.getenv("DEBUG", False))

# Setup Rich logger handler
logger.remove()
logger.add(
    console.print,
    level="TRACE",
    format=_log_formatter,
    colorize=None,
)

# Decorator to log error messages
logger_catch = logger.catch(
    message=(
        "[bold red]Program interrupted due to {record[exception].type.__name__}: '{record[exception].value}'[/bold red]"
    ),
    reraise=DEBUG,
)

# Install rich traceback formatting
if DEBUG:
    install()


def _positive_even_int_validator(type_: type, value: int | None) -> None:
    if value is None:
        pass
    elif value % 2 == 1 or value <= 0:
        raise TypeError("Value must be a positive, even number.")


def _positive_odd_int_or_zero_validator(type_: type, value: int | None) -> None:
    if value is None:
        pass
    elif value == 0:
        pass
    elif value % 2 == 0 or value < 0:
        raise TypeError("Value must be a positive, odd number.")


def _band_validator(type_: type, value: list[int] | None) -> None:
    if value is None:
        pass
    elif not all([v >= 1 for v in value]):
        raise TypeError("All values must be >= 1.")


def _existing_model_validator(type_: type, value: str) -> None:
    if value not in model_registry.list_model_names():
        raise TypeError("Specified model is not a valid option.")


@app.command
@logger_catch
def models() -> None:
    """List all available models with their latest revisions."""
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
                status = "[green]Cached[/green]" if local_path.exists() else "[yellow]Available[/yellow]"
            else:
                status = "[green]Local[/green]" if local_path.exists() else "[red]Missing[/red]"

            table.add_row(
                model_name,
                latest_revision,
                cfg.description or "No description",
                status,
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
@logger_catch
def revisions(
    model_name: Annotated[
        str,
        Parameter(
            help="The name of the model to run. Run `kom models` to see options",
            validator=_existing_model_validator,
            name=["--model", "-m"],
        ),
    ],
) -> None:
    """List all available revisions for a specific model."""
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
                status = "[green]Cached[/green]" if local_path.exists() else "[yellow]Available[/yellow]"
            else:
                status = "[green]Local[/green]" if local_path.exists() else "[red]Missing[/red]"

            # Mark latest revision
            is_latest = "✓" if revision == latest_revision else ""

            table.add_row(
                revision,
                is_latest,
                cfg.description or "No description",
                status,
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
@logger_catch
def clean() -> None:
    """Clear the Kelp-O-Matic model cache to free up space. Models will be re-downloaded as needed."""
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
        logger.warning("Model cache clearing aborted.")
        return

    logger.info("Clearing model cache...")
    for file in model_dir.glob("*.onnx"):
        file.unlink()

    panel = Panel(
        f"[green]✓ Cleared model cache at {model_dir}.\nFreed {humanize.naturalsize(total_size)}[/green]",
        title="[bold green]Cache Cleared[/bold green]",
        border_style="green",
    )
    console.print(panel)


@app.command
@logger_catch
def segment(
    model_name: Annotated[
        str,
        Parameter(
            help="The name of the model to run. Run `kom models` to see options",
            validator=_existing_model_validator,
            name=["--model", "-m"],
        ),
    ],
    img_path: Annotated[
        ExistingFile,
        Parameter(
            help="Path to input 8 band PlanetScope raster file",
            name=["--input", "-i"],
        ),
    ],
    output_path: Annotated[
        File,
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
        PositiveInt,
        Parameter(
            help="Batch size for processing",
            name=["--batch-size"],
            alias="--batch",
        ),
    ] = 1,
    crop_size: Annotated[
        int | None,
        Parameter(
            help="Tile size for processing (must be even). Defaults to the 1024 or to the size required by the model",
            validator=_positive_even_int_validator,
            name=["--crop-size", "-z"],
            alias="--size",
        ),
    ] = None,
    blur_kernel_size: Annotated[
        int,
        Parameter(
            help="Size of median blur kernel (must be odd)",
            validator=_positive_odd_int_or_zero_validator,
            name=["--blur-kernel"],
            alias="--blur",
        ),
    ] = 5,
    morph_kernel_size: Annotated[
        int,
        Parameter(
            help="Size of morphological kernel (must be odd, 0 to disable)",
            validator=_positive_odd_int_or_zero_validator,
            name=["--morph-kernel"],
            alias="--morph",
        ),
    ] = 0,
    band_order: Annotated[
        list[int] | None,
        Parameter(
            help="Band reordering flag for rearranging bands into RGB(+NIR) order when necessary.",
            validator=_band_validator,
            name=["--band-order", "-b"],
        ),
    ] = None,
) -> None:
    """Apply a segmentation model to an input raster and save the output."""
    # Handle revision retrieval
    try:
        if revision == "latest":
            model = model_registry[model_name]  # Gets latest revision
            actual_revision = model_registry.get_latest_revision(model_name)
        else:
            model = model_registry[model_name, revision]  # Gets specific revision
            actual_revision = revision
    except KeyError:
        logger.error(f"Revision {revision} was not found for model {model_name}")
        return

    # Show processing info in a panel
    info_panel = Panel(
        f"[blue]Model:[/blue] {model_name}\n"
        f"[blue]Revision:[/blue] {actual_revision}\n"
        f"[blue]Input:[/blue] {img_path}\n"
        f"[blue]Output:[/blue] {Path(output_path).expanduser()}",
        title="[bold blue]Processing Configuration[/bold blue]",
        border_style="blue",
    )
    console.print(info_panel)

    model.process(
        img_path=img_path,
        output_path=Path(output_path).expanduser(),
        batch_size=batch_size,
        crop_size=crop_size,
        blur_kernel_size=blur_kernel_size,
        morph_kernel_size=morph_kernel_size,
        band_order=band_order,
    )

    # Show a success message
    success_panel = Panel(
        f"[green]✓ Successfully processed {img_path.name}\nOutput saved to: {Path(output_path).expanduser()}[/green]",
        title="[bold green]Processing Complete[/bold green]",
        border_style="green",
    )
    console.print(success_panel)


@app.command
@deprecation.deprecated(
    deprecated_in="0.14.0",
    removed_in="0.15.0",
    current_version=version("kelp_o_matic"),
    details="Please use the `kom segment` command instead.",
)
@logger_catch
def find_kelp(
    source: Annotated[
        ExistingFile,
        Parameter(
            help="Input image with Byte data type.",
            name=[],
        ),
    ],
    dest: Annotated[
        File,
        Parameter(
            help="File path location to save output to.",
            name=[],
        ),
    ],
    species: Annotated[
        bool,
        Parameter(
            "--species",
            negative="--presence",
            help="Segment to species or presence/absence level.",
        ),
    ] = False,
    crop_size: Annotated[
        int,
        Parameter(
            validator=_positive_even_int_validator(),
            help="The data window size to run through the segmentation model.",
        ),
    ] = 1024,
    use_nir: Annotated[
        bool,
        Parameter(
            "--rgbi",
            negative="--rgb",
            help="Use RGB and NIR bands for classification. Assumes RGBI ordering.",
        ),
    ] = False,
    band_order: Annotated[
        list[int] | None,
        Parameter(
            help="GDAL-style band re-ordering flag. Defaults to RGB or RGBI order. "
            "To e.g., reorder a BGRI image at runtime, pass flags `-b 3 -b 2 -b 1 -b 4`.",
            validator=_band_validator,
            name=["--band-order", "-b"],
        ),
    ] = None,
    use_gpu: Annotated[
        bool,
        Parameter("--gpu", negative="--no-gpu", help="Enable or disable GPU, if available."),
    ] = True,
    use_tta: Annotated[
        bool,
        Parameter(
            "--tta",
            negative="--no-tta",
            help="Use test time augmentation to improve accuracy at the cost of processing time.",
        ),
    ] = False,
) -> None:
    """DEPRECATED: Use `segment` instead.

    Detect kelp in image at path SOURCE and output the resulting classification raster to file at path DEST.
    """
    logger.warning("`kom find-kelp` is deprecated and will be removed in v0.15.0. Please use `kom segment` instead")

    if not species:
        logger.warning(
            "Only species kelp detection is supported since version 0.14.0. Proceeding with kelp species detection."
        )

    if not use_gpu:
        logger.warning("Since version 0.14.0, GPU and CPU usage is determined automatically and cannot be overridden.")

    if use_tta:
        logger.warning(
            "Since version 0.14.0, test-time augmentation is no longer supported. Please open a GitHub issue at "
            "https://github.com/HakaiInstitute/kelp-o-matic if you would like to see test-time augmentation added "
            "back into Kelp-o-Matic"
        )

    segment(
        model_name=("kelp-rgbi" if use_nir else "kelp-rgb"),
        img_path=source,
        output_path=dest,
        revision="latest",
        batch_size=1,
        crop_size=crop_size,
        blur_kernel_size=0,
        morph_kernel_size=0,
        band_order=band_order,
    )


@app.command
@deprecation.deprecated(
    deprecated_in="0.14.0",
    removed_in="0.15.0",
    current_version=version("kelp_o_matic"),
    details="Please use the `kom segment` command instead.",
)
@logger_catch
def find_mussels(
    source: Annotated[
        ExistingFile,
        Parameter(
            help="Input image with Byte data type.",
            name=[],
        ),
    ],
    dest: Annotated[
        File,
        Parameter(
            help="File path location to save output to.",
            name=[],
        ),
    ],
    crop_size: Annotated[
        int,
        Parameter(
            validator=_positive_even_int_validator,
            help="The data window size to run through the segmentation model.",
        ),
    ] = 1024,
    band_order: Annotated[
        list[int] | None,
        Parameter(
            help="GDAL-style band re-ordering flag. Defaults to RGB or RGBI order. "
            "To e.g., reorder a BGRI image at runtime, pass flags `-b 3 -b 2 -b 1 -b 4`.",
            validator=_band_validator,
            name=["--band-order", "-b"],
        ),
    ] = None,
    use_gpu: Annotated[
        bool,
        Parameter("--gpu", negative="--no-gpu", help="Enable or disable GPU, if available."),
    ] = True,
    use_tta: Annotated[
        bool,
        Parameter(
            "--tta",
            negative="--no-tta",
            help="Use test time augmentation to improve accuracy at the cost of processing time.",
        ),
    ] = False,
) -> None:
    """DEPRECATED: Use `segment` instead.

    Detect kelp in image at path SOURCE and output the resulting classification raster to file at path DEST.
    """
    logger.warning("`kom find-mussels` is deprecated and will be removed in v0.15.0. Please use `kom segment` instead")

    if not use_gpu:
        logger.warning("Since version 0.14.0, GPU and CPU usage is determined automatically and cannot be overridden.")

    if use_tta:
        logger.warning(
            "Since version 0.14.0, test-time augmentation is no longer supported. Please open a GitHub issue at "
            "https://github.com/HakaiInstitute/kelp-o-matic if you would like to see test-time augmentation added "
            "back into Kelp-o-Matic"
        )

    segment(
        model_name="mussel-rgb",
        img_path=source,
        output_path=dest,
        revision="latest",
        batch_size=1,
        crop_size=crop_size,
        blur_kernel_size=0,
        morph_kernel_size=0,
        band_order=band_order,
    )


if __name__ == "__main__":
    # Run the cli app
    app()
