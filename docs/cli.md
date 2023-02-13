# Command Line Reference

The `kelp-o-matic` package includes one command line tool, `kom`. It will be registered in the same Conda environment
that the `kelp-o-matic` package is installed to.

```bash
$ kom --help

Usage: kom [OPTIONS] COMMAND [ARGS]...

Options:
  --install-completion  Install completion for the current shell.
  --show-completion     Show completion for the current shell, to copy it or
                        customize the installation.
  --help                Show this message and exit.

Commands:
  find-kelp     Detect kelp in image at path `source` and output the...
  find-mussels  Detect mussels in image at path `source` and output the...
```

## find-kelp

```bash
$ kom find-kelp --help

Usage: kom find-kelp [OPTIONS] SOURCE DEST

  Detect kelp in image at path SOURCE and output the resulting
  classification raster to file at path DEST.

Arguments:
  SOURCE  Input image with Byte data type.  [required]
  DEST    File path location to save output to.  [required]

Options:
  --species / --presence  Segment to species or presence/absence level.
                          [default: presence]
  --crop-size INTEGER     The size for the cropped image squares run through
                          the segmentation model.  [default: 512]
  --padding INTEGER       The number of context pixels added to each side of
                          the image crops.  [default: 256]
  --batch-size INTEGER    The batch size of cropped image sections to process
                          together.  [default: 1]
  --gpu / --no-gpu        Enable or disable GPU, if available.  [default: gpu]
  --help                  Show this message and exit.
```

Example usage:

```bash
$ kom find-kelp --presence --crop-size=3200 ./some/image_with_kelp.tif ./some/place_to_write_output.tif
```

## find-mussels

```bash
$ kom find-mussels --help

Usage: kom find-mussels [OPTIONS] SOURCE DEST

  Detect mussels in image at path SOURCE and output the resulting
  classification raster to file at path DEST.

Arguments:
  SOURCE  Input image with Byte data type.  [required]
  DEST    File path location to save output to.  [required]

Options:
  --crop-size INTEGER   The size for the cropped image squares run through the
                        segmentation model.  [default: 512]
  --padding INTEGER     The number of context pixels added to each side of the
                        image crops.  [default: 256]
  --batch-size INTEGER  The batch size of cropped image sections to process
                        together.  [default: 1]
  --gpu / --no-gpu      Enable or disable GPU, if available.  [default: gpu]
  --help                Show this message and exit.
```

Example usage:

```bash
$ kom find-mussels ./some/image_with_mussels.tif ./some/place_to_write_output.tif
```