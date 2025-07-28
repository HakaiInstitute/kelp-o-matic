from __future__ import annotations

from functools import cached_property
from pathlib import Path

import numpy as np
import onnxruntime as ort

from kelp_o_matic.config import ModelConfig
from kelp_o_matic.utils import get_ort_providers

ort.set_default_logger_severity(3)  # Set to 3=ERROR


class ONNXModel:
    def __init__(self, config: ModelConfig):
        self.cfg = config
        self.__ort_sess = None

    @classmethod
    def from_json_config(cls, config_path: str):
        config = ModelConfig.model_validate_json(open(config_path).read())
        cls(config=config)

    @property
    def _ort_sess(self) -> ort.InferenceSession:
        """Load and cache the ONNX Runtime session."""
        if self.__ort_sess is not None:
            return self.__ort_sess

        # Get local model path (handles download if needed)
        local_model_path = self.cfg.local_model_path

        # Load CUDA and CUDNN DLLs
        ort.preload_dlls(directory="")

        # Load appropriate ONNX providers for OS capabilities
        providers = get_ort_providers()

        # Load the model
        self.__ort_sess = ort.InferenceSession(
            str(local_model_path), providers=providers
        )
        self.__ort_sess.enable_fallback()

        return self.__ort_sess

    @cached_property
    def _input_name(self) -> str:
        """
        Get the input name for the model.
        Returns:
            Input name as a string.
        """
        inputs = self._ort_sess.get_inputs()
        if not inputs:
            raise ValueError("No inputs found in the ONNX model.")
        return inputs[0].name

    @cached_property
    def input_tile_size(self) -> int | None:
        """
        Get the input tile size from the model configuration.
        Returns:
            Tuple of (height, width) or None if not specified.
        """
        inputs = self._ort_sess.get_inputs()
        if not inputs:
            raise ValueError("No inputs found in the ONNX model.")
        input_shape = inputs[0].shape
        if len(input_shape) < 3:
            raise ValueError(
                "ONNX model input shape must have at least 3 dimensions (batch, channels, height, width)."
            )

        h, w = input_shape[2], input_shape[3]

        if isinstance(h, str) and isinstance(w, str):
            return None  # Dynamic shape, no fixed tile size

        elif isinstance(h, int) and h > 0:
            if h == w or isinstance(w, str):
                return h

        elif isinstance(w, int) and w > 0:
            if w == h or isinstance(h, str):
                return w

        msg = f"Model input shape must be square or dynamic (e.g., [1, 8, 224, 224]). Bad model input shape: {input_shape}"
        raise ValueError(msg)

    def _preprocess(self, batch: np.ndarray) -> np.ndarray:
        """
        Preprocess the input image according to the model's configuration.
        """
        batch = batch.astype(np.float32) / self.cfg.max_pixel_value

        if self.cfg.normalization is None:
            return batch

        elif self.cfg.normalization == "standard":
            # Expand dims for broadcasting
            mean = np.array(self.cfg.mean)[None, :, None, None]
            std = np.array(self.cfg.std)[None, :, None, None]
            return (batch - mean) / std

        elif self.cfg.normalization == "min_max":
            return (batch - batch.min(axis=0)) / (batch.max(axis=0) - batch.min(axis=0))

        elif self.cfg.normalization == "min_max_per_channel":
            return (batch - batch.min(axis=(0, 1), keepdims=True)) / (
                batch.max(axis=(0, 1), keepdims=True)
                - batch.min(axis=(0, 1), keepdims=True)
            )

        else:
            raise NotImplementedError("Normalization method not implemented.")

    def postprocess(self, batch: np.ndarray) -> np.ndarray:
        """
        Postprocess the output to get class label from logits or probs.

        Supports batch inputs and single samples.
        """
        undo_batch = False
        if len(batch.shape) == 3:
            undo_batch = True
            # Expand single class dim
            batch = np.expand_dims(batch, axis=0)

        if self.cfg.activation == "softmax":
            batch = np.exp(batch) / np.sum(np.exp(batch), axis=1, keepdims=True)
        elif self.cfg.activation == "sigmoid":
            batch = 1 / (1 + np.exp(-batch))

        if batch.shape[1] == 1:
            # If single dim class, make into binary tensor
            batch = np.concat([1 - batch, batch], axis=1)

        batch = np.argmax(batch, axis=1, keepdims=False).astype(np.uint8)

        if undo_batch:
            batch = batch.squeeze(0)

        return batch

    def predict(self, batch: np.ndarray) -> np.ndarray:
        """
        Run inference on a batch of image tiles.

        Args:
            batch: Input batch with shape [batch_size, channels, height, width]

        Returns:
            Predictions with shape [batch_size, height, width]
        """
        batch = self._preprocess(batch)

        batch = self._ort_sess.run(
            None, {f"{self._input_name}": batch.astype(np.float32)}
        )
        return batch[0]

    def process(
        self,
        input_path: str | Path,
        output_path: str | Path,
        *,
        batch_size: int = 1,
        crop_size: int | None = None,
        blur_kernel_size: int = 5,
        morph_kernel_size: int = 0,
        band_order: list[int] | None = None,
    ) -> None:
        """
        Process an image using the default tiled processing strategy.

        This is a convenience method that creates an ImageProcessor with
        TiledProcessingStrategy and processes the image.

        Args:
            input_path: Path to input raster
            output_path: Path to output segmentation raster
            batch_size: Batch size for processing
            crop_size: Tile size for processing (uses model's preferred size if None)
            blur_kernel_size: Size of median blur kernel (must be odd)
            morph_kernel_size: Size of morphological kernel (0 to disable)
        """
        # Import here to avoid circular imports
        from kelp_o_matic.processing import ImageProcessor

        processor = ImageProcessor(self)
        processor.process(
            input_path=input_path,
            output_path=output_path,
            batch_size=batch_size,
            crop_size=crop_size,
            blur_kernel_size=blur_kernel_size,
            morph_kernel_size=morph_kernel_size,
            band_order=band_order,
        )
