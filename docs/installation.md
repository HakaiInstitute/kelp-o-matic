# Installation and Updating

The most reliable way to install `kelp-o-matic` is with [Conda](https://docs.anaconda.com/anaconda/).

The library is currently available for Python versions 3.9 through 3.11. Support for future versions
will be added when possible.

New versions of the tool are occasionally released to improve segmentation performance, speed, and
the user interface of the tool. Changes are published to the PyPI and Anaconda repositories using
[semantic versioning](https://semver.org/). You may want to occasionally run the update commands to ensure
that you're using the most up-to-date version of `kelp-o-matic`.

## Commands

!!! help "Need more help?"

    If you are unfamiliar with the command line or installing Python packages, you may find our [Beginner Guide](beginner_guide/index.md) helpful.

### Pre-requisites

Install `pytorch` and `torchvision` for your operating system using the
[official installation instructions here](https://pytorch.org/).
Make sure you select "CUDA" as the compute platform if you have an NVIDIA GPU you'd like to use to improve performance.

!!! warning

    Unfortunately, Kelp-O-Matic v0.7.0 and later are only available via `pip` due to 
    a dependency currently missing from conda-forge.

    In the meantime, you can install the prerequisities with `conda` and then install 
    Kelp-O-Matic with `pip`

    Thanks for your patience!


=== "PIP"

    ### Install

    ```bash
    pip install kelp-o-matic
    ```

    ### Update

    ```bash
    pip install --upgrade kelp-o-matic
    ```

=== "Conda"

    ### Install

    ```bash
    conda install -c conda-forge kelp-o-matic
    ```

    ### Update

    ```bash
    conda update -c conda-forge kelp-o-matic
    ```
