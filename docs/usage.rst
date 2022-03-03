Usage
=====

Input Expectations
------------------

All interfaces to ``hakai-segmentation`` tool make the following assumptions about input images:

1. The range of values in the input are in the interval [0, 255] and the datatype is Unsigned 8-bit (Often called "uint8" or "Byte" in various some software).
2. The first three channels of the image are the Red, Green, and Blue bands, in that order.
3. The *nodata* value for the image is defined in the geotiff metadata. (For images with a black background, this value should be 0, white background would be 255, etc.)


Command Line Interface
----------------------

The ``hakai-segmentation`` package includes one command line tool, ``kom``. It will be registered in the same Conda environment
that the ``hakai-segmentation`` package is installed to.

Usage Example
^^^^^^^^^^^^^

.. code-block:: console

    $ kom find-kelp ./some/image_with_kelp.tif ./some/place_to_write_output.tif

    $ kom find-mussels ./some/image_with_mussels.tif ./some/place_to_write_output.tif

API
^^^

.. code-block:: console

    $ kom --help

    NAME
        kom

    SYNOPSIS
        kom COMMAND

    COMMANDS
        COMMAND is one of the following:

         find-mussels
           Detect mussels in source image and output the resulting classification raster to dest.

         find-kelp
           Detect kelp in source image and output the resulting classification raster to dest.

Get help with a specific sub command:

.. code-block:: console

    $ kom find-kelp --help

    NAME
        kom find-kelp - Detect kelp in source image and output the resulting classification raster to dest.

    SYNOPSIS
        kom find-kelp SOURCE DEST <flags>

    DESCRIPTION
        Detect kelp in source image and output the resulting classification raster to dest.

    POSITIONAL ARGUMENTS
        SOURCE
            Type: str
            Input image with Byte data type.
        DEST
            Type: str
            File path location to save output to.

    FLAGS
        --crop_size=CROP_SIZE
            Type: int
            Default: 256
            The size of cropped image square run through the segmentation model.
        --padding=PADDING
            Type: int
            Default: 128
            The number of context pixels added to each side of the cropped image squares.
        --batch_size=BATCH_SIZE
            Type: int
            Default: 2
            The batch size of cropped image sections to process together.

    NOTES
        You can also use flags syntax for POSITIONAL ARGUMENTS



Python Library
--------------

The Python library provide two functions that run classification on an input image and write data to an output location.

Usage Example
^^^^^^^^^^^^^

.. code-block:: python

    import hakai_segmentation
    hakai_segmentation.find_kelp("./path/to/kelp_image.tif", "./path/to/output_file_to_write.tif")

API
^^^

.. automodule:: hakai_segmentation
    :members: