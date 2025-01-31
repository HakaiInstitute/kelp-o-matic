# Installation and Updating

## Requirements

Kelp-O-Matic is currently available for Python versions 3.10 through 3.13.

## Quick Install

=== "PIP"

    ```bash
    pip install kelp-o-matic
    ```

=== "Conda"

    ```bash
    conda install -c conda-forge kelp-o-matic
    ```

!!! help "Need more help?"

    If you are unfamiliar with the command line or installing Python packages, you may
    find our [Beginner Guide](beginner_guide/index.md) helpful.

## Recommended Installation (Virtual Environment)

It is recommended to install Kelp-O-Matic in a virtual environment to avoid conflicts
with other Python packages present on your system. `uv` is our recommended environment manager
(a faster alternative to `venv`/`virtualenv`), but you can use any Python environment manager you prefer.

**UV Virtual Environment Setup**

1. Install `uv` using their [installation instructions](https://docs.astral.sh/uv/getting-started/installation/).

2. Create a new virtual environment (you can replace `kom-env` with a different name if you prefer):
    ```bash
    uv venv kom-env 
    ```

3. Activate the virtual environment

    === "Windows"
        ```powershell
        kom-env\Scripts\activate
        ```

    === "MacOS/Linux"
        ```bash
        source kom-env/bin/activate
        ```

4. Install Kelp-O-Matic and its dependencies

    ```bash
    uv pip install kelp-o-matic
    ```

5. If you want to deactivate the virtual environment, run

    ```bash
    deactivate
    ```

   It will deactivate automatically when you close the terminal. To reactivate, just run `source kom-env/bin/activate`
   (you don't have to reinstall Kelp-O-Matic though).

!!! important 

      The `kom` command will be available only when the virtual environment is activated.

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
