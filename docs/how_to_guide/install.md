# Installation

## Standalone Executable
Starting with v0.3, [standalone executables are available](https://github.com/usnistgov/nestor/releases) for windows, linux, and mac. This feature is new and very much in beta. Meant to be a temporary solution for those not needing access to the underlying Nestor API, it will eventually be replaced by more portable, web-app solutions. 

> Note that `nestor-dash` and `nestor-gui` command line scripts will not be installed, and therefore unavailable! Only the interface normally accessible via `nestor-gui` is bundled as an executable at this time.

At the link above, select a distribution (Linux 5.0 x86_64 or greater, tested on Ubuntu 18.10; Windows 10 or greater; OSx v10.1 or greater), which downloads a zipped folder containing dependencies and the program itself. Extract the folder to any directory and run the `Nestor` file to start tagging!

> On Windows, you will see a `Nestor.exe`; on Linux you must ensure the `Nestor` script file is executable, and can be run in the terminal via `./<path-to-file>/Nestor`


## Python-based Install 
If you want to use the Nestor API to access NLP/plotting functions, along with access to the (beta) `nestor-dash` analysis webtool, you will need to install Nestor as a python library. This will assume a basic level of familiarity with python and terminal usage. 


### System Requirements
The installation can be done using either the automatic *pip* method (recommended) or by downloading the installation and completing it manually.
To install Nestor, your computer must at least have the following configured:
* Operating system: Windows 10, Mac OS, or Ubuntu Linux
* A working installation of Python 3. If you do not have Python installation, an easy way to install it is using the [Anaconda distribution](https://www.anaconda.com/download) of Python.
* The Comma Separated Value (csv) file that contains your raw data must be in UTF-8 encoding to be compatible with the tagging tool. Your computer has [tools](https://www.ibm.com/support/knowledgecenter/en/SSWU4L/WebLanding/imc_WebLanding/WebLanding_q_a_watson_assistant/Saving_a_CSV_file_with_UTF-8_encoding.html) to help you save your csv as utf-8.
* If you decide to use a `conda` environment (recommended), ensure `pip` is installed in the environment itself to prevent references to the top-level pip installation

### Nestor Installation using PyPI (Recommended)
This is the recommended way of installing Nestor since it is minimal. To install,

- Open a terminal, and type in `pip install nist-nestor`. The installation will then proceed automatically and will install the graphical user interface (GUI) for the Nestor Tagging Tool.
- Optionally, you can install additional dependencies for the Nestor Dashboard using the `[dash]` options flag, as: `pip install nist-nestor[dash]`
- The developer releases (unstable!) can be installed directly from the github `master` branch, if you have `git` installed: `pip install git+https://github.com/usnistgov/nestor.git`


### Nestor installation using local archive
This step is necessary **only** if you did not install using the above method (using PyPI), or if you wish to edit code locally while still gaining access to the command-line scripts.

1. Download a [.zip file](https://github.com/usnistgov/nestor/archive/master.zip) of the entire nestor repository from Github.
2. Extract the files to a directory, preferably with write access, and navigate a terminal to the folder where the files have been extracted to (the folder will have the file setup.py in it).
5. Install nestor using the command `pip install -e . ` (note the ".")
> (Optional Step) Type in `pip install -e .[dash]` to install the Nestor Dashboard with dependencies.

