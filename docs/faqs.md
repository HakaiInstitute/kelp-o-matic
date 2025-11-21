# Common Questions

## Getting Started

**Do I need to activate the environment every time I use Habitat-Mapper?**

Yes. The virtual environment must be activated every time you open a new terminal window. This keeps Habitat-Mapper's dependencies separate from your system Python. You'll know the environment is active when you see `(habitat-env)` (or your environment name) at the beginning of your terminal prompt.

=== "Windows"
    ```powershell
    .\habitat-env\Scripts\activate
    ```

=== "MacOS/Linux"
    ```bash
    source ./habitat-env/bin/activate
    ```

See [Installation](installation.md) for details.

**How long does processing take?**

Processing time varies widely depending on several factors:

- **Image size:** Larger orthomosaics take longer to process
- **Model choice:** Different models have different computational requirements
- **Hardware:** GPU processing is significantly faster than CPU-only processing
- **Crop size:** Larger crop sizes take more time per tile but may require fewer tiles overall

There's no single answer—times can range from seconds to hours depending on your specific setup and data. The tool will display progress as it processes tiles.

**Can I process multiple images at once?**

The CLI processes one image at a time. For batch processing, use the [Python API](python_lib.md) to write a script that loops through multiple files. Here's a simple example:

```python
from habitat_mapper import model_registry
from pathlib import Path

model = model_registry['kelp-rgb']
input_dir = Path("./orthomosaics")

for img_path in input_dir.glob("*.tif"):
    output_path = Path(f"./outputs/{img_path.stem}_mask.tif")
    model.process(img_path=img_path, output_path=output_path)
```

## Installation and Setup

**What kind of computer do I need to run this?**

The tool will run on any computer that can run Python. An Nvidia CUDA-compatible GPU will improve performance but is not
required.

**During installation, I'm getting errors about GDAL**

These errors typically occur when your uv virtual environment is located on a different disk than where uv itself is
installed (usually the C: drive on Windows). When uv creates an environment on a network drive or secondary disk, it can
fail to properly link the system libraries that GDAL and rasterio depend on.

**Solution:** Create your uv environment on your local C: drive instead. Once created and activated, you can navigate to
wherever your data is stored (including network drives) and run `hab segment` commands normally—the environment location
only matters during installation, not during use.

## Input Data

**What resolution should my data be?**

Habitat-Mapper works best on imagery with 1-10cm pixel resolution; 5cm is optimal. For the PlanetScope model, use 3m or
better resolution with surface reflectance bands.

**Will Habitat-Mapper work with data from outside western North America?**

While Habitat-Mapper was trained primarily on data from British Columbia and California, it has shown good performance
in other regions like Alaska and Patagonia. If the model isn't performing well with your data, please contact us—we're
interested in expanding its capabilities and may be able to optimize it for your region.

**Can I substitute different sensor bands (e.g., use a different band instead of red)?**

No. The model is specifically trained on the relationships between RGB bands (and NIR for certain models) to detect kelp
and mussels. Substituting bands will not work.

## Running the Tool

**I'm getting warnings when I run the tool. Should I worry?**

No. Warnings provide optional suggestions to help optimize processing speed. You can safely proceed, but addressing them
may improve performance.

**The output image is all black. Did it find anything?**

The model outputs pixel values from 0-3 depending on which model was used ([see here](model_outputs.md)). Make
sure you visualize the outputs in your GIS using "unique values" classification, not a continuous color ramp.

**My outputs don't align with the input orthomosaic in my GIS**

Check that your orthomosaic has an assigned geographic coordinate system and try again.

---

*Still have questions?*

[Send us an email](mailto:habitat.mapper.support@hakai.org)
or [file a GitHub issue](https://github.com/HakaiInstitute/habitat-mapper/issues)
