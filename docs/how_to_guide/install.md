# Installation

## System Requirements
This guide will help you install Nestor. The installation can be done using either the automatic *pip* method (recommended) or by downloading the installation and completing it manually.
To install Nestor, your computer must at least have the following configured:
* Operating system: Windows 10, Mac OS, or Ubuntu Linux
* A working installation of Python 3. If you do not have Python installation, an easy way to install it is using the [Anaconda distribution](https://www.anaconda.com/download) of Python.
* The Comma Separated Value (csv) file that contains your raw data must be in UTF-8 encoding to be compatible with the tagging tool. Your computer has [tools](https://www.ibm.com/support/knowledgecenter/en/SSWU4L/WebLanding/imc_WebLanding/WebLanding_q_a_watson_assistant/Saving_a_CSV_file_with_UTF-8_encoding.html) to help you save your csv as utf-8.

## Nestor Installation using PyPI (Recommended)
This is the recommended way of installing Nestor since it is minimal. To install,

1. Open a command line terminal using these keyboard shortcuts
    * Windows <kbd>START</kbd>+<kbd>R</kbd> and then type `cmd` in the dialog box
    * Mac <kbd>⌘</kbd>+<kbd>SPACE</kbd> and type `Terminal`
    * Ubuntu Linux (some flavors) <kbd>CTRL</kbd>+<kbd>ALT</kbd>+<kbd>T</kbd>

2. Once the terminal window is open, type in `pip install nist-nestor`. The installation will then proceed automatically and will install the graphical user interface (GUI) for the Nestor Tagging Tool.

3. Optionally, you can install the Nestor Dashboard using `pip install nist-nestor[dash]`



## Nestor installation using local archive
This step is necessary **only** if you did not install using the above method (using PyPI).
You can install Nestor locally by downloading the source code from the 
[GitHub repository for Nestor](https://github.com/usnistgov/nestor)

1. Download the .zip file of the entire nestor installation from the Github repository
2. Extract the files to a directory, preferably with write access.
3. Open a terminal window
    * Windows: <kbd>START</kbd>+<kbd>R</kbd> and then type `cmd` in the dialog box
    * Mac: <kbd>⌘</kbd>+<kbd>SPACE</kbd> and type `Terminal`
    * Ubuntu Linux (some flavors): <kbd>CTRL</kbd>+<kbd>ALT</kbd>+<kbd>T</kbd>
4. Navigate to the folder where the files have been extracted to (the folder will have the file setup.py in it).
5. Install nestor using the command `pip install . ` (please note the "." is part of the command)
6. (Optional Step) Type in `pip install .[dash]` to install the Nestor Dashboard.

