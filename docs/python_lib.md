# Python Library Reference

The Python library provides access to the segmentation models and processing functionality through a high-level API.

## Core Components

The main components of the kelp-o-matic Python library are:

- **`ONNXModel`**: The core model class for running inference
- **`ModelConfig`**: Configuration class for model settings
- **`model_registry`**: Registry for discovering and loading available models

## Basic Usage

### Model Registry

The model registry provides easy access to all available models:

```python
from kelp_o_matic import model_registry

# List all available model names
model_names = model_registry.list_model_names()
print(model_names)  # ['kelp-rgb', 'kelp-rgbi', 'kelp-ps8b', 'mussel-rgb', 'mussel-gooseneck-rgb']

# Get the latest version of a model
model = model_registry['kelp-rgb']  # Gets latest version
# Or get a specific version
model = model_registry['kelp-rgb', '20240722']

# Get model metadata
latest_version = model_registry.get_latest_version('kelp-rgb')
all_models = model_registry.list_models()  # Returns [(name, version), ...]
```

### Processing Images

Once you have a model, you can process images using the model's `process` method:

```python
from kelp_o_matic import model_registry
from pathlib import Path

# Load a model for kelp segmentation
model = model_registry['kelp-rgb']

# Process an image
model.process(
    input_path=Path("./path/to/input_image.tif"),
    output_path=Path("./path/to/output_segmentation.tif"),
    crop_size=1024,
    batch_size=1,
    blur_kernel_size=5,
    morph_kernel_size=0,
    band_order=None
)
```

### Advanced Configuration

For more control over the processing, you can access the underlying configuration:

```python
from kelp_o_matic import model_registry, ModelConfig, ONNXModel
from pathlib import Path

# Access model configuration
model = model_registry['kelp-rgb']
print(f"Model description: {model.description}")
print(f"Expected input size: {model.input_size}")

# Create a model with custom configuration
custom_config = ModelConfig(
    model_path="path/to/custom/model.onnx",
    description="Custom model",
    # ... other configuration options
)
# see help(ModelConfig) for all options

custom_model = ONNXModel(custom_config)
custom_model.process(
    input_path=Path("./path/to/custom_input.tif"),
    output_path=Path("./path/to/custom_output.tif"),
    crop_size=2048,
    batch_size=2,
    blur_kernel_size=3,
    morph_kernel_size=1,
    band_order=[2, 1, 0]  # Example for reordering bands)
```

## Examples

### Kelp Segmentation

```python
from kelp_o_matic import model_registry

# Segment kelp in RGB drone imagery
model = model_registry['kelp-rgb']
model.process(
    input_path="./kelp_drone_image.tif",
    output_path="./kelp_segmentation.tif",
    crop_size=3200  # Use larger crop size for better results
)

# Segment kelp in 4-band RGB+NIR imagery
model = model_registry['kelp-rgbi']
model.process(
    input_path="./kelp_rgbi_image.tif",
    output_path="./kelp_segmentation.tif",
    crop_size=2048,
    band_order=[3, 2, 1, 0]  # Reorder bands from BGR+NIR to RGB+NIR
)
```

### Mussel Segmentation

```python
from kelp_o_matic import model_registry

# Segment mussels in RGB drone imagery
model = model_registry['mussel-rgb']
model.process(
    input_path="./mussel_drone_image.tif",
    output_path="./mussel_segmentation.tif",
    crop_size=1024
)

# Segment both mussels and gooseneck barnacles
model = model_registry['mussel-gooseneck-rgb']
model.process(
    input_path="./intertidal_image.tif",
    output_path="./mussel_gooseneck_segmentation.tif"
)
```

### Custom Processing Parameters

```python
from kelp_o_matic import model_registry

model = model_registry['kelp-rgb']
model.process(
    input_path="./input.tif",
    output_path="./output.tif",
    batch_size=4,          # Process 4 tiles at once
    crop_size=2048,        # Use 2048x2048 tiles
    blur_kernel_size=7,    # Apply stronger median blur
    morph_kernel_size=3,   # Apply morphological operations
    band_order=[3, 2, 1]   # Reorder BGR to RGB
)
```

!!! tip "Performance Tips"

    - Use the largest `crop_size` your system can handle (start with 3200 and work down)
    - Increase `batch_size` if you have sufficient GPU memory
    - Consider using `blur_kernel_size` and `morph_kernel_size` for post-processing
    - Use `band_order` to reorder bands if your imagery doesn't match the expected RGB(+NIR) order
