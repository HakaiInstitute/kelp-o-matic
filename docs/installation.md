# Installation and Updating

The most reliable way to install `kelp-o-matic` is with [Conda](https://docs.anaconda.com/anaconda/).

The library is currently available for Python versions 3.9 through 3.11. Support for future versions
will be added when possible.

New versions of the tool are occasionally released to improve segmentation performance, speed, and
the user interface of the tool. Changes are published to the PyPI and Anaconda repositories using
[semantic versioning](https://semver.org/). You may want to occasionally run the update commands to ensure
that you're using the most up-to-date version of `kelp-o-matic`.

## Commands

=== "Conda"

    ??? help "Installing in Anaconda Navigator"

        1. Use the Anaconda Navigator GUI and create a new environment.
        2. Add the `pytorch`, `nvidia`, and `conda-forge` channels.
        3. Search for and install the `torch`, `torchvision`, and `kelp-o-matic` package in your environment. 
            For GPU support, also install the `pytorch-cuda` package.'

        If you need more help, please see the [Beginner Guide](beginner_guide/index.md).

    ### Pre-requisites
    
    ##### PyTorch
    
    Install `pytorch` and `torchvision` for your operating system using the 
    [official installation instructions here](https://pytorch.org/). 
    Make sure you select "CUDA" as the compute platform if you have an NVIDIA GPU you'd like to use to improve performance.
    
    ### Install
    
    ```bash
    conda install -c conda-forge kelp-o-matic
    ```

    ### Update

    ```bash
    conda update -c conda-forge kelp-o-matic
    ```

=== "PIP"
    
    ### Pre-requisites

    ##### PyTorch
    
    Install `pytorch` and `torchvision` for your operating system using the 
    [official installation instructions here](https://pytorch.org/). 
    Make sure you select "CUDA" as the compute platform if you have an NVIDIA GPU you'd like to use to improve performance.
    
    ### Install

    ```bash
    pip install kelp-o-matic
    ```

    ### Update

    ```bash
    pip install --upgrade kelp-o-matic
    ```
