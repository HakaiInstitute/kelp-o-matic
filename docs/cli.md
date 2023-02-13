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

!!! Example

    ```bash
    kom find-kelp --species --crop-size=1024 ./some/image_with_kelp.tif ./some/place_to_write_output.tif
    ```

???+ tip "Tip: Reduce windowed processing artifacts"

    To reduce artifacts caused by Kelp-O-Matic's moving window classification, use the largest `crop_size` that you can.
    Try starting with a crop_size around 3200 pixels and reduce it if your computer is unable to load that much data at once and the application crashes.

    We hope to improve Kelp-O-Matic in the future such that the maximum crop size for your computer can be determined automatically.
    
    CLI Example:

    ```bash
    kom --crop-size=3200 your-input-image.tif output-image.tif
    ```

    <div style="display:flex;">
        <img alt="Small window output" src="../images/kom-small-window.png" width="50%"/>
        <img alt="Big window output" src="../images/kom-big-window.png" width="50%"/>
    </div>

[//]: # (??? info "Info: Misclassifications over land")

[//]: # ()
[//]: # (    Currently, Kelp-O-Matic is mostly optimized to differentiate between canopy-forming kelp, water, and)

[//]: # (    near-shore land. It is a known issue that inland vegetation is sometimes misclassified as)

[//]: # (    kelp. )

[//]: # ()
[//]: # (    Please check out our [post-process documentation]&#40;post_process.md&#41; for our recommendations on)

[//]: # (    cleaning up the output classification mask.)

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

!!! example

    ```bash
    kom find-mussels --crop-size=1024 ./some/image_with_mussels.tif ./some/place_to_write_output.tif
    ```