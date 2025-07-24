from __future__ import annotations

import hashlib
from pathlib import Path

import onnxruntime as ort
import platformdirs
import requests
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TransferSpeedColumn,
)


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


def get_local_model_path(model_uri: str) -> Path:
    """
    Get the local path for a model, handling both URLs and local file paths.

    Args:
        model_uri: Either a URL to download from or a local file path

    Returns:
        Path to the local model file
    """
    # Check if it's a local file path
    if model_uri.startswith(("/", "./", "../", "~")) or (
        len(model_uri) > 1 and model_uri[1] == ":"
    ):
        # It's a local path (Unix absolute/relative or Windows drive path)
        return Path(model_uri).expanduser().resolve()

    # Check if it's a URL
    if is_url(model_uri):
        # It's a URL - use existing cache logic
        url_hash = hashlib.md5(model_uri.encode()).hexdigest()[:8]
        filename = f"{Path(model_uri).stem}_{url_hash}.onnx"
        return get_local_model_dir() / filename

    # If it doesn't match URL patterns, assume it's a local path
    return Path(model_uri).expanduser().resolve()
