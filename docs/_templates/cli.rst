CLI Documentation
=================

To run the CLI:
::

    $ kom find-kelp ./some/image_with_kelp.tif ./some/place_to_write_output.tif

Get help:
::

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
::

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
