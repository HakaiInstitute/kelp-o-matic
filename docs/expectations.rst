Data Expectations
=================

All interfaces to ``hakai-segmentation`` tool make the following assumptions about input images:

1. The range of values in the input are in the interval [0, 255] and the datatype is Unsigned 8-bit (Often called "uint8" or "Byte" in software).
2. The first three channels of the image are the Red, Green, and Blue bands, in that order. Extra channels are fine and will be ignored.
3. The *nodata* value should be defined in the geotiff metadata for fastest processing times.
   (For images with a black background, this value should be 0, white background would be 255, etc.).
