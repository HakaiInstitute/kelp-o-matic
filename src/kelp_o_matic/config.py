"""Configuration models for segmentation processing and ONNX models."""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Any, Literal

from loguru import logger
from pydantic import AfterValidator, BaseModel, Field, PositiveInt

from kelp_o_matic.utils import _all_positive, _is_odd_or_zero, download_file_with_progress, get_local_model_path, is_url

if TYPE_CHECKING:
    from kelp_o_matic.reader import ImageReader


class ModelConfig(BaseModel):
    """ONNXModel configuration for ONNX semantic segmentation models."""

    cls_name: Annotated[str, "For dynamic loading of model class in registry"] = "kelp_o_matic.model.ONNXModel"
    name: Annotated[str, "The name of the model for the model registry"]
    description: Annotated[str | None, "Brief description of the model for the model registry"] = None
    revision: Annotated[str, "Model revision number. Date based versioning is preferred"]
    model_path: Annotated[str, "URL to download model from, or local file path"]
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

    reader_class_name: Annotated[
        str,
        "Fully qualified class name of the ImageReader to use (e.g., 'kelp_o_matic.reader.TIFFReader')",
    ] = "kelp_o_matic.reader.TIFFReader"
    reader_kwargs: Annotated[
        dict[str, Any],
        "Additional keyword arguments to pass to the reader constructor",
    ] = {}

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
                logger.success(
                    f"✓ Loaded model from: {local_path}",
                )
            else:
                logger.info(f"Downloading model to: {local_path}")
                try:
                    download_file_with_progress(self.model_path, local_path)
                    logger.success("✓ Model downloaded successfully")
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
                logger.warning(f"File does not have .onnx extension: {local_path}")

        return local_path

    def get_reader(self, input_path: str | Path) -> ImageReader:
        """Instantiate the configured ImageReader for the given input.

        Args:
            input_path: Path to the input file or directory

        Returns:
            An instantiated ImageReader configured for this model

        Raises:
            ValueError: If the reader class cannot be imported
            TypeError: If input_path is not compatible with the reader
        """
        # Dynamically import and instantiate the reader class
        try:
            module_name, class_name = self.reader_class_name.rsplit(".", 1)
            module = importlib.import_module(module_name)
            reader_class = getattr(module, class_name)
        except (ValueError, ImportError, AttributeError) as e:
            raise ValueError(f"Cannot load reader class '{self.reader_class_name}': {e}") from e

        # Prepare kwargs for reader initialization
        reader_init_kwargs = {
            **self.reader_kwargs,
        }

        # Instantiate the reader
        try:
            return reader_class(input_path, **reader_init_kwargs)
        except TypeError as e:
            # Filter out unknown kwargs for readers that don't accept them
            raise TypeError(f"Cannot instantiate {self.reader_class_name} with the provided arguments: {e}") from e


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
