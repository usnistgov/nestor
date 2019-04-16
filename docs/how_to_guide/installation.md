Installation
============

This guide helps you to install Nestor onto your computer. There are two
modes for installation. They are as follows.

Install from PyPI (Recommended)
-------------------------------

This will do a cloud install to your python installation directory.

1.  Open a command line terminal

Linux
:   `Ctrl` + `Alt` + `T`

Windows
:   `Windows` + `R` -\> Type \'cmd\'

Mac
:   `⌘` + `Space` -\> Type \'Terminal\'

2.  Type in `pip install nist-nestor` and wait for the install to
    complete. This installs the Graphical User Interface (GUI) for the
    Nestor Tagging Tool.
3.  (Optional Step) Type in `pip install nist-nestor[dash]` to also
    install the Nestor Dashboard (Under Development!).

Install using local archive
---------------------------

This is necessary **only** if you did not install using the above method
(using PyPI).

This will be a local install downloaded from a [recent source code
release on GitHub](https://github.com/usnistgov/nestor/releases)

1.  Download the [.zip file](https://github.com/usnistgov/nestor/releases) of the entire
    **nestor** installation from the Github repository
2.  Extract the files to a directory, preferably with write access.
3.  Open a terminal window

Linux

:   `Ctrl` + `Alt` + `T`

Windows

:   `Windows` + `R` -\> Type \'cmd\'

Mac

:   `⌘` + `Space` -\> Type \'Terminal\'

4.  Navigate to the folder where the files have been extracted to (the
    folder will have the file setup.py in it).
5.  Install **nestor** using the command `pip install .` (please note
    the \".\" is part of the command)
6.  (Optional Step) Type in `pip install .[dash]` to install the Nestor
    Dashboard (Under Development!).

How to automatically build documentation (Optional)
---------------------------------------------------

This section is useful for developers of Nestor.

A version of the documentation for Nestor is hosted at
[Readthedocs](http://nestor.readthedocs.io/en/latest/). However you may
build a local version if required.

1.  If Nestor is not installed and you want to build a local version of
    the documentation, you can run `pip install .[docs]`. If Nestor is
    already installed, navigate to the installation directory and
    install the [Sphinx](http://www.sphinx-doc.org/en/master/)
    dependancies by typing in `pip install -r requirements/doc.txt`
2.  To build HTML documentation navigate into the `docs` subdirectory of
    Nestor and run `make html`. The HTML source code will be created in
    `nestor/_build/html` and can be opened with the index.html file in a
    browser.
3.  To build PDF documentation
    [LaTeX](https://www.latex-project.org/get/) must be installed. As
    above, run `make latex` and navigate into the `nestor/_build/latex`
    directory. Run `pdflatex nestor.tex`.
