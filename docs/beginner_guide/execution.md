# Running the Segmentation Tool

Each time you want to run a classification on new imagery follow these steps.

1. Open your preferred terminal
    1. See the [Terminal Crash Course](./terminal_crash_course.md) if you need to refresh your memory.
2. Activate your virtual environment
    1. This is detailed under [Virtual Environment Setup and Installation](./install_env_setup.md).
3. Run the Kelp-O-Matic tool, as detailed in this document.

***

## The `kom` Command

The `kom` command is the entry point for the Kelp-O-Matic tool. It is used to run the image processing tools that are part of the Kelp-O-Matic package.

`kom`, like many command line tools, has a number of subcommands that can be used to run different tools.

### Getting Help

It is typical of many CLI tools to also have a `--help` option that can be used to get more information about the tool and its subcommands. This is also true for `kom`.

To get help documentation for the `kom` tool, you can type `kom --help` into your terminal.

??? tip "Shorthand flags"
    You can also use the shorthand flags `-h` to get help, e.g. `kom -h`. This is common for many CLI tools. 
    Options will be shown in the help documentation with both the long form (`--help`) and the shorthand form (`-h`).

```console
kom --help
```

This will show you a list of the subcommands available to you, as well as a brief description of what each subcommand does.

### Processing an Image

??? note "A note on mussel detection"
    The Kelp-O-Matic tool is designed to detect both kelp and mussels. The following information was written for kelp 
    detection, but the same information applies for mussels. All you have to do to find mussels instead of kelp is use 
    the `kom find-mussels` subcommand instead of `kom find-kelp` in the following steps.

#### Subcommands and Options
To process an image, you will need to use the `kom find-kelp` subcommand. This subcommand is used to detect kelp in an 
image. Like we did for `kom`, we can also get help for subcommands:

```console
kom find-kelp --help
```

And it will print out something like this:

```console
 Usage: kom find-kelp [OPTIONS] SOURCE DEST

 Detect kelp in image at path SOURCE and output the resulting classification raster to file at path DEST.

   Arguments
  *    source      FILE  Input image with Byte data type. [default: None] [required]
  *    dest        FILE  File path location to save output to. [default: None] [required]

   Options
  --species        --presence             Segment to species or presence/absence level. [default: presence]
  --crop-size                    INTEGER  The data window size to run through the segmentation model. [default: 1024]
  --rgbi           --rgb                  Use RGB and NIR bands for classification. Assumes RGBI ordering. [default: rgb]
               -b                INTEGER  GDAL-style band re-ordering flag. Defaults to RGB or RGBI order. To e.g., reorder a BGRI image at runtime, pass flags `-b 3 -b 2 -b 1 -b 4`. [default: None]
  --gpu            --no-gpu               Enable or disable GPU, if available. [default: gpu]
  --tta            --no-tta               Use test time augmentation to improve accuracy at the cost of processing time. [default: no-tta]
  --help       -h                         Show this message and exit.
```

This help documentation will show you the required arguments and options that are available to you when running the `find-kelp` subcommand.

#### Constructing and Executing a Command

##### Arguments
We're going to use the above `--help` documentation to construct a command relevant to the image we want to process.
For the `SOURCE` and `DEST` arguments, you will need to provide the path to the image you want to process and the path where you want to save the output, respectively.
The same path options discussed in the [Terminal Crash Course](./terminal_crash_course.md) apply here.

##### Options
The various options available to you are detailed in the `--help` documentation. You can use these options to customize the processing of your image, or you can use the default values.
The options are flags that can be used to enable or disable certain features of the tool, or they can take arguments to customize the behavior of the tool.

!!! example "An Example Command"
    
    === "Windows"

        ```console
        kom find-kelp --species --crop-size 2048 .\some\image_with_kelp.tif .\some\output.tif
        ```

        In this example, we are running the `find-kelp` subcommand with the `--species` option and a 
        `--crop-size` of 2048. The input image is located at `.\some\image_with_kelp.tif`. 
        The output will be saved to `.\some\output.tif`.
    
    === "MacOS/Linux"

        ```console
        kom find-kelp --species --crop-size 2048 ./some/image_with_kelp.tif ./some/output.tif
        ```

        In this example, we are running the `find-kelp` subcommand with the `--species` option and a 
        `--crop-size` of 2048. The input image is located at `./some/image_with_kelp.tif`. 
        The output will be saved to `./some/output.tif`.

##### Executing the Command
Once you have constructed your command, execute it by pressing ++enter++. 

Wait for the progress bar to reach 100%, then open the results in an image processing or spatial analysis software such as QGIS or ArcGIS. 
Review the results for errors and edit as needed.

**Part 3 Kelp Segmentation is now complete!**

Continue to [Part 4](./post_processing.md) to learn how to post-process the results.
