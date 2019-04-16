# import holoviews as hv
import pandas as pd
# from nestor.tagplots import tag_relation_net, color_opts
from pathlib import Path
from subprocess import call, Popen
from itertools import product
import nestor

nestorParams = nestor.CFG

# import numpy as np
# from itertools import product


class DataModel:
    """for now mostly a placeholder. eventually used to connect to database backend"""

    def __init__(self):
        print('instantiating data connection service')
        self._fname = None
        self._data_names = None

    @property
    def data_names(self):
        """which data column names are being served"""
        return self._data_names

    @data_names.setter
    def data_names(self, colnames):
        data = [name for name in colnames
                if name in list(nestorParams.datatype_search('name'))]
        self._data_names = data
        print(
            'Found valid data columns: \n',
            self.data_pprint
        )

    @property
    def data_pprint(self):
        data = self._data_names
        return [nestorParams._datatypes.get(name) for name in data]

    @property
    def fname(self):
        """I'm the 'x' property."""
        return self._fname

    @fname.setter
    def fname(self, fname):
        self._fname = fname
        print(f'data location set to {fname}')

        with pd.HDFStore(fname, 'r') as store:
            self.data_names = store.select('df', stop=1).columns

    def serve_data(self):
        assert self.fname is not None, 'File has not been assigned! Raising error...'
        exec_loc = Path(__file__).parent/"plotserve.py"
        proc = Popen(['python', str(exec_loc), str(self.fname)])
        return proc

