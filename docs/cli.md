# Command Line Reference

The `kelp-o-matic` package includes one command line tool, `kom`. It will be registered in the same Conda environment
that the `kelp-o-matic` package is installed to.

```
$ kom --help

 Usage: python -m kelp_o_matic.cli [OPTIONS] COMMAND [ARGS]...

   Options 
  --version             -v                                                                                                                                                         
  --install-completion          [bash|zsh|fish|powershell|pwsh]  Install completion for the specified shell. [default: None]                                                       
  --show-completion             [bash|zsh|fish|powershell|pwsh]  Show completion for the specified shell, to copy it or customize the installation. [default: None]                
  --help                -h                                       Show this message and exit.                                                                                       
  
   Commands
  find-kelp           Detect kelp in image at path SOURCE and output the resulting classification raster to file at path DEST.                                                     
  find-mussels        Detect mussels in image at path SOURCE and output the resulting classification raster to file at path DEST.                                                  
```

## find-kelp

```
$ kom find-kelp --help

 Usage: python -m kelp_o_matic.cli find-kelp [OPTIONS] SOURCE DEST

 Detect kelp in image at path SOURCE and output the resulting classification raster to file at path DEST.

   Arguments
  *    source      TEXT  Input image with Byte data type. [default: None] [required]                                    
  *    dest        TEXT  File path location to save output to. [default: None] [required]                               

   Options
  --species        --presence             Segment to species or presence/absence level. [default: presence]             
  --crop-size                    INTEGER  The data window size to run through the segmentation model. [default: 1024]   
  --gpu            --no-gpu               Enable or disable GPU, if available. [default: gpu]                           
  --help       -h                         Show this message and exit.                                                   
```

!!! Example

    ```bash
    kom find-kelp --species --crop-size=1024 ./some/image_with_kelp.tif ./some/place_to_write_output.tif
    ```

[//]: # (??? info "Info: Misclassifications over land")

[//]: # ()

[//]: # (    Currently, Kelp-O-Matic is mostly optimized to differentiate between canopy-forming kelp, water, and)

[//]: # (    near-shore land. It is a known issue that inland vegetation is sometimes misclassified as)

[//]: # (    kelp. )

[//]: # ()

[//]: # (    Please check out our [post-process documentation]&#40;post_process.md&#41; for our recommendations on)

[//]: # (    cleaning up the output classification mask.)

## find-mussels

```
$ kom find-mussels --help

 Usage: python -m kelp_o_matic.cli find-mussels [OPTIONS] SOURCE DEST

 Detect mussels in image at path SOURCE and output the resulting classification raster to file at path DEST.

   Arguments
  *    source      TEXT  Input image with Byte data type. [default: None] [required]                                    
  *    dest        TEXT  File path location to save output to. [default: None] [required]                               

   Options
  --crop-size                  INTEGER  The data window size to run through the segmentation model. [default: 1024]     
  --gpu            --no-gpu             Enable or disable GPU, if available. [default: gpu]                             
  --help       -h                       Show this message and exit.                                                     
```

!!! example

    ```bash
    kom find-mussels --crop-size=1024 ./some/image_with_mussels.tif ./some/place_to_write_output.tif
    ```
