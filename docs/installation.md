# Installation and Updating

!!! help "Need more help?"

    If you are unfamiliar with the command line or installing Python packages, you may
    find our [Beginner Guide](beginner_guide/index.md) helpful.

## Requirements

Habitat-Mapper is currently available for Python versions 3.10 through 3.13.

## Quick Install

We recommend using a virtual environment to manage your Python packages. This will help avoid conflicts with other packages and system installations.

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

## Next Steps

For available commands, see the [Command Line Interface](cli.md) documentation.
