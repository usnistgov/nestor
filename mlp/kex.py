"""
author: Thurston Sexton
"""
import numpy as np
import pandas as pd
from tqdm import tqdm
from pathlib import Path

# import dask.dataframe as dd
# import dask
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
        # if len(nlp_cols) > 1:  # more than one column, concat them
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


def generate_vocabulary_df(transformer, filename=None, init=None):
    """
    Helper method to create a formatted pandas.DataFrame and/or a .csv containing
    the token--tag/alias--classification relationship. Formatted as jargon/slang tokens,
    the Named Entity classifications, preferred labels, notes, and tf-idf summed scores:

    tokens | NE | alias | notes | scores

    This is intended to be filled out in excel or using the Tagging Tool.

    Parameters
    ----------
    transformer: object TokenExtractor
        the (TRAINED) token extractor used to generate the ranked list of vocab.
    filename: str, optional
        the file location to read/write a csv containing a formatted vocabulary list
    init: str or pandas.Dataframe, optional
        file location of csv or dataframe of existing vocab list to read and update
        token classification values from

    Returns
    -------
    vocab: pandas.Dataframe
        the correctly formatted vocabulary list for token:NE, alias matching
    """

    try:
        check_is_fitted(transformer._model, 'vocabulary_', 'The tfidf vector is not fitted')
    except NotFittedError:
        if (filename is not None) and Path(filename).is_file():
            print('No model fitted, but file already exists. Importing...')
            return pd.read_csv(filename, index_col=0)
        elif (init is not None) and Path(init).is_file():
            print('No model fitted, but file already exists. Importing...')
            return pd.read_csv(init, index_col=0)
        else:
            raise

    df = pd.DataFrame({'tokens': transformer.vocab_,
                       'NE': '',
                       'alias': '',
                       'notes': '',
                       'score': transformer.scores_})[['tokens', 'NE', 'alias', 'notes', 'score']]
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
        if isinstance(init, Path) and init.is_file():  # filename is passed
            df_import = pd.read_csv(init, index_col=0)
        else:  # assume input pandas df
            df_import = init.copy()
        df.update(df_import)
        print('intialized successfully!')
        df.fillna('', inplace=True)


    if filename is not None:
        df.to_csv(filename)
        print('saved locally!')
    return df


def _series_itervals(s):
    """wrapper that turns a pandas/dask dataframe into a generator of values only (for sklearn)"""
    for n, val in s.iteritems():
        yield val


def _get_readable_tag_df(tag_df):
    """ helper function to take binary tag co-occurrence matrix and make comma-sep readable columns"""
    temp_df = pd.DataFrame(index=tag_df.index)  # empty init
    for clf, clf_df in tag_df.drop('NA', axis=1).T.groupby(level=0):  # loop over top-level classes (ignore NA)
        join_em = lambda strings: ', '.join([x for x in strings if x != ''])  # func to join str
        strs = np.where(clf_df.T == 1, clf_df.T.columns.droplevel(0).values, '').T
        temp_df[clf] = pd.DataFrame(strs).apply(join_em)
    return temp_df


def _get_tag_completeness(tag_df):
    """get tagging statistic/array, as the completeness ratio for each MWO"""
    tag_pct = 1-(tag_df['NA'].sum(axis=1)/tag_df.sum(axis=1))
    print(f'Tag completeness: {tag_pct.mean():.2f} +/- {tag_pct.std():.2f}')

    tag_comp = (tag_df['NA'].sum(axis=1) == 0).sum()
    print(f'Complete Docs: {tag_comp}, or {tag_comp/len(tag_df):.2%}')

    tag_empt = ((tag_df['I'].sum(axis=1) == 0) & (tag_df['P'].sum(axis=1) == 0) & (tag_df['S'].sum(axis=1) == 0)).sum()
    print(f'Empty Docs: {tag_empt}, or {tag_empt/len(tag_df):.2%}')
    return tag_pct, tag_comp, tag_empt


