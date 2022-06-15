Python Library Reference
====================

The Python library provide two functions that run classification on an input image and write data to an output location.

API
---

.. automodule:: hakai_segmentation
    :members:


Example Usage
-------------

.. code-block:: python

    import hakai_segmentation
    hakai_segmentation.find_kelp("./path/to/kelp_image.tif", "./path/to/output_file_to_write.tif")
