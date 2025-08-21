# Python Library Reference

The Python library provide two functions that run classification on an input image and write data to an output location.

## API

### Running the segmentation models

::: kelp_o_matic.segment
    options:
        show_root_heading: True
        heading_level: 4

!!! example
    ```
    import kelp_o_matic

    kelp_o_matic.segment(
        model_name="kelp-rgb",
        revision="20240722",
        img_path="/path/to/your/image.tif",
        output_path="/path/to/save/results_kelp.tif",
        batch_size=1,
        crop_size=2048,
        blur_kernel_size=5,
        morph_kernel_size=0,
    )
    ```

::: kelp_o_matic.model_registry
    options:
        show_root_heading: True
        heading_level: 4

As an alternative to the segment function, you can also use the model registry to access the different models and model revisions.

!!! example
    ```
    import kelp_o_matic

    model = kelp_o_matic.model_registry["kelp-rgb", "20240722"]
    model.process(
        img_path="/path/to/your/image.tif",
        output_path="/path/to/save/results_kelp.tif",
        batch_size=1,
        crop_size=2048,
        blur_kernel_size=5,
        morph_kernel_size=0,
    )
    ```

### Getting model information

::: kelp_o_matic.models
    options:
        show_root_heading: True
        heading_level: 4

::: kelp_o_matic.revisions
    options:
        show_root_heading: True
        heading_level: 4

### Freeing up space

::: kelp_o_matic.clean
    options:
        show_root_heading: True
        heading_level: 4



