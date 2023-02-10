Installation and Updating
=========================

The most reliable way to install ``kelp-o-matic`` is with `Conda <https://docs.anaconda.com/anaconda/>`_.

The library is currently available for Python versions 3.7 through 3.10. Support for future versions will be added when it
becomes possible.

New versions of the tool are occasionally released to improve segmentation performance, speed, and
the user interface of the tool. Changes are published to the PyPI and Anaconda repositories using
`semantic versioning <https://semver.org/>`_. You may want to occasionally run the update commands to ensure
that you're using the most up-to-date version of `kelp-o-matic`.


Conda
-----

Use the Anaconda Navigator GUI to create a new environment and add the *hakai-institute*, *conda-forge*, and *pytorch* channels
before searching for and installing the ``kelp-o-matic`` package in your environment.

Alternatively, install using your terminal or the Anaconda prompt (for Windows users) by running the following command:

.. code-block:: bash

    conda install -c pytorch -c conda-forge kelp-o-matic

You can update the package when new versions become available with:

.. code-block:: bash

    conda update -c pytorch -c conda-forge kelp-o-matic

PIP
---

.. warning:: It is highly recommended to install the library with Conda, not with PIP.

You can install ``kelp-o-matic`` with PIP. Automatic hardware acceleration is only supported with the Conda install.

.. code-block:: bash

    pip install kelp-o-matic

Similarly, to update:

.. code-block:: bash

    pip install --upgrade kelp-o-matic
