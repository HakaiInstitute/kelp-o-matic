# Processing Images with Kelp-O-Matic

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
    Many CLI options have shorthand flags for convenience. For example, `--input` can be shortened to `-i` and `--output` can be shortened to `-o`.
    Options will be shown in the help documentation with both the long form (`--input`) and the shorthand form (`-i`).

```console
kom --help
```

This will show you a list of the subcommands available to you, as well as a brief description of what each subcommand does.

### Discovering Available Models

Before processing an image, you should see what models are available to you. Kelp-O-Matic comes with multiple models for different types of marine life and different image types.

To see all available models, use the `kom models` command:

```console
kom models
```

This will show you a table with all available models, their latest revisions, descriptions, and availability status. For example, you might see models for kelp detection, mussel detection, or other marine organisms.

If you want to see all available revisions for a specific model, you can use:

```console
kom revisions <model-name>
```

For example:
```console
kom revisions kelp-rgb
```

### Processing an Image

#### Subcommands and Options
To process an image, you will need to use the `kom segment` subcommand. This subcommand is used to apply a segmentation model to an image. Like we did for `kom`, we can also get help for subcommands:

```console
kom segment --help
```

And it will print out something like this:

```console
Usage: kom segment [ARGS] [OPTIONS]

Apply a segmentation model to an input raster and save the output.

╭─ Parameters ──────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  MODEL --model                        -m  The name of the model to run. Run kom models to see options           │
│                                             [required]                                                            │
│ *  INPUT --input                        -i  Path to input 8 band PlanetScope raster file [required]               │
│ *  OUTPUT --output                      -o  Path to the output raster that will be created [required]             │
│    REVISION --revision --rev                The revision of the model to use. Run kom revisions <model_name> to   │
│                                             see options [default: latest]                                         │
│    BATCH-SIZE --batch-size --batch          Batch size for processing [default: 1]                                │
│    CROP-SIZE --crop-size --size         -z  Tile size for processing (must be even). Defaults to the 1024 or to   │
│                                             the size required by the model                                        │
│    BLUR-KERNEL --blur-kernel --blur         Size of median blur kernel (must be odd) [default: 5]                 │
│    MORPH-KERNEL --morph-kernel --morph      Size of morphological kernel (must be odd, 0 to disable) [default: 0] │
│    BAND-ORDER --band-order              -b  Band reordering flag for rearranging bands into RGB(+NIR) order when  │
│      --empty-band-order                     necessary.                                                            │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

This help documentation will show you the required arguments and options that are available to you when running the `segment` subcommand.

#### Constructing and Executing a Command

##### Arguments
We're going to use the above `--help` documentation to construct a command relevant to the image we want to process.
For the `MODEL`, `INPUT` and `OUTPUT` arguments, you will need to:

1. Choose a model name from the list shown by `kom models`
2. Provide the path to the image you want to process
3. Provide the path where you want to save the output

The same path options discussed in the [Terminal Crash Course](./terminal_crash_course.md) apply here.

##### Options
The various options available to you are detailed in the `--help` documentation. You can use these options to customize the processing of your image, or you can use the default values.
The options are flags that can be used to enable or disable certain features of the tool, or they can take arguments to customize the behavior of the tool.

!!! example "An Example Command"

    === "Windows"

        ```console
        kom segment kelp-rgb --crop-size 2048 --input .\some\image_with_kelp.tif --output .\some\output.tif
        ```

        In this example, we are running the `segment` subcommand with the `kelp-rgb` model and a
        `--crop-size` of 2048. The input image is located at `.\some\image_with_kelp.tif`.
        The output will be saved to `.\some\output.tif`.

    === "MacOS/Linux"

        ```console
        kom segment kelp-rgb --crop-size 2048 --input ./some/image_with_kelp.tif --output ./some/output.tif
        ```

        In this example, we are running the `segment` subcommand with the `kelp-rgb` model and a
        `--crop-size` of 2048. The input image is located at `./some/image_with_kelp.tif`.
        The output will be saved to `./some/output.tif`.

??? example "Additional Examples"

    **Complete workflow - discovering and using models:**

    ```console
    # First, see what models are available
    kom models
    
    # Choose a model based on your image type and target organism
    # For example, if you want to detect mussels in RGB imagery:
    kom segment mussel-rgb --input ./my_image.tif --output ./mussel_results.tif
    
    # Or if you want to detect kelp in 4-band RGBI imagery:
    kom segment kelp-rgbi --input ./rgbi_image.tif --output ./kelp_results.tif
    ```

    **Using a specific model revision:**

    ```console
    # First, check what revisions are available for a model
    kom revisions kelp-rgb
    
    # Use a specific revision instead of the latest
    kom segment kelp-rgb --revision 20240722 --input ./my_image.tif --output ./results.tif
    ```

    This is useful when you need to reproduce results with a specific model version or when you want to use a previous revision for consistency with earlier work.

    **Re-ordering bands for BGRI image (Blue-Green-Red-NIR to RGB-NIR):**

    === "Windows"

        ```console
        kom segment kelp-rgbi -b 3 -b 2 -b 1 -b 4 --input .\some\bgri_image.tif --output .\some\output.tif
        ```

    === "MacOS/Linux"

        ```console
        kom segment kelp-rgbi -b 3 -b 2 -b 1 -b 4 --input ./some/bgri_image.tif --output ./some/output.tif
        ```

    In the band re-ordering example, `-b 3 -b 2 -b 1 -b 4` tells Kelp-O-Matic to rearrange the bands from BGRI order (bands 1,2,3,4) to RGBI order by taking band 3 (Red), band 2 (Green), band 1 (Blue), and band 4 (NIR).

##### Executing the Command
Once you have constructed your command, execute it by pressing ++enter++.

Wait for the progress bar to reach 100%, then open the results in an image processing or spatial analysis software such as QGIS or ArcGIS.
Review the results for errors and edit as needed.

??? tip "Checking GPU Usage"

    If you have a GPU, you should be able to run `nvidia-smi` to check its status.
    You can see here what processes are using the GPU, and how much memory they are using.

    If Kelp-O-Matic is running, you'll have to run this in a new PowerShell window or tab.
    If Kelp-O-Matic is actively using the GPU, you should see it listed here.

#### Aborting Processing

If you need to stop the processing of an image, you can press ++ctrl+c++ in the terminal to send a signal to the process
that it should stop. This will stop the processing and return you to the command prompt.

This is useful, for example, if you realize that you entered the wrong path and need to correct it but don't want to
wait for `kom` for finish running.

This command is standard in the terminal. It is used to send a signal to the running process that it should stop.

---

**Part 3 Image Segmentation is now complete!**

Continue to [Part 4](./post_processing.md) to learn how to post-process the results.
