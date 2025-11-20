# Installation and Updating

!!! help "Need more help?"

    If you are unfamiliar with the command line or installing Python packages, you may
    find our [Beginner Guide](beginner_guide/index.md) helpful.

## Requirements

Habitat-Mapper is currently available for Python versions 3.10 through 3.13.

## Quick Install

We recommend using a virtual environment to manage your Python packages. This will help avoid conflicts with other
packages and system installations.

```bash
pip install habitat-mapper
```

## Verify Installation

To verify that Habitat-Mapper was installed correctly and to check the installed version, run:

```bash
hab --version
```

## Updating

We follow [semantic versioning](https://semver.org/). Regular updates are recommended for:

- Performance improvements
- New features
- Security patches

To update Habitat-Mapper, you can use the following commands:

```bash
pip install --upgrade habitat-mapper
```

!!! note "For existing Kelp-O-Matic users"

    If you have previously installed `kelp-o-matic`, we strongly recommend a clean transition to avoid dependency
    conflicts and duplicate files.

    **1. Uninstall the legacy package**

    Remove the old package before installing `habitat-mapper`:

    ```bash
    pip uninstall kelp-o-matic
    pip install habitat-mapper
    ```

    **2. Clean the model cache**

    By default, `habitat-mapper` uses a new cache location. To avoid storing two copies of large model files (one for
    the old tool, one for the new), run the clean command:

    ```bash
    hab clean
    ```

    Select **"y"** when prompted. This will remove legacy Kelp-O-Matic models. `habitat-mapper` will automatically
    re-download the latest optimized models when you run your first `segment` command.

## Next Steps

For available commands, see the [Command Line Interface](cli.md) documentation.
