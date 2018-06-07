import os
from setuptools import setup
import configparser

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...


CONFIG_FILE = 'setup.cfg'

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

def run_setup(packages):
    # populate the version_info dictionary with values stored in the version file

    setup(
        name = "nestor",
        version = "0.2.1",
        author = "Thurston Sexton",
        author_email = "thurston.sexton@nist.gov",
        description = ("Quantifying tacit human knowledge with python,\
                        for maintnenance-based investigatory analysis"),
        keywords = "example documentation tutorial",
        url = "http://packages.python.org/an_example_pypi_project",
        packages=packages,
        long_description=read('README'),
        classifiers=[
            "Development Status :: 2 - Pre-Alpha",
            'Intended Audience :: Science/Research/Industry',
            'Programming Language :: Python :: 3',
        ],
    )




config = configparser.ConfigParser()
try:
    with open(CONFIG_FILE) as f:
        config.read_file(f)
except IOError:
    print("Could not open config file.")

packages = ['nestor']
if config.getboolean('GUI', 'use'):
    packages.append('nestor.ui')

run_setup(packages)