# Common Questions

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

The model outputs pixel values from 0-3 depending on which model was used ([see here](about.md#model-outputs)). Make
sure you visualize the outputs in your GIS using "unique values" classification, not a continuous color ramp.

**My outputs don't align with the input orthomosaic in my GIS**

Check that your orthomosaic has an assigned geographic coordinate system and try again.

---

*Still have questions?*

[Send us an email](mailto:habitat.mapper.support@hakai.org)
or [file a GitHub issue](https://github.com/HakaiInstitute/habitat-mapper/issues)
