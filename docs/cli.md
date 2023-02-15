# Command Line Reference

The `kelp-o-matic` package includes one command line tool, `kom`. It will be registered in the same
Conda environment that the `kelp-o-matic` package is installed to.

```bash
$ kom --help

 Usage: kom [OPTIONS] COMMAND [ARGS]...

╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.                                                               │
│ --show-completion             Show completion for the current shell, to copy it or customize the installation.                        │
│ --help                        Show this message and exit.                                                                             │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ find-kelp                 Detect kelp in image at path SOURCE and output the resulting classification raster to file at path DEST.    │
│ find-mussels              Detect mussels in image at path SOURCE and output the resulting classification raster to file at path DEST. │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## find-kelp

```bash
$ kom find-kelp --help

 Usage: kom find-kelp [OPTIONS] SOURCE DEST
 
 Detect kelp in image at path SOURCE and output the resulting classification raster to file at path DEST.
 
╭─ Arguments ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    source      TEXT  Input image with Byte data type. [default: None] [required]                                                                                                     │
│ *    dest        TEXT  File path location to save output to. [default: None] [required]                                                                                                │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --species       --presence             Segment to species or presence/absence level. [default: presence]                                                                               │
│ --crop-size                   INTEGER  The size for the cropped image squares run through the segmentation model. If unspecified, uses the largest crop size possible. [default: None] │
│ --padding                     INTEGER  The number of context pixels added to each side of the image crops. [default: 256]                                                              │
│ --batch-size                  INTEGER  The batch size of cropped image sections to process together. [default: 1]                                                                      │
│ --gpu           --no-gpu               Enable or disable GPU, if available. [default: gpu]                                                                                             │
│ --help                                 Show this message and exit.                                                                                                                     │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

!!! Example

    ```bash
    kom find-kelp --species ./some/image_with_kelp.tif ./some/place_to_write_output.tif
    ```

??? tip "Tip: Reduce windowed processing artifacts"

    To reduce artifacts caused by Kelp-O-Matic's moving window classification, use the largest `crop_size` that you can.
    Kelp-O-Matic will automatically find a large crop size that fits in your computers memory if you leave this parameter unspecified (the default).

    If you want to specify this size manually, we suggest starting with a crop_size around 6400 pixels and reducing it until the crop size fits into your computer's memory.
    You will know if the crop size does not fit into memory because the program will crash and give an error message stating that insufficient memory was available.
    
    CLI example, manually specifying the crop size:

    ```bash
    kom --crop-size=3200 your-input-image.tif output-image.tif
    ```

    CLI example, automated crop size optimization:

    ```bash
    kom your-input-image.tif output-image.tif
    ```

    <div style="display:flex;">
        <img alt="Small window output" src="../images/kom-small-window.png" width="50%"/>
        <img alt="Big window output" src="../images/kom-big-window.png" width="50%"/>
    </div>

## find-mussels

```bash
$ kom find-mussels --help

 Usage: kom find-mussels [OPTIONS] SOURCE DEST
 
 Detect mussels in image at path SOURCE and output the resulting classification raster to file at path DEST.

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    source      TEXT  Input image with Byte data type. [default: None] [required]                                                                                                   │
│ *    dest        TEXT  File path location to save output to. [default: None] [required]                                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --crop-size                 INTEGER  The size for the cropped image squares run through the segmentation model. If unspecified, uses the largest crop size possible. [default: None] │
│ --padding                   INTEGER  The number of context pixels added to each side of the image crops. [default: 256]                                                              │
│ --batch-size                INTEGER  The batch size of cropped image sections to process together. [default: 1]                                                                      │
│ --gpu           --no-gpu             Enable or disable GPU, if available. [default: gpu]                                                                                             │
│ --help                               Show this message and exit.                                                                                                                     │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

!!! example

    ```bash
    kom find-mussels ./some/image_with_mussels.tif ./some/place_to_write_output.tif
    ```