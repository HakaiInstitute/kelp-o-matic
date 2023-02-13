# Data Expectations

All interfaces to Kelp-O-Matic make the following assumptions about input images:

## 1. The datatype is unsigned 8-bit integer

This is often called "uint8" or "Byte" in software. If your data has a different numerical data type,
you are very likely to get strange results as output.

The range of values in the input should thus be in the range [0, 255].

## 2. The first three channels of the image are the Red, Green, and Blue, in that order.

Additional channels after these are fine and simply ignored.

## 3. The *nodata* value should be defined in the geotiff metadata.

This is not strictly required, but is helpful for skipping classification on blank image areas to save time.
For images with a black background, this value should be 0. For white backgrounds *nodata* should be set to 255.

If no *nodata* value is set, any part of the image that is completely black or completely white is ignored.