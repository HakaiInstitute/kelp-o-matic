# Installation and Updating

!!! help "Need more help?"

    If you are unfamiliar with the command line or installing Python packages, you may
    find our [Beginner Guide](beginner_guide/index.md) helpful.

## Requirements

Kelp-O-Matic is currently available for Python versions 3.10 through 3.13.

## Quick Install

We recommend using a virtual environment to manage your Python packages. This will help avoid conflicts with other packages and system installations.


=== "PIP (recommended)"
    ```bash
    pip install kelp-o-matic

    # For Windows users with a CUDA capable GPU, instead run:
    pip install kelp-o-matic --extra-index-url https://download.pytorch.org/whl/cu124
    ```

=== "Conda"

    ```bash
    conda install -c conda-forge kelp-o-matic
    ```

## Verify Installation

To verify that Kelp-O-Matic was installed correctly and to check the installed version, run:

```bash
kom --version
```

If you have an Nvidia GPU, you can check if it is detected with:

```bash
kom --gpu-test
```

## Updating

We follow [semantic versioning](https://semver.org/). Regular updates are recommended for:

- Performance improvements
- New features
- Security patches

To update Kelp-O-Matic, you can use the following commands:

=== "PIP"

    ```bash
    pip install --upgrade kelp-o-matic
    ```

=== "Conda"

    ```bash
    conda update -c conda-forge kelp-o-matic
    ```

## Next Steps

For available commands, see the [Command Line Interface](cli.md) documentation.
