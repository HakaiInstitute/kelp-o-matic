# Python Library Reference

The Python library provide two functions that run classification on an input image and write data to an output location.

## API


::: kelp_o_matic.find_kelp
    options:
        show_root_heading: True
        heading_level: 3

!!! example

    ```python
    import kelp_o_matic
    kelp_o_matic.find_kelp("./path/to/kelp_image.tif", "./path/to/output_file_to_write.tif", crop_size=3200)
    ```

***

::: kelp_o_matic.find_mussels
    options:
        show_root_heading: True
        heading_level: 3

!!! example

    ```python
    import kelp_o_matic
    kelp_o_matic.find_mussels("./path/to/mussel_image.tif", "./path/to/output_file_to_write.tif", crop_size=3200)
    ```