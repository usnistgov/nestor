Installation
------------

This guide helps you to install the Tagging Tool App onto your computer. There are two modes for installation. They are as follows.

Install from PyPI
~~~~~~~~~~~~~~~~~
(This will do a cloud install to your python installation directory)

1. Open a command line terminal 

:Linux:		``Ctrl`` + ``Alt`` + ``T``
:Windows:	``Windows`` + ``R`` -> Type 'cmd'
:Mac: 		``⌘`` + ``Space`` -> Type 'Terminal'

2. Type in ``pip install nestor`` and wait for the install to complete


Install using local archive
~~~~~~~~~~~~~~~~~~~~~~~~~~~
(This will be a local install downloaded from a `recent source code release on GitHub <https://github.com/usnistgov/nestor/releases>`__)

1. Download the .zip file of the entire **nestor** installation from `the Github repository <https://github.com/usnistgov/nestor/archive/master.zip>`__

2. Extract the files to a directory, preferably with write access.

3. Open a terminal window and navigate to the folder where the files have been extracted to.

4. Install **nestor** using the command ``pip install .[options]``, where options is one of


:``gui``: To install additional dependancies needed to install the user interface
:``all``: To install the entire set of dependancies to enable network analysis and visualization functions


How to automatically build documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A version of the documentation for Nestor is hosted at `Readthedocs <http://nestor.readthedocs.io/en/latest/>`__. 
However you may build a local version if required.

1. After installing Nestor using any of the above means, navigate to the installation directory and install the `Sphinx <http://www.sphinx-doc.org/en/master/>`__ dependancies by typing in ``pip install -r requirements/doc.txt``

2. To build HTML documentation navigate into the ``docs`` subdirectory of Nestor and run ``make html``. The HTML source code will be created in ``nestor/_build/html`` and can be opened with the index.html file in a browser.

3. To build PDF documentation `LaTeX <https://www.latex-project.org/get/>`__ must be installed. As above, run ``make latex`` and navigate into the ``nestor/_build/latex`` directory. Run ``pdflatex nestor.tex``.