# Terminal Crash Course

The terminal is a text-based interface to your computer. It allows you to run
commands to interact with your computer. The terminal is where you will run the
Kelp-O-Matic tool.

There are slight differences in how you interact with the terminal
depending on your operating system, so choose the tab below based on which is relevant to you.

### Accessing the Terminal

=== "Windows"
    On Windows, there are two default terminal options: Command Prompt and PowerShell.
    You can use either of these to run the Kelp-O-Matic tool. We recommend using PowerShell.

    To open PowerShell, search for "PowerShell" in the search bar and click on the
    application that appears.

=== "MacOS/Linux"
    On MacOS and Linux, the default terminal is called Terminal. To open Terminal, search for "Terminal" in the search bar 
    and click on the application that appears.

### Nagivating around

=== "Windows"
    There are two main commands you will use to navigate around the file system in the terminal: `cd` and `dir`.
    `cd` stands for "change directory" and is used to move between folders. `dir` stands for "directory" and is used to list the contents of a folder.

    !!! tip "Cheat Sheet"

        | Command | Description |
        | ------- | ----------- |
        | `cd [some path]` | Change directory |
        | `dir [some path]` | List files and folders in the current directory |

=== "MacOS/Linux"
    There are two main commands you will use to navigate around the file system in the terminal: `cd` and `ls`.
    `cd` stands for "change directory" and is used to move between folders. `ls` means for "list" and is used to list the contents of a folder.

    !!! tip "Cheat Sheet"

        | Command | Description |
        | ------- | ----------- |
        | `cd [some path]` | Change directory |
        | `ls [some path]` | List files and folders in the current directory |
    

#### Specifying Paths

=== "Windows"
    - Use backslashes `\` to separate folders in a path.
    - Using `..` is interpreted as "the parent directory" of my current location.
    - Using `.` is interpreted as "the current directory".
    - Using `~` is interpreted as the user's home directory. (e.g. `C:\Users\McLovin`, if that is your username)
    - You can use relative paths to navigate to folders in relation to your current location, like ` cd .\Documents` 
    - You can also use absolute paths to navigate, like `cd C:\Users\McLovin\Documents`.
    - Use ++tab++ to autocomplete file and folder names. It is **very strongly** recommended to use this to avoid typos and save time typing long paths.
        - e.g. `cd C:\Users\McLovin\Docu` then press ++tab++ to autocomplete to `cd C:\Users\McLovin\Documents`. Pressing ++tab++ again will cycle through all possible completions.

=== "MacOS/Linux"
    - Use forward slashes `/` to separate folders in a path.
    - Using `..` is interpreted as "the parent directory" of my current location.
    - Using `.` is interpreted as "the current directory".
    - Using `~` is interpreted as the user's home directory. (e.g. `/home/mclovin`, if that is your username)
    - You can use relative paths to navigate to folders in relation to your current location, like ` cd ./documents` 
    - You can also use absolute paths to navigate, like `cd /home/mclovin/documents`. Absolute paths start from the root directory `/`.
    - Use ++tab++ to autocomplete file and folder names. It is **very strongly** recommended to use this to avoid typos and save time typing long paths.
        - e.g. `cd /home/mclovin/docu` then press ++tab++ to autocomplete to `cd /home/mclovin/documents`. Pressing ++tab++ again will cycle through all possible completions.


!!! example "Examples"
    === "Windows"
        | Command | Effect |
        | ------- | ------ |
        | `dir` | List files and folders in the current directory |
        | `dir .` | Same as above |
        | `dir ..` | List files and folders in the parent directory of your current location|
        | `cd Documents` | Move to a folder called `Documents`, that is contained in the current directory |
        | `cd .\Documents` | Same as above |
        | `cd ..` | Move up one directory |
        | `cd Downloads\CoolDirectory` | Move to a folder called `CoolDirectory` inside a folder called `Downloads` contained in your current directory |
        | `cd ~` | Move to your user home directory |
        | `cd ~\Documents` | Move to a folder called `Documents` inside the user home directory |
        | `cd ..\Documents` | Move up one folder and then into a folder called `Documents` |
        | `cd C:\Users\McLovin\Documents` | Move to a folder called `Documents` inside the `McLovin` user directory on the `C:` drive |


    === "MacOS/Linux"
        | Command | Effect |
        | ------- | ------ |
        | `ls` | List files and folders in the current directory |
        | `ls .` | Same as above |
        | `ls ..` | List files and folders in the parent directory of your current location|
        | `cd documents` | Move to a folder called `documents`, that is contained in the current directory |
        | `cd ./documents` | Same as above |
        | `cd ..` | Move up one directory |
        | `cd downloads/cool_directory` | Move to a folder called `cool_directory` inside a folder called `downloads` contained in your current directory |
        | `cd ~` | Move to your user home directory |
        | `cd ~/documents` | Move to a folder called `documents` inside the user home directory |
        | `cd ../documents` | Move up one folder and then into a folder called `Documents` |
        | `cd /home/mclovin/documents` | Move to a folder called `documents` inside the `mclovin` home directory |

!!! warning "Spaces in Paths"
    If a folder or file name has a space in it, you need to enclose the path in quotes. 
    For example, if you have a folder called `My Documents`, you would need to use `cd "My Documents"`. 
    It's a good idea to avoid spaces in folder and file names to make your life easier. Many people use 
    underscores `_` or hyphens `-` instead of spaces.


You did it! You now know enough to navigate around the terminal. There are many commands you can use 
in the terminal, but these are the most important ones to get you started. You're now going to copy and paste some 
commands to set up the Kelp-O-Matic tool, detailed in the next section. This is going to add a new command to your 
terminal that you can use to run the Kelp-O-Matic tool.

### Next Steps

Time to move on to the next section: [Virtual Environment Setup and Installation](./install_env_setup.md)
