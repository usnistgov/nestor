import holoviews as hv
# import pandas as pd
# from nestor.tagplots import tag_relation_net, color_opts
from pathlib import Path
from subprocess import call, Popen

# import numpy as np
# from itertools import product


class DataModel:
    """for now mostly a placeholder. eventually used to connect to database backend"""

    def __init__(self):
        print('instantiating data connection service')
        self.fname = None

    def set_data_location(self, fname):
        self.fname = fname
        print(f'data location set to {fname}')

    def serve_data(self):
        assert self.fname != None, 'File has not been assigned! Raising error...'

        proc = Popen(['python', str(Path(__file__).parent/"plotserve.py"), self.fname])
        return proc

