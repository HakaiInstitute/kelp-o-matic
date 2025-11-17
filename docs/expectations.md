# Data Requirements

## Imagery Assumptions

All interfaces to Habitat-Mapper make the following assumptions about input images:

### 1. Data type is unsigned 8- or 16-bit integer.

This is often called `uint8` or `Byte` in software for unsigned 8-bit data, and
`uint16` for unsigned 16-bit data. If your data has a different numerical type,
you are very likely to get strange results as output.

If your image meets this condition, the pixels will be in the range 0 - 255
(for `uint8`) or 0 - 65535 (for `uint16`).

### 2. Channel order is Red, Green, Blue, then (optionally) Near Infrared.

The RGB channels are required, and the Near Infrared channel is optional. Extra channels
are ignored. The NIR channel is used when using the RGBI models, and will be ignored
when using the RGB models.

If you have a different channel order, you can use `-b` CLI flags (see [docs](cli.md))
to specify which band indices to use for each channel. For example, if your image has
Blue, Green, Red, and Near Infrared channels, you can use `-b 3 -b 2 -b 1 -b 4` flags
to specify the order of the channels. Similarly, if using the python library functions,
you can pass a list of band indices to the `band_order` parameter.

## Additional Recommendations

### 1. Define a *nodata* value in the image metadata.

This is not a strict requirement, but is helpful for skipping classification on blank
image areas to speed up processing.

!!! example
    For images with a black background, this value should be 0.
    For white backgrounds, it should be set to 255.

If there is no *nodata* value set, any part of the image that is completely black or
completely white is classified as "background" by Habitat-Mapper.

### 2. Use tiled GeoTIFFs.

Habitat-Mapper uses a moving window to classify images. This means that the image is
broken up into smaller chunks, and each chunk is classified separately. This is done
to reduce the amount of memory required to classify an image, and to allow for
classification of images that are larger than the amount of memory available on your
computer.

Tiled GeoTIFFs are a way of storing images that allows for efficient access to small
chunks of the image and will significantly speed up classification.
