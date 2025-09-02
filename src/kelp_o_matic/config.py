"""Configuration models for segmentation processing and ONNX models."""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, Field, PositiveInt

from kelp_o_matic.utils import (
    _all_positive,
    _is_odd_or_zero,
    console,
    download_file_with_progress,
    get_local_model_path,
    is_url,
)


class ModelConfig(BaseModel):
    """ONNXModel configuration for ONNX semantic segmentation models."""

    name: str
    description: str | None = None
    revision: str
    model_path: str  # URL to download model from, or local file path
    input_channels: PositiveInt = 3
    activation: Literal["sigmoid", "softmax"] | None = None

    normalization: (
        Literal[
            "standard",
            "image",
            "image_per_channel",
            "min_max",
            "min_max_per_channel",
        ]
        | None
    ) = "standard"
    mean: tuple[float, ...] | None = (0.485, 0.456, 0.406)
    std: tuple[float, ...] | None = (0.229, 0.224, 0.225)
    max_pixel_value: float | Literal["auto"] = "auto"  # Value to scale input pixels by prior to normalization
    default_output_value: int = 0  # Value to use as default output (e.g. for black areas in image)

    @property
    def local_model_path(self) -> Path:
        """Get the local path to the ONNX model file.

        For URLs: Downloads the model to cache if not already present.
        For local paths: Returns the path directly after validation.

        Returns:
            Path to the local ONNX model file

        Raises:
            FileNotFoundError: If local file doesn't exist
            RuntimeError: If download fails
            ValueError: If the local path is not a file or does not have .onnx extension
        """
        local_path = get_local_model_path(self)

        # If it's a URL, handle download
        if is_url(self.model_path):
            if local_path.exists():
                console.print(
                    f"[green]✓ Loaded model from: {local_path}[/green]",
                )
            else:
                console.print(f"[blue]Downloading model to: {local_path}[/blue]")
                try:
                    download_file_with_progress(self.model_path, local_path)
                    console.print("[green]✓ Model downloaded successfully[/green]")
                except Exception as e:
                    raise RuntimeError(
                        f"Failed to download model from {self.model_path}: {e}",
                    )
        else:
            # It's a local path - validate it exists
            if not local_path.exists():
                raise FileNotFoundError(f"Local model file not found: {local_path}")
            if not local_path.is_file():
                raise ValueError(f"Path is not a file: {local_path}")
            if not local_path.suffix.lower() == ".onnx":
                warnings.warn(f"File does not have .onnx extension: {local_path}")

        return local_path


class ProcessingConfig(BaseModel):
    """Configuration for image processing parameters."""

    crop_size: Annotated[int, Field(gt=0, multiple_of=2)]
    band_order: Annotated[list[int], Field(min_length=1), AfterValidator(_all_positive)]
    batch_size: PositiveInt = 1
    blur_kernel_size: Annotated[int, Field(ge=0), AfterValidator(_is_odd_or_zero)] = 5
    morph_kernel_size: Annotated[int, Field(ge=0), AfterValidator(_is_odd_or_zero)] = 0

    @property
    def stride(self) -> int:
        """Calculate the stride based on tile size and 50% overlap."""
        return int(self.crop_size * 0.5)

    @property
    def apply_morphological_ops(self) -> bool:
        """Whether to apply morphological operations."""
        return self.morph_kernel_size > 1

    @property
    def apply_median_blur(self) -> bool:
        """Whether to apply median blur."""
        return self.blur_kernel_size > 1


if __name__ == "__main__":
    config = ModelConfig(
        name="kelp_ps8b",
        revision="20250626",
        description="Kelp segmentation model for 8-band PlanetScope imagery.",
        model_path="https://hakai-triton-models-bf426c24.s3.us-east-1.amazonaws.com/kelp_segmentation_ps8b_model/1/model.onnx",
        normalization="standard",
        activation=None,
        mean=(1720.0, 1715.0, 1913.0, 2088.0, 2274.0, 2290.0, 2613.0, 3970.0),
        std=(747.0, 698.0, 739.0, 768.0, 849.0, 868.0, 849.0, 914.0),
        max_pixel_value=1.0,
    )

    with open(Path("./default_configs") / f"{config.name}.json", "w") as f:
        f.write(config.model_dump_json(indent=4, exclude_none=True))
