"""Configuration models for segmentation processing and ONNX models."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Literal

from loguru import logger
from pydantic import AfterValidator, BaseModel, Field, PositiveInt

from kelp_o_matic.utils import (
    _all_positive,
    _is_odd_or_zero,
    download_dependencies,
)


class ModelConfig(BaseModel):
    """ONNXModel configuration for ONNX semantic segmentation models."""

    cls_name: Annotated[str, "For dynamic loading of model class in registry"] = "kelp_o_matic.model.ONNXModel"
    name: Annotated[str, "The name of the model for the model registry"]
    description: Annotated[str | None, "Brief description of the model for the model registry"] = None
    revision: Annotated[str, "Model revision number. Date based versioning is preferred"]
    dependencies: Annotated[
        list[str],
        "List of files to download (URLs or local paths). Downloaded to model-specific cache subdirectory.",
    ]
    model_filename: Annotated[
        str,
        "Name of the file in dependencies list that is the ONNX model (e.g., 'model.onnx')",
    ]
    input_channels: PositiveInt = 3
    activation: (
        Annotated[
            Literal["sigmoid", "softmax"],
            "Final activation to apply to model outputs. "
            "If None, it is assumed that the output of the ONNX model are probabilities",
        ]
        | None
    ) = None

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

    max_pixel_value: Annotated[
        float | Literal["auto"],
        "Value to scale input pixels by prior to normalization, or 'auto' to infer from the image datatype.",
    ] = "auto"
    default_output_value: Annotated[
        int,
        (
            "Value the model should output for tiles that are all the same colour (used to speed up processing by "
            "skipping background areas)"
        ),
    ] = 0
    nodata_value: Annotated[int, "The nodata value for the output raster"] = 0

    @property
    def local_dependency_paths(self) -> dict[str, Path]:
        """Get local paths to all dependency files.

        Downloads dependencies in parallel if they are URLs and not yet cached.

        Returns:
            Dict mapping filenames to local paths for all dependencies
        """
        dep_paths = download_dependencies(self)
        # Create a dict mapping filename to path for easy lookup
        return {path.name: path for path in dep_paths}

    @property
    def local_model_path(self) -> Path:
        """Get the local path to the ONNX model file.

        Downloads all dependencies (including the model) if needed.

        Returns:
            Path to the local ONNX model file

        Raises:
            ValueError: If model_filename not found in dependencies
        """
        # Download all dependencies (this will be cached on subsequent calls)
        dep_paths = self.local_dependency_paths

        # Find the model file by name
        if self.model_filename not in dep_paths:
            raise ValueError(
                f"Model file '{self.model_filename}' not found in dependencies. "
                f"Available files: {list(dep_paths.keys())}"
            )

        model_path = dep_paths[self.model_filename]

        # Validate it's an ONNX file
        if not model_path.suffix.lower() == ".onnx":
            logger.warning(f"Model file does not have .onnx extension: {model_path}")

        return model_path


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
        dependencies=[
            "https://hakai-triton-models-bf426c24.s3.us-east-1.amazonaws.com/kelp_segmentation_ps8b_model/1/model.onnx"
        ],
        model_filename="model.onnx",
        normalization="standard",
        activation=None,
        mean=(1720.0, 1715.0, 1913.0, 2088.0, 2274.0, 2290.0, 2613.0, 3970.0),
        std=(747.0, 698.0, 739.0, 768.0, 849.0, 868.0, 849.0, 914.0),
        max_pixel_value=1.0,
    )

    with open(Path("./default_configs") / f"{config.name}.json", "w") as f:
        f.write(config.model_dump_json(indent=4, exclude_none=True))
