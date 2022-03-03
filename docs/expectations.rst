Data Expectations
=================

All interfaces to ``hakai-segmentation`` tool make the following assumptions about input images:

1. The range of values in the input are in the interval [0, 255] and the datatype is Unsigned 8-bit (Often called "uint8" or "Byte" in software).
2. The first three channels of the image are the Red, Green, and Blue bands, in that order. Extra channels are fine, but will be ignored.
3. The *nodata* value for the image is defined in the geotiff metadata.
   (For images with a black background, this value should be 0, white background would be 255, etc.). This is not a hard requirement,
   but it speeds up processing considerably if these regions are known and do not need to be classified.
