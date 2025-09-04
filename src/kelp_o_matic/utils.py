"""Utilities and helper functions for the Kelp-O-Matic package."""

from __future__ import annotations

import itertools
import os
import shutil
import site
import sys
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np
import onnxruntime as ort
import platformdirs
import requests
from loguru import logger
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TransferSpeedColumn,
)
from rich.prompt import Confirm

if TYPE_CHECKING:
    from collections.abc import Iterable

    from kelp_o_matic.config import ModelConfig


def download_file_with_progress(url: str, out_path: Path, timeout: tuple[int, int] = (15, 120)) -> None:
    """Download the file at url to out_path."""
    try:
        response = requests.get(url, stream=True, timeout=timeout)
        response.raise_for_status()

        # Get total file size
        total_size = int(response.headers.get("content-length", 0))

        # Download with progress to temp location
        with (
            tempfile.TemporaryDirectory() as tmp_dir,
            open(tmp_out := Path(tmp_dir) / out_path.name, "wb") as f,
            Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}"),
                BarColumn(),
                DownloadColumn(),
                TransferSpeedColumn(),
                console=None,  # Use default console
            ) as progress,
        ):
            task = progress.add_task(f"Downloading {out_path.name}", total=total_size)
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                progress.update(task, advance=len(chunk))

            # Move the completed file to the proper location
            shutil.move(tmp_out, out_path)
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        logger.error(f"Download timed out: {e}")

        if Confirm.ask("Do you want to retry the download?"):
            logger.trace("Retrying download...")
            # Retry with longer timeout
            download_file_with_progress(url, out_path, timeout=(timeout[0] * 2, timeout[1] * 2))
    except requests.exceptions.RequestException as e:
        logger.error(f"Download failed: {e}")


def get_ort_providers() -> list[str]:
    """Get the ORT provider list for the current system and installation.

    Returns:
       list[str]: List of available ONNX Runtime providers in order of preference.
    """
    available_providers = ort.get_available_providers()
    providers = []

    if "NvTensorRtRtxExecutionProvider" in available_providers:
        providers.append("NvTensorRtRtxExecutionProvider")

    if "CUDAExecutionProvider" in available_providers:
        providers.append("CUDAExecutionProvider")

    providers.append("CPUExecutionProvider")
    return providers


def get_local_model_dir() -> Path:
    """Get the path to the directory containing cached models.

    Returns:
        Path: The path to the local model directory, creating it if it doesn't exist.
    """
    cache_dir = platformdirs.user_cache_dir(appname="kelp_o_matic", appauthor="hakai")
    model_dir = Path(cache_dir) / "models"
    model_dir.mkdir(exist_ok=True, parents=True)
    return model_dir


def is_url(uri: str) -> bool:
    """Check if a URI is a URL or a local file path.

    Args:
        uri: The URI to check

    Returns:
        True if it's a URL, False if it's a local path

    """
    return uri.startswith(("http://", "https://", "ftp://", "ftps://"))


def get_local_model_path(model_config: ModelConfig) -> Path:
    """Get the local path for a model, handling both URLs and local file paths.

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
    """Batch data from the iterable into tuples of length n. The last batch may be shorter.

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


def setup_cuda_paths() -> None:
    """Add CUDA DLL directories to PATH on Windows."""
    if sys.platform != "win32":
        return

    # Find all NVIDIA bin directories in site-packages
    dll_paths = []
    for site_dir in site.getsitepackages():
        nvidia_path = Path(site_dir) / "nvidia"
        if nvidia_path.exists():
            # Find all bin directories under nvidia/*
            dll_paths.extend(str(p) for p in nvidia_path.glob("*/bin") if p.is_dir())

    if not dll_paths:
        return

    # Add to PATH environment variable
    os.environ["PATH"] = ";".join(dll_paths) + ";" + os.environ.get("PATH", "")

    # Add as DLL directories for Python 3.8+
    if hasattr(os, "add_dll_directory"):
        for path in dll_paths:
            try:
                os.add_dll_directory(path)
            except OSError:
                pass


def _is_odd_or_zero(value: int) -> int:
    if value == 0:
        return value
    if value % 2 == 0:
        raise ValueError(f"{value} is not an odd number")
    return value


def _all_positive(value: list[int]) -> list[int]:
    if any(v <= 0 for v in value):
        raise ValueError("All values must be positive integers")
    return value


def softmax(x: np.ndarray, axis: int = 0, keepdims: bool = False) -> np.ndarray:
    """Apply softmax function to ndarray x.

    Args:
        x: A numpy array
        axis: Axis along which to apply the softmax function
        keepdims: Whether to keep dimensions or not

    Returns:
        A numpy array representing the softmax output
    """
    return np.exp(x) / np.sum(np.exp(x), axis=axis, keepdims=keepdims)


def sigmoid(x: np.ndarray) -> np.ndarray:
    """Apply the sigmoid activation function to array x.

    Args:
        x: A numpy array

    Returns:
        A numpy array of the sigmoid output
    """
    return 1 / (1 + np.exp(-x))
