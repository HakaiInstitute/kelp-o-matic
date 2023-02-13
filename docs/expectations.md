# Data Expectations

All interfaces to Kelp-O-Matic make the following assumptions about input images:

## 1. The data type must be unsigned 8-bit integer.

This is often called `uint8` or `Byte` in software. If your data has a different numerical type,
you are very likely to get strange results as output.

If your image meets this condition, all pixels will be in the range 0 - 255.

## 2. The first three channels of the image must be Red, Green, and Blue (in that order).

Additional channels are accepted and will simply be ignored.

## 3. The *nodata* value for your image should be defined in the geotiff metadata.

This is not a strict requirement, but is helpful for skipping classification on blank image areas to
speed up processing.

!!! example
    For images with a black background, this value should be 0.
    For white backgrounds, it should be set to 255.

If there is no *nodata* value set, any part of the image that is completely black or completely
white is classified as "background" by Kelp-O-Matic.