def tag_extractor(transformer, raw_text, vocab_df=None, readable=False):
    """
    Wrapper for the TokenExtractor to streamline the generation of tags from text.
    Determines the documents in <raw_text> that contain each of the tags in <vocab>,
    using a TokenExtractor transformer object (i.e. the tfidf vocabulary).

    As implemented, this function expects an existing transformer object, though in
    the future this will be changed to a class-like functionality (e.g. sklearn's
    AdaBoostClassifier, etc) which wraps a transformer into a new one.

    Parameters
    ----------
    transformer: object KeywordExtractor
        instantiated, can be pre-trained
    raw_text: pandas.Series
        contains jargon/slang-filled raw text to be tagged
    vocab_df: pandas.DataFrame, optional
        An existing vocabulary dataframe or .csv filename, expected in the format of
        kex.generate_vocabulary_df().
    readable: bool, default False
        whether to return readable, categorized, comma-sep str format (takes longer)

    Returns
    -------
    pandas.DataFrame, extracted tags for each document, whether binary indicator (default)
    or in readable, categorized, comma-sep str format (readable=True, takes longer)
    """

    try:
        check_is_fitted(transformer._model, 'vocabulary_', 'The tfidf vector is not fitted')
        toks = transformer.transform(raw_text)
    except NotFittedError:
        toks = transformer.fit_transform(raw_text)

    vocab = generate_vocabulary_df(transformer, init=vocab_df)

    v_filled = vocab.replace({'NE':{'':np.nan},
                              'alias':{'':np.nan}}).fillna({'NE': 'NA',  # TODO make this optional
                                                            'alias': vocab.index.to_series()})  # we want NA?
    # make a df with one column per clf of tag
    tags = {typ: pd.DataFrame(index=range(len(raw_text))) for typ in v_filled.NE.unique()}

    # loop over the unique alias' (i.e.e all tags, by classification
    groups = v_filled.groupby('NE').alias.unique().iteritems()
    with tqdm(total=vocab.NE.nunique(), file=sys.stdout, position=0) as pbar1:
        for clf, queries in groups:
            # loop over each tag, returning any token where the alias matches
            pbar1.set_description(f'Category: {clf}')
            pbar1.update(1)
            with tqdm(total=len(queries), file=sys.stdout, position=1, leave=False) as pbar2:
                for query in queries:
                    # pbar2.set_description(clf + ' token loop'
                    pbar2.update(1)
                    to_map = v_filled.loc[v_filled.alias == query].index.tolist()  # the tokens
                    query_idx = [transformer._model.vocabulary_[i] for i in to_map]
                    # make a binary indicator for the tag, 1 if any of the tokens occurred, 0 if not.
                    match = ((toks[:, query_idx]).toarray() > 0).any(axis=1).astype(int)

                    # make a big dict with all of it together
                    tags[clf][query] = match

    def tags_to_df(tags, idx_col=None):
        tag_df = pd.concat(tags.values(), axis=1, keys=tags.keys())
        if idx_col is not None:  # not used currently...let the user do this himself
            tag_df = tag_df.set_index(idx_col).sort_index()  # sort by idx
        return tag_df

    tag_df = tags_to_df(tags)

    if readable:
        tag_df = _get_readable_tag_df(tag_df)

    return tag_df


def token_to_alias(raw_text, vocab):
    """
    Replaces known tokens with their "tag" form, i.e. the alias' in some
    known vocabulary list

    Parameters
    ----------
    raw_text: pandas.Series
        contains text with known jargon, slang, etc
    vocab: pandas.DataFrame
        contains alias' keyed on known slang, jargon, etc.

    Returns
    -------
    pd.Series
        new text, with all slang/jargon replaced with unified representations
    """
    thes_dict = vocab[vocab.alias.replace('', np.nan).notna()].alias.to_dict()
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


def ngram_automatch(voc1, voc2, NE_types, NE_map_rules):

    vocab = voc1.copy()
    vocab.NE.replace('', np.nan, inplace=True)
    # first we need to substitute alias' for their NE identifier
    NE_dict = vocab.NE.fillna('U').to_dict()
    NE_dict.update(vocab.fillna('U').reset_index()[['NE', 'alias']].drop_duplicates().set_index('alias').NE.to_dict())
    NE_sub = sorted(NE_dict, key=len, reverse=True)
    print(NE_sub)
    # print(r'\b(' + '|'.join(map(re.escape, NE_sub)) + r')\b')
    NErx = re.compile(r'\b(' + '|'.join(map(re.escape, NE_sub)) + r')\b')
    NE_text = voc2.index.str.replace(NErx, lambda match: NE_dict[match.group(0)])
    # print(NE_text)
    # now we have NE-soup/DNA of the original text.
    mask = voc2.alias.replace('', np.nan).isna() # don't overwrite the NE's the user has input (i.e. alias != NaN)
    voc2.loc[mask, 'NE'] = NE_text[mask].tolist()

    # all combinations of NE types
    NE_map = {' '.join(i): '' for i in product(NE_types, repeat=2)}
    NE_map.update(NE_map_rules)

    # apply rule substitutions
    voc2.loc[mask, 'NE'] = voc2.loc[mask, 'NE'].apply(lambda x: NE_map[x])  # special logic for custom NE type-combinations (config.yaml)
    # voc2['score'] = tex2.scores_  # should already happen?
    return voc2