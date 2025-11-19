# Model Outputs

Each of the Habitat-Mapper models outputs a mask raster with integer pixel values that
represent the following classes:

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
