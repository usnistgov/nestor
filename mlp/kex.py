import numpy as np
import pandas as pd
from tqdm import tqdm_notebook as tqdm
from pathlib import Path

import dask.dataframe as dd
import dask
import re
import sys
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.base import TransformerMixin
from sklearn.utils.validation import check_is_fitted, NotFittedError
from itertools import product


class Transformer(TransformerMixin):
    """
    Base class for pure transformers that don't need a fit method (returns self)
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

    def __init__(self, columns=0, special_replace=None):
        """
        Parameters
        ----------
        columns: int, or list of int or str.
            corresponding columns in X to extract, clean, and merge
        """

        self.columns = columns
        self.special_replace = special_replace
        # self.to_np = to_np

    def get_params(self, deep=True):
        return dict(columns=self.columns,
                    names=self.names,
                    special_replace=self.special_replace)

    def transform(self, X, y=None):
        if isinstance(self.columns, list):  # user passed a list of column labels
            if all([isinstance(x, int) for x in self.columns]):
                nlp_cols = list(X.columns[self.columns])  # select columns by user-input indices
            elif all([isinstance(x, str) for x in self.columns]):
                nlp_cols = self.columns  # select columns by user-input names
            else:
                print("Select error: mixed or wrong column type.")  # can't do both
                raise Exception
        elif isinstance(self.columns, int):  # take in a single index
            nlp_cols = [X.columns[self.columns]]
        else:
            nlp_cols = [self.columns]  # allow...duck-typing I guess? Don't remember.

        raw_text = X.loc[:, nlp_cols].fillna('')  # fill nan's
        if len(self.columns) > 1:  # more than one column, concat them
            raw_text = raw_text.add(' ').sum(axis=1).str[:-1]
        raw_text = raw_text.str.lower()  # all lowercase
        raw_text = raw_text.str.replace('\n', ' ')  # no hanging newlines

        # No punctuation
        raw_text = raw_text.str.replace('[{}]'.format(string.punctuation), ' ')
        if self.special_replace is not None:
            rx = re.compile('|'.join(map(re.escape, self.special_replace)))
            # allow user-input special replacements.
            raw_text = raw_text.str.replace(rx, lambda match: self.special_replace[match.group(0)])
        return raw_text


class TokenExtractor(TransformerMixin):

    def __init__(self, **tf_idfkwargs):

        self.default_kws = dict({'input': 'content',
                                 'ngram_range': (1, 1),
                                 'stop_words': 'english',
                                 'sublinear_tf': True,
                                 'smooth_idf': False,
                                 'max_features': 5000})

        self.default_kws.update(tf_idfkwargs)
        # super(TfidfVectorizer, self).__init__(**tf_idfkwargs)
        self._model = TfidfVectorizer(**self.default_kws)


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
        ranks = self._tf_tot.argsort()[::-1]
        if len(ranks) > self.default_kws['max_features']:
            ranks = ranks[:self.default_kws['max_features']]
        return ranks

    @property
    def vocab_(self):
        extracted_toks = np.array(self._model.get_feature_names())[self.ranks_]
        return extracted_toks

    @property
    def scores_(self):
        scores = self._tf_tot[self.ranks_]
        return scores/scores.sum()

    def annotation_assistant(self, filename=None, init=None):
        try:
            check_is_fitted(self, '_model', 'The tfidf vector is not fitted')
        except NotFittedError:
            if (filename is not None) and Path(filename).is_file():
                print('No model fitted, but file already exists. Importing...')
                return pd.read_csv(filename, index_col=0)
            else:
                raise

        df = pd.DataFrame({'tokens': self.vocab_,
                           'NE': '',
                           'alias': '',
                           'notes': '',
                           'score': self.scores_})[['tokens', 'NE', 'alias', 'notes', 'score']]
        df = df[~df.tokens.duplicated(keep='first')]
        df.set_index('tokens', inplace=True)

        if init is None:
            if (filename is not None) and Path(filename).is_file():
                init = filename
                print('attempting to initialize with pre-existing vocab')

        if init is not None:
            df.NE = np.nan
            df.alias = np.nan
            df.notes = np.nan
            df_import = pd.read_csv(init, index_col=0)
            df.update(df_import)
            print('intialized successfully!')
            df.fillna('', inplace=True)


        if filename is not None:
            df.to_csv(filename)
            print('saved locally!')
        return df


def _series_itervals(s):
    for n, val in s.iteritems():
        yield val


def annotation_app(fname):
    import PyQt5.QtWidgets as qw
    from app.test_app import MyWindow
    app = 0
    app = qw.QApplication(sys.argv)
    # if not qw.QApplication.instance():
    #     app = qw.QApplication(sys.argv)
    # else:
    #     app = qw.QApplication.instance()
    window = MyWindow(vocab_filename=fname)
    window.show()
    sys.exit(app.exec_())


def tag_extractor(tex, raw_text, toks, vocab):
    v_filled = vocab.fillna({'NE': 'NA',  # TODO make this optional
                             'alias': vocab.index.to_series()}) # we want NA?
    # make a df with one column per clf of tag
    tags = {typ: pd.DataFrame(index=range(len(raw_text))) for typ in v_filled.NE.unique()}

    # loop over the unique alias' (i.e.e all tags, by classification
    for clf, queries in tqdm(v_filled.groupby('NE').alias.unique().iteritems(),
                                      desc='Category Loop', total=vocab.NE.nunique()):
        # loop over each tag, returning any instance where the alias matches
        for query in tqdm(queries, desc=clf + ' token loop', leave=True):
            to_map = v_filled.loc[v_filled.alias == query].index.tolist()
            query_idx = [tex._model.vocabulary_[i] for i in to_map]
            match = ((toks[:, query_idx]).toarray() > 0).any(axis=1).astype(int)

            # make a big dict with all of it together
            tags[clf][query] = match
    return tags


def tags_to_df(tags, idx_col=None):
    tag_df = pd.concat(tags.values(), axis=1, keys=tags.keys())
    if idx_col is not None:
        tag_df = tag_df.set_index(idx_col).sort_index()  # sort by idx
    return tag_df


def token_to_alias(raw_text, vocab):

    thes_dict = vocab[vocab.alias.replace('', np.nan).notna()].alias.to_dict()
    # print(thes_dict)
    substr = sorted(thes_dict, key=len, reverse=True)
    if substr:
        # matcher = lambda s: r'\b'+re.escape(s)+r'\b'
        # matcher = lambda s: re.escape(s)
        rx = re.compile(r'\b(' + '|'.join(map(re.escape, substr)) + r')\b')
        clean_text = raw_text.str.replace(rx, lambda match: thes_dict[match.group(0)])
    # clean_text.compute()[:4]
    else:
        clean_text=raw_text
    return clean_text

def ngram_automatch(vocab, voc2, NE_types, NE_map_rules):

    # first we need to substitute alias' for their NE identifier
    NE_dict = vocab.NE.replace('', np.nan).fillna('U').to_dict()
    NE_dict.update(vocab.fillna('U').reset_index()[['NE', 'alias']].drop_duplicates().set_index('alias').NE.to_dict())
    NE_sub = sorted(NE_dict, key=len, reverse=True)

    # matcher = lambda s: r'\b'+re.escape(s)+r'\b'
    # matcher = lambda s: re.escape(s)
    NErx = re.compile(r'\b(' + '|'.join(map(re.escape, NE_sub)) + r')\b')
    NE_text = voc2.index.str.replace(NErx, lambda match: NE_dict[match.group(0)])
    # now we have NE-soup/DNA of the original text.
    voc2.loc[:, 'NE'] = NE_text.tolist()

    # all combinations of NE types
    NE_map = {' '.join(i): '' for i in product(NE_types, repeat=2)}
    NE_map.update(NE_map_rules)
    # print(NE_map)
    # apply rule substitutions
    voc2['NE'] = voc2.NE.apply(lambda x: NE_map[x])  # special logic for custom NE type-combinations (config.yaml)
    # voc2['score'] = tex2.scores_  # should already happen?
    return voc2