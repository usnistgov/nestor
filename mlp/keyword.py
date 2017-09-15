"""
author: Thurston Sexton
"""

from mlp.tools import *

import numpy as np
import pandas as pd
from tqdm import tqdm
import sys
import textacy

class KeywordExtractor(object):

    def __init__(self, wdir='data'):
        """

        :param wdir:
        """
        self.data_directory = os.path.join(os.getcwd(), 'data')
        self.raw_excel_filepath = None

    def _load_xlsx(self, xlsx_fname):
        self.raw_excel_filepath = os.path.join(self.data_directory, xlsx_fname)

    def fit(self,
            nlp_cols={'RawText':0},
            meta_cols={},
            xlsx_fname=None,
# TODO: NEED TO OPTIMIZE SELECTION OF COLS AND NAMES
            keep_temp_files=True):
        # assert len(nlp_cols)==len(nlp_col_names), 'length of nlp_cols and nlp_col_names must match!'
        # assumed = {
        #     'nlp_cols': [0],
        #     'meta_cols': [1],
        #     'xlsx_fname': None
        # }
        # assumed.update(kwargs)

        if self.raw_excel_filepath is None:
            assert xlsx_fname is not None, 'Please provide an xlsx_fname kwarg,' \
                                           'or call <self>._load_xlsx() prior to fit().'
            self._load_xlsx(xlsx_fname)




