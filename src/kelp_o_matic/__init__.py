"""Kelp-O-Matic: A tool for segmenting audio files using machine learning models."""

from kelp_o_matic.config import ModelConfig
from kelp_o_matic.main import clean, models, revisions, segment
from kelp_o_matic.model import ONNXModel
from kelp_o_matic.registry import model_registry

__all__ = [
    "ModelConfig",
    "ONNXModel",
    "clean",
    "model_registry",
    "models",
    "revisions",
    "segment",
]
