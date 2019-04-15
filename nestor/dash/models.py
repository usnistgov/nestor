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
        self.fname = None
        self.data_names = None

    def set_data_location(self, fname):
        self.fname = fname
        print(f'data location set to {fname}')
        with pd.HDFStore(fname, 'r') as store:
            colnames = store.select('df', stop=1).columns
        self.data = [i for i in colnames if i in nestorParams._datatypes.keys()]
        self.data_names = [nestorParams._datatypes.get(name) for name in self.data]

        print('Found valid data columns: \n', self.data_names)

    def serve_data(self):
        assert self.fname != None, 'File has not been assigned! Raising error...'
        exec_loc = Path(__file__).parent/"plotserve.py"
        proc = Popen(['python', str(exec_loc), str(self.fname)])
        return proc

