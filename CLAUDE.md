# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Habitat-Mapper (formerly Kelp-O-Matic) is an AI-powered habitat segmentation tool that uses ONNX models to identify marine habitats (kelp, mussels) in aerial/drone imagery. The tool processes large GeoTIFF files using a tiled inference approach with overlapping windows to handle edge effects.

Package name: `habitat-mapper`
CLI command: `hab`
Documentation: https://habitat-mapper.readthedocs.io

## Development Commands

### Environment Setup
This project uses `uv` for dependency management:

```bash
# Install dependencies (includes CoreML support on macOS)
uv sync

# Install with NVIDIA GPU acceleration (Windows/Linux)
uv sync --extra gpu

# Install with dev dependencies
uv sync --dev

# Install with specific dependency groups
uv sync --group docs
uv sync --group examples
```

**Hardware Acceleration:**
- **macOS:** CoreML execution provider automatically enabled (Apple Silicon & Intel with GPU)
- **Windows/Linux:** CUDA/TensorRT support via `[gpu]` extra (requires NVIDIA GPU + CUDA/cuDNN)
- **All platforms:** Falls back to CPU if no accelerator available

### Testing
```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_NumpyMemoryRegister.py

# Run with verbose output
uv run pytest -v
```

### Linting and Formatting
```bash
# Run ruff linter (check only)
uv run ruff check

# Run ruff linter with auto-fix
uv run ruff check --fix

# Format code
uv run ruff format

# Type checking with mypy
uv run mypy src/habitat_mapper
```

### Pre-commit Hooks
```bash
# Install pre-commit hooks
uv run pre-commit install

# Run pre-commit on all files
uv run pre-commit run --all-files
```

### Documentation
```bash
# Serve documentation locally
uv run mkdocs serve

# Build documentation
uv run mkdocs build
```

### CLI Usage
```bash
# List available models
uv run hab models

# List model revisions
uv run hab revisions --model kelp-rgb

# Segment an image
uv run hab segment --model kelp-rgb --input image.tif --output result.tif

# Clear model cache
uv run hab clean
```

## Architecture Overview

### Core Processing Pipeline

The segmentation pipeline follows this flow:

1. **Model Registry** (`registry.py`): Loads model configurations from `src/habitat_mapper/configs/*.json` and instantiates appropriate model classes dynamically
2. **Image Reader** (`reader.py`): Abstract interface for reading image tiles; currently implements `TIFFReader` for GeoTIFF files
3. **Image Processor** (`processing.py`): Orchestrates tiled processing with overlapping windows
4. **ONNX Model** (`model.py`): Handles model inference, preprocessing, and postprocessing
5. **Windowing System** (`hann.py`): Implements Bartlett-Hann windowing to reduce edge artifacts from tiled processing

### Execution Provider Selection

The `get_ort_providers()` function in `utils.py` automatically selects optimal ONNX Runtime execution providers based on system capabilities, in order of preference:
1. **NvTensorRtRtxExecutionProvider** (NVIDIA TensorRT on RTX GPUs)
2. **CUDAExecutionProvider** (NVIDIA CUDA GPUs - requires `[gpu]` extra)
3. **CoreMLExecutionProvider** (Apple Silicon & Intel Macs with GPU - automatic)
4. **CPUExecutionProvider** (fallback for all systems)

ONNX Runtime will automatically use the first available provider in the list.

### Model Configuration System

Models are defined via JSON config files in `src/habitat_mapper/configs/`. Each config specifies:
- Model class to use (supports custom model classes via `cls_name`)
- Model revision (calendar versioning preferred: YYYYMMDD)
- Dependencies (URLs or local paths) that are auto-downloaded and cached
- Preprocessing parameters (normalization, mean, std)
- Activation function (sigmoid/softmax)
- Reader class and auxiliary data requirements

Example config structure:
```json
{
  "cls_name": "habitat_mapper.model.ONNXModel",
  "name": "kelp-rgb",
  "revision": "20240722",
  "dependencies": ["https://example.com/model.onnx"],
  "model_filename": "model.onnx",
  "normalization": "standard",
  "mean": [0.485, 0.456, 0.406],
  "std": [0.229, 0.224, 0.225]
}
```

### Tiled Processing Strategy

Large images are processed in overlapping tiles to manage memory:
- Default tile size: 1024×1024 pixels (can be overridden by model config)
- Default stride: 50% of tile size (creates 50% overlap)
- Overlap regions are blended using Bartlett-Hann windowing weights
- The `NumpyMemoryRegister` class accumulates weighted logits across overlapping tiles
- Post-processing (median blur, morphological operations) is applied after inference

### Legacy Model Support

The codebase maintains backward compatibility with multi-model kelp detection:
- `LegacyKelpRGBModel` and `LegacyKelpRGBIModel` in `model.py`
- These classes handle the old two-stage approach (presence detection + species classification)
- New models should use the standard `ONNXModel` class with single-stage detection

### Custom Reader Pattern

Models can specify custom `ImageReader` implementations via `reader_class_name` in config:
- Readers must inherit from `ImageReader` abstract class
- Auxiliary data (bathymetry, substrate) can be injected via `reader_kwargs`
- Dependency auto-injection: Files matching "bathymetry" or "substrate" in dependencies are automatically passed to readers

## Code Style

- Ruff configuration in `pyproject.toml` enforces line length of 120 characters
- Google-style docstrings required (enforced by ruff DOC rules)
- Type hints required (enforced by ruff ANN rules)
- Tests exempt from docstring requirements (see `per-file-ignores`)

## Important Patterns

### Adding a New Model

1. Create ONNX model file and upload to accessible URL (HuggingFace or S3)
2. Create JSON config in `src/habitat_mapper/configs/{name}_{revision}.json`
3. If standard preprocessing/postprocessing suffices, use `cls_name: "habitat_mapper.model.ONNXModel"`
4. If custom processing needed, create new model class inheriting from `ONNXModel` and override `_preprocess` or `_postprocess`
5. Model will be auto-registered on import via `ModelRegistry.from_config_dir()`

### Adding a New Reader

1. Create class inheriting from `ImageReader` in `reader.py`
2. Implement required abstract properties: `height`, `width`, `num_bands`, `dtype`
3. Implement `read_window()` method with support for `band_order`, `boundless`, and `fill_value`
4. Implement `close()` method for resource cleanup
5. Set `reader_class_name` in model config to use custom reader

### Model Caching

- Models and dependencies are cached in `platformdirs.user_cache_dir(appname="habitat_mapper")`
- On macOS: `~/Library/Caches/habitat_mapper/models/`
- On Linux: `~/.cache/habitat_mapper/models/`
- Cache structure: `{model_name}/{revision}/{files}`
- Use `hab clean` to clear cache

## Testing

Tests are located in `tests/`:
- `test_NumpyMemoryRegister.py`: Tests windowing and overlap handling
- `test_window_generation_coverage.py`: Tests tile generation and coverage

CI runs tests on Python 3.10-3.13 across Ubuntu, Windows, and macOS.

## Migration from Kelp-O-Matic

The project was renamed from "Kelp-O-Matic" to "Habitat-Mapper" in v0.14.0:
- Deprecated commands: `hab find-kelp`, `hab find-mussels` (use `hab segment` instead)
- Old cache location at `~/.cache/kelp_o_matic/` is still checked during `hab clean`
- CLI moved from `click` to `cyclopts` framework
- Multi-model approach replaced with single-model approach for new models
