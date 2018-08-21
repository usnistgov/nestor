Installation
------------

This guide helps you to install the Tagging Tool App onto your computer. There are two modes for installation. They are as follows. Please note, one install method (Install from PyPI) is coming soon as it is in development.


Install using local archive
~~~~~~~~~~~~~~~~~~~~~~~~~~~
(This will be a local install downloaded from a `recent source code release on GitHub <https://github.com/usnistgov/nestor/releases>`__)

1. Download the `.zip file <https://github.com/usnistgov/nestor/releases>`__ of the entire **nestor** installation from the Github repository 

2. Extract the files to a directory, preferably with write access.

3. Open a terminal window 

:Linux:      ``Ctrl`` + ``Alt`` + ``T``
:Windows: 	 ``Windows`` + ``R`` -> Type 'cmd'
:Mac: 		 ``⌘`` + ``Space`` -> Type 'Terminal'

4. Navigate to the folder where the files have been extracted to (the folder will have the file setup.py in it).

5. Install **nestor** using the command ``pip install .`` 


How to automatically build documentation (Optional)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A version of the documentation for Nestor is hosted at `Readthedocs <http://nestor.readthedocs.io/en/latest/>`__. 
However you may build a local version if required. 

1. If Nestor is not installed and you want to build a local version of the documentation, you can run ``pip install .[docs]``. If Nestor is already installed, navigate to the installation directory and install the `Sphinx <http://www.sphinx-doc.org/en/master/>`__ dependancies by typing in ``pip install -r requirements/doc.txt``

2. To build HTML documentation navigate into the ``docs`` subdirectory of Nestor and run ``make html``. The HTML source code will be created in ``nestor/_build/html`` and can be opened with the index.html file in a browser.

3. To build PDF documentation `LaTeX <https://www.latex-project.org/get/>`__ must be installed. As above, run ``make latex`` and navigate into the ``nestor/_build/latex`` directory. Run ``pdflatex nestor.tex``.


Install from PyPI (Coming Soon)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 (This will do a cloud install to your python installation directory)

1. Open a command line terminal


:Linux:      ``Ctrl`` + ``Alt`` + ``T``
:Windows: 	 ``Windows`` + ``R`` -> Type 'cmd'
:Mac: 		 ``⌘`` + ``Space`` -> Type 'Terminal'

2. Type in ``pip install nestor`` and wait for the install to complete