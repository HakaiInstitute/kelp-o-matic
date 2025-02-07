# Virtual Environment Setup and Installation

It is recommended to install Kelp-O-Matic in a virtual environment to avoid conflicts
with other Python packages present on your system. `uv` is our recommended environment manager, so we'll use it in this
guide.

??? question "Why UV"

    `uv` is a Python environment manager that is easy to use and works on Windows, MacOS, and Linux.
    It is a good choice for beginners and experienced users alike. It's extremely fast and lightweight, and provides a
    simple way to manage Python environments and install packages.

## UV Virtual Environment Setup

1. Install `uv` using their [installation instructions](https://docs.astral.sh/uv/getting-started/installation/).
    1. This will make a new command available in your terminal called `uv`.
    2. Check the official instructions for installation, but generally, you're going to copy and paste the installation
       command they provide (e.g. `curl ...`) into your terminal and press ++enter++. Read and follow the instructions
       and prompts that are printed.

2. Once UV is installed, create a new "virtual environment" in your preferred location with the following commands:
    ```bash
    cd path/to/your/preferred/location
    uv venv my_env_name  # my_env_name is the name of your virtual environment. You can choose any name you like.
    ```

    ??? question "What's a Virtual Environment"

        A virtual environment is a self-contained directory that contains a Python installation for a particular version
        of Python, plus a number of additional packages. It allows you to work on a specific project without affecting
        other projects or the system Python installation.

        It's a good practice to create a new virtual environment for each project you work on. This way, you can install the
        specific versions of the packages you need for that project without affecting other projects.

3. Activate the virtual environment

    === "Windows"
        ```powershell
        .\my_env_name\Scripts\activate
        ```

    === "MacOS/Linux"
        ```bash
        source ./my_env_name/bin/activate
        ```

Many terminal emulators will show the name of the active virtual environment in the prompt. For example, the prompt might
change from `C:\Users\McLovin>` to `(my_env_name) C:\Users\McLovin>`. This indicates that the virtual environment is
active.

??? note "Manual deactivation"
    If you want to deactivate the virtual environment without closing your terminal, run:

    ```bash
    deactivate
    ```

## Install Kelp-O-Matic

Now that you have your virtual environment set up, you can install Kelp-O-Matic and its dependencies very easily with
`uv`.

1. Install Kelp-O-Matic using the following command:
    ```bash
    uv pip install kelp-o-matic
    ```

!!! important

      The `kom` command will be available only when the virtual environment is activated. If you close your terminal,
      be sure to navigate to the location where you created the virtual environment and activate it again before running
      `kom`.

??? question "What's `uv pip`?"
    `uv` has a built-in package manager called `pip` that you can use to install Python packages. When not using `uv`,
    Python comes with a package manager called `pip`. `uv pip` is just a faster version of that default package manager.

## Next Steps

You're now ready to process some imagery, hooray! Head over to the next section,
[Running the Segmentation tool](./execution.md), to learn how to run the segmentation tool
