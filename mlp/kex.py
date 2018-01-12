import numpy as np
import pandas as pd
from tqdm import tqdm
from pathlib import Path

import dask.dataframe as dd
import dask
import sys
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.base import TransformerMixin
from sklearn.utils.validation import check_is_fitted


class Transformer(TransformerMixin):
    """
    Base class for pure transformers that don't need a fit method
    """

    def fit(self, X, y=None, **fit_params):
        return self

    def transform(self, X, **transform_params):
        return X

    def get_params(self, deep=True):
        return dict()


class NLPSelect(Transformer):
    """
    Extract specified natural language columns from
    a dask df, and combine into a single dask series.
    """

    def __init__(self, columns=0):
        """
        Parameters
        ----------
        columns: int, or list of int or str.
            corresponding columns in X to extract, clean, and merge
        """

        self.columns = columns
        # self.to_np = to_np

    def get_params(self, deep=True):
        return dict(columns=self.columns, names=self.names)

    def transform(self, X, y=None):
        if isinstance(self.columns, list):
            if all([isinstance(x, int) for x in self.columns]):
                nlp_cols = list(X.columns[self.columns])
            elif all([isinstance(x, str) for x in self.columns]):
                nlp_cols = self.columns
            else:
                print("Select error: mixed or wrong column type.")
                raise Exception
        elif isinstance(self.columns, int):
            nlp_cols = [X.columns[self.columns]]
        else:
            nlp_cols = [self.columns]

        raw_text = X.loc[:, nlp_cols].fillna('')  # fill nan's
        if len(self.columns) > 1:  # more than one column, cat them
            raw_text = raw_text.add(' ').sum(axis=1).str[:-1]
        raw_text = raw_text.str.lower()  # all lowercase
        raw_text.str.replace('\n', ' ')  # no hanging newlines

        # No punctuation
        raw_text = raw_text.str.replace('[{}]'.format(string.punctuation), ' ')
        return raw_text


class TokenExtractor(TransformerMixin):

    def __init__(self, **tf_idfkwargs):

        self.default_kws = dict({'input': 'content',
                                 'ngram_range': (1, 1),
                                 'stop_words': 'english',
                                 'sublinear_tf': True,
                                 'smooth_idf': False})

        self.default_kws.update(tf_idfkwargs)
        # super(TfidfVectorizer, self).__init__(**tf_idfkwargs)
        self._model = TfidfVectorizer(self.default_kws)

        # super(TokenExtractor, self).__init__(input=input,
        #                                       ngram_range=ngram_range,
        #                                       stop_words=stop_words,
        #                                       sublinear_tf=sublinear_tf,
        #                                       smooth_idf=smooth_idf,
        #                                       **kwargs)

    # def fit(self, X, y=None, **fit_params):
    #     raw_documents = _series_itervals(X)
    #     self.model.fit(raw_documents)
    #     return self
    #
    # def transform(self, dask_documents, y=None):
    #     raw_documents = _series_itervals(dask_documents)
    #     return self.model.transform(raw_documents)
        # if wdir is None:
        #     wdir = Path('.') / 'data'
        # self.data_directory = wdir
        # self.vocab = None
        # self.df = None
        #
        # if nlp_cols is None:
        #     nlp_cols = {'RawText': 0}
        #
        # if meta_cols is not None:
        #     relevant_data = dict(nlp_cols, **meta_cols)
        #     relevant_names, relevant_cols = tuple(map(list, zip(*relevant_data.items())))
        # else:
        #     relevant_names, relevant_cols = tuple(map(list, zip(*nlp_cols.items())))
        #     meta_cols = {}
        #
        # default_pd_kws = {
        #     'header':0,
        #     'encoding':'utf-8'
        # }  # privide some default assumptions
        # if df_kws is not None:
        #     default_pd_kws.update(df_kws)

    def fit(self, dask_documents, y=None):
        X = _series_itervals(dask_documents)
        self._model.fit(X)
        return self

    def fit_transform(self, dask_documents, y=None):
        X = _series_itervals(dask_documents)
        # X is already a transformed view of dask_documents so
        # we set copy to False
        X_tf = self._model.fit_transform(X)
        self._tf_tot = np.array(X_tf.sum(axis=0))[0]
        return X_tf

    def transform(self, dask_documents, copy=True):

        check_is_fitted(self, '_model', 'The tfidf vector is not fitted')

        X = _series_itervals(dask_documents)
        X_tf = self._model.transform(X, copy=False)
        self._tf_tot = np.array(X_tf.sum(axis=0))[0]
        return X_tf

    @property
    def ranks_(self):
        return self._tf_tot.argsort()[::-1]

    @property
    def vocab_(self):
        return np.array(self._model.get_feature_names())[self.ranks_]

    @property
    def scores_(self):
        return self._tf_tot[self.ranks_]

    def annotation_assistant(self,
                             filename,
                             gui=True):
        if not Path(filename).is_file():
            check_is_fitted(self, '_model', 'The tfidf vector is not fitted')

            df = pd.DataFrame({'tokens': self.vocab_,
                               'NE': '',
                               'alias': '',
                               'notes': ''})[['tokens', 'NE', 'alias', 'notes']]
            df.to_csv(filename, index=False)
            print(f'New Vocab. file written to {filename}')
            if gui:
                annotation_app(filename)
        elif gui:
            print('opening pre-existing vocab file in the GUI...')
            annotation_app(filename)
        else:
            print('file already exists, please enter a new filename or start the GUI!')
            raise Exception


def _series_itervals(s):
    for n, val in s.iteritems():
        yield val


def annotation_app(fname):
    import PyQt5.QtWidgets as qw
    from app.test_app import MyWindow

    app = qw.QApplication(sys.argv)
    window = MyWindow(vocab_filename=fname)
    window.show()
    sys.exit(app.exec_())
