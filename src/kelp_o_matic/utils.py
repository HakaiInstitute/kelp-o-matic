from __future__ import annotations

from pathlib import Path

import onnxruntime as ort
import platformdirs
import requests
from rich.console import Console
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TransferSpeedColumn,
)
from typing import TYPE_CHECKING, Iterable, Any
import itertools

if TYPE_CHECKING:
    from kelp_o_matic.config import ModelConfig

console = Console()


def download_file_with_progress(url: str, out_path: Path):
    response = requests.get(url, stream=True)
    response.raise_for_status()

    # Get total file size
    total_size = int(response.headers.get("content-length", 0))

    # Download with progress
    with open(out_path, "wb") as f:
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            DownloadColumn(),
            TransferSpeedColumn(),
            console=None,  # Use default console
        ) as progress:
            task = progress.add_task(f"Downloading {out_path.name}", total=total_size)
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                progress.update(task, advance=len(chunk))


def get_ort_providers():
    available_providers = ort.get_available_providers()
    providers = []

    if "NvTensorRtRtxExecutionProvider" in available_providers:
        providers.append("NvTensorRtRtxExecutionProvider")

    if "CUDAExecutionProvider" in available_providers:
        providers.append("CUDAExecutionProvider")

    providers.append("CPUExecutionProvider")
    return providers


def get_local_model_dir() -> Path:
    cache_dir = platformdirs.user_cache_dir(appname="kelp_o_matic", appauthor="hakai")
    model_dir = Path(cache_dir) / "models"
    model_dir.mkdir(exist_ok=True, parents=True)
    return model_dir


def is_url(uri: str) -> bool:
    """
    Check if a URI is a URL or a local file path.

    Args:
        uri: The URI to check

    Returns:
        True if it's a URL, False if it's a local path
    """
    return uri.startswith(("http://", "https://", "ftp://", "ftps://"))


def get_local_model_path(model_config: ModelConfig) -> Path:
    """
    Get the local path for a model, handling both URLs and local file paths.

    Args:
        model_config: Either a URL to download from or a local file path

    Returns:
        Path to the local model file
    """
    # Check if it's a local file path
    if model_config.model_path.startswith(("/", "./", "../", "~")) or (
        len(model_config.model_path) > 1 and model_config.model_path[1] == ":"
    ):
        # It's a local path (Unix absolute/relative or Windows drive path)
        return Path(model_config.model_path).expanduser().resolve()

    # Check if it's a URL
    if is_url(model_config.model_path):
        # It's a URL - use existing cache logic
        filename = f"{model_config.name}-{model_config.revision}.onnx"
        return get_local_model_dir() / filename

    # If it doesn't match URL patterns, assume it's a local path
    return Path(model_config.model_path).expanduser().resolve()


def batched(iterable: Iterable[Any], n: int) -> Iterable[tuple[Any, ...]]:
    """
    Batch data from the iterable into tuples of length n. The last batch may be shorter.

    This function emulates itertools.batched() which was introduced in Python 3.12.

    Args:
        iterable: Any iterable (list, string, generator, etc.)
        n: Batch size (positive integer)

    Yields:
        Tuples containing up to n elements from the iterable

    Raises:
        ValueError: If n is less than 1

    Examples:
        >>> list(batched('ABCDEFG', 3))
        [('A', 'B', 'C'), ('D', 'E', 'F'), ('G',)]

        >>> list(batched([1, 2, 3, 4, 5, 6, 7, 8, 9], 4))
        [(1, 2, 3, 4), (5, 6, 7, 8), (9,)]

        >>> list(batched(range(10), 2))
        [(0, 1), (2, 3), (4, 5), (6, 7), (8, 9)]
    """
    if n < 1:
        raise ValueError("n must be at least one")

    iterator = iter(iterable)
    while True:
        batch = tuple(itertools.islice(iterator, n))
        if not batch:
            break
        yield batch
