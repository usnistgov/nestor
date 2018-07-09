import os
from setuptools import setup, find_packages
import configparser
from subprocess import Popen, PIPE


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...


CONFIG_FILE = 'setup.cfg'


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname), encoding='utf-8').read()


def get_version():
    """
    Returns project version as string from 'git describe' command.
    """
    pipe = Popen('git describe --tags --always', stdout=PIPE, shell=True)
    version = pipe.stdout.read()
    if version:
        return version.decode('utf-8').lstrip('v').rstrip()
    else:
        return 'X.Y'

print(get_version())

def run_setup(packages, install_requires, extras_require):
    # populate the version_info dictionary with values stored in the version file
    # print(packages)
    setup(
        name = "Nestor",
        version = get_version(),
        author = "Thurston Sexton",
        author_email = "thurston.sexton@nist.gov",
        description = ("Quantifying tacit human knowledge for Smart Manufacturing Maintenance,\
                        for maintnenance-based investigatory analysis"),
        keywords = "nlp smart manufacturing maintenance tag app",
        url = "https://github.com/usnistgov/nestor",
        packages=packages,
        long_description=read('README.rst'),
        classifiers=[
            "Development Status :: 2 - Pre-Alpha",
            'Intended Audience :: Science/Research'
            'Intended Audience :: Manufacturing',
            'Topic :: Scientific/Engineering :: Information Analysis',
            'Programming Language :: Python :: 3',
        ],
        install_requires=install_requires,
        extras_require=extras_require,
        include_package_data=True,
        zip_safe=False
    )


config = configparser.ConfigParser()

try:
    with open(CONFIG_FILE) as f:
        config.read_file(f)
except IOError:
    print("Could not open config file.")

# packages = ['nestor',
#             'nestor/_database_storage',
#             'nestor/datasets']
packages = find_packages(exclude='database_storage')

install_requires = ['numpy>=1.14.2',
                    'pandas>=0.22.0',
                    'scikit-learn',
                    'tqdm>=4.23.0'
                    ]
extras_require = {'gui': ['pyqt5', 'pyyaml', 'chardet',
                          'seaborn>=0.8.1', 'matplotlib>=2.2.2',
                          'fuzzywuzzy', 'python-levenshtein'],
                  'tree': ['networkx'],
                  'plot': ['bokeh', 'holoviews']}

extras_require['all'] = extras_require['gui'] + extras_require['tree'] + extras_require['plot']


# if config.getboolean('gui', 'use'):
#     packages.append('nestor._ui')

run_setup(packages, install_requires, extras_require)
