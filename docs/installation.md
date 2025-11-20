# Installation

Habitat-Mapper is available for Python versions 3.10 through 3.13.

Please select the installation method that best matches your experience level.

=== "Beginner Guide (Recommended)"

    !!! tip "New to the Command Line?"
        Don't worry! Check the **[Beginner's Guide](/beginner_guide)** that walks you through setting up your terminal
        and then come back here.

    We recommend using `uv` to manage your environment. It is faster than standard Python tools and simplifies the setup process across Windows, macOS, and Linux.

    ### 1. Install `uv`

    If you haven't installed `uv` yet, run the command for your operating system:

    === "Windows"
        ```powershell
        powershell -ExecutionPolicy ByPass -c "irm [https://astral.sh/uv/install.ps1](https://astral.sh/uv/install.ps1) | iex"
        ```
    === "MacOS/Linux"
        ```bash
        curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh
        ```

    *Restart your terminal after installation to ensure the `uv` command is recognized.*

    ### 2. Create a Virtual Environment

    Navigate to your project folder and create a clean environment.

    !!! warning "Storage Location"
        **Windows Users:** Create your environment on a local drive (e.g., `C:`), not a network drive. This avoids common GDAL errors.

    ```bash
    # 1. Go to your preferred folder
    cd path/to/your/projects

    # 2. Create the environment named 'habitat-env'
    uv venv habitat-env
    ```

    ### 3. Activate the Environment

    You must activate the environment every time you open a new terminal to work on this project.

    === "Windows"
        !!! warning "Fixing Permission Errors"
            The first time you run the activation command below, you might see an error stating:
            *`cannot be loaded because running scripts is disabled on this system.`*

            To fix this, run the following command once:
            ```powershell
            Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
            ```

        **Activate the environment:**
        ```powershell
        .\habitat-env\Scripts\activate
        ```

    === "MacOS/Linux"
        ```bash
        source ./habitat-env/bin/activate
        ```

    *Your terminal prompt should now show `(habitat-env)`*

    ### 4. Install Habitat-Mapper

    With the environment active, install the package:

    ```bash
    uv pip install habitat-mapper
    ```

=== "Standard Pip (Advanced)"

    We strongly recommend installing habitat-mapper in a virtual environment to prevent compatability issues with
    system Python packages. Installation of Habitat-Mapper can be installed from PyPI using `pip`.

    ```bash
    pip install habitat-mapper
    ```

---

## Verify Installation

To verify that Habitat-Mapper was installed correctly and to check the installed version, run:

```bash
hab --version
```

!!! important "Troubleshooting 'Command Not Found'"
    The `hab` command is **only** available when your virtual environment is activated.

    ```
    If you see an error like `command not found` or `hab is not recognized`:

    1. Check your terminal prompt. Does it show `(habitat-env)` (or your environment name)?
    2. If not, run the **Activation** command from Step 3 above.
    3. Try `hab --version` again.
    ```

## Updating

We follow [semantic versioning](https://semver.org/). To update to the latest version:

=== "Using uv"
    `uv pip install --upgrade habitat-mapper`

=== "Standard Pip"
    `pip install --upgrade habitat-mapper `

## Next Steps

* **Beginners:** Head to [Processing Images](beginner_guide/execution.md) to run your first segmentation.
* **Advanced:** Check the [CLI Reference](cli.md) for available command flags.
