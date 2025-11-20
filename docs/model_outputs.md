# Model Outputs

Each of the Habitat-Mapper models outputs a mask raster with integer pixel values that
represent the following classes.

!!! warning "Visualizing Outputs Correctly"
    **Output images may appear completely black when first opened** because pixel values are 0-3.

    To view them correctly in GIS software:

    - **Use "Unique Values" or "Categorical" classification**, NOT a continuous color ramp
    - **In ArcGIS Pro:** Right-click layer → Symbology → Unique Values → Field: Value
    - **In QGIS:** Right-click layer → Properties → Symbology → Paletted/Unique Values → Classify

    If you still see a black image, check that values 0, 1, 2, 3 are present in the classification table.

### Kelp (RGB and RGBI models)

These are the outputs from the `hab segment kelp-rgb` and `hab segment kelp-rgbi` routines:

| Output value | Class                               |
|-------------:|-------------------------------------|
|        **0** | Background (water, other features)  |
|        **1** | *Macrocystis pyrifera* (Giant kelp) |
|        **2** | *Nereocystis luetkeana* (Bull kelp) |

### Kelp (PS8B model)

These are the outputs from the `hab segment kelp-ps8b` routine:

| Output value | Class                               |
|-------------:|-------------------------------------|
|        **0** | Background (water, other features)  |
|        **1** | Kelp                                |

### Mussels

These are the outputs from the `hab segment mussel-rgb` and `hab segment mussel-gooseneck-rgb` routines:

| Output value | Class                                            |
|-------------:|--------------------------------------------------|
|        **0** | Background (water, rocks, other substrates)      |
|        **1** | Mussels (typically blue mussels, *Mytilus* spp.) |
|        **2** | Gooseneck barnacles (*Pollicipes* spp.)          |
