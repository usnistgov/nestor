__author__ = "Thurston Sexton"

import nestor
import numpy as np
import pandas as pd
from pathlib import Path
import re, sys, string
from scipy.sparse import csc_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.base import TransformerMixin
from sklearn.utils.validation import check_is_fitted, NotFittedError
from itertools import product
from tqdm.autonotebook import tqdm

nestorParams = nestor.CFG

__all__ = [
    "NLPSelect",
    "TokenExtractor",
    "generate_vocabulary_df",
    "get_tag_completeness",
    "tag_extractor",
    "token_to_alias",
    "ngram_automatch",
    "ngram_keyword_pipe",
]


class _Transformer(TransformerMixin):
    """
    Base class for pure transformers that don't need a fit method (returns self)
    """
    
    def fit(self, X, y=None, **fit_params):
        return self

    def transform(self, X, **transform_params):
        return X

    def get_params(self, deep=True):
        return dict()


class NLPSelect(_Transformer):
    """
    Extract specified natural language columns
    
    Starting from a pd.DataFrame, combine `columns` into a single series
    containing lowercased text with punctuation and excess newlines removed.
    Using the `special_replace` dict allows for arbitrary mapping during the
    cleaning process, for e.g. a priori normalization.
    
    Args:
        columns(int,list of int,str): names/positions of data columns to extract, clean, and merge
        special_replace(dict,None): mapping from strings to normalized strings (known a priori)
        together(pd.Series): merged text, before any cleaning/normalization
        clean_together(pd.Series): merged text, after cleaning (output of `transform`)
    """

    def __init__(self, columns=0, special_replace=None):
        self.columns = columns
        self.special_replace = special_replace
        self.together = None
        self.clean_together = None
        # self.to_np = to_np

    def get_params(self, deep=True):
        """Retrieve parameters of the transformer for sklearn compatibility.

        Args:
          deep:  (Default value = True)

        Returns:

        """
        return dict(
            columns=self.columns, names=self.names, special_replace=self.special_replace
        )

    def transform(self, X, y=None):
        """get clean column of text from column(s) of raw text in a dataset
        
        Depending on which of Union[List[Union[int,str]],int,str]
        `self.columns` is, this will extract desired columns (of text) from
        positions, names, etc. in the original dataset `X`.
        
        Columns will be merged, lowercased, and have punctuation and hanging
        newlines removed.

        Args:
          X(pandas.DataFrome): dataset containing certain columns with natural language text.
          y(None, optional):  (Default value = None)

        Returns:
           clean_together(pd.Series): a single column of merged, cleaned text
        
        """
        if isinstance(self.columns, list):  # user passed a list of column labels
            if all([isinstance(x, int) for x in self.columns]):
                nlp_cols = list(
                    X.columns[self.columns]
                )  # select columns by user-input indices
            elif all([isinstance(x, str) for x in self.columns]):
                nlp_cols = self.columns  # select columns by user-input names
            else:
                print("Select error: mixed or wrong column type.")  # can't do both
                raise Exception
        elif isinstance(self.columns, int):  # take in a single index
            nlp_cols = [X.columns[self.columns]]
        else:
            nlp_cols = [self.columns]  # allow...duck-typing I guess? Don't remember.

        def _robust_cat(df, cols):
            """pandas doesn't like batch-cat of string cols...needs 1st col

            Args:
              df: 
              cols: 

            Returns:

            """
            if len(cols) <= 1:
                return df[cols].astype(str).fillna("").iloc[:, 0]
            else:
                return (
                    df[cols[0]]
                    .astype(str)
                    .str.cat(df.loc[:, cols[1:]].astype(str), sep=" ", na_rep="",)
                )

        def _clean_text(s, special_replace=None):
            """lower, rm newlines and punct, and optionally special words

            Args:
              s: 
              special_replace:  (Default value = None)

            Returns:

            """
            raw_text = (
                s.str.lower()  # all lowercase
                .str.replace("\n", " ")  # no hanging newlines
                .str.replace("[{}]".format(string.punctuation), " ")
            )
            if special_replace is not None:
                rx = re.compile("|".join(map(re.escape, special_replace)))
                # allow user-input special replacements.
                return raw_text.str.replace(
                    rx, lambda match: self.special_replace[match.group(0)]
                )
            else:
                return raw_text

        self.together = X.pipe(_robust_cat, nlp_cols)
        self.clean_together = self.together.pipe(
            _clean_text, special_replace=self.special_replace
        )
        return self.clean_together


class TokenExtractor(TransformerMixin):
    """A wrapper for the sklearn TfidfVectorizer class, with utilities for ranking by
       total tf-idf score, and getting a list of vocabulary.

       Valid options are given below from sklearn docs.

           
       """
    def __init__(
            self,
            input="content",
            ngram_range=(1,1),
            stop_words="english",
            sublinear_tf=True,
            smooth_idf=False,
            max_features=5000,
            **tfidf_kwargs
        ):
        """Initialize the extractor

        Args:
           input (string): {'filename', 'file', 'content'}
                If 'filename', the sequence passed as an argument to fit is
                expected to be a list of filenames that need reading to fetch
                the raw content to analyze.

                If 'file', the sequence items must have a 'read' method (file-like
                object) that is called to fetch the bytes in memory. 
                Otherwise the input is expected to be the sequence strings or
                bytes items are expected to be analyzed directly.
           ngram_range (tuple): (min_n, max_n), default=(1,1)
                The lower and upper boundary of the range of n-values for different
                n-grams to be extracted. All values of n such that min_n <= n <= max_n
                will be used.
           stop_words (string): {'english'} (default), list, or None
                If a string, it is passed to _check_stop_list and the appropriate stop
                list is returned. 'english' is currently the only supported string
                value.

                If a list, that list is assumed to contain stop words, all of which
                will be removed from the resulting tokens.
                Only applies if ``analyzer == 'word'``.

                If None, no stop words will be used. max_df can be set to a value
                in the range [0.7, 1.0) to automatically detect and filter stop
                words based on intra corpus document frequency of terms.
           max_features (int or None):
                If not None, build a vocabulary that only consider the top
                max_features ordered by term frequency across the corpus.
                This parameter is ignored if vocabulary is not None.
                (default=5000)
           smooth_idf (boolean):
                Smooth idf weights by adding one to document frequencies, as if an
                extra document was seen containing every term in the collection
                exactly once. Prevents zero divisions. (default=False)
           sublinear_tf (boolean): (Default value = True)
                Apply sublinear tf scaling, i.e. replace tf with 1 + log(tf).

           **tfidf_kwargs: other arguments passed to `sklearn.TfidfVectorizer`
        """ 
        self.default_kws = dict(
            {
                "input": input,
                "ngram_range": ngram_range,
                "stop_words": stop_words,
                "sublinear_tf": sublinear_tf,
                "smooth_idf": smooth_idf,
                "max_features": max_features,
            }
        )

        self.default_kws.update(tfidf_kwargs)
        self._model = TfidfVectorizer(**self.default_kws)
        self._tf_tot = None

    def fit_transform(self, X, y=None, **fit_params):
        """

        Args:
          X: 
          y:  (Default value = None)
          **fit_params: 

        Returns:

        
        """
        documents = _series_itervals(X)
        if y is None:
            X_tf = self._model.fit_transform(documents)
        else:
            X_tf = self._model.fit_transform(documents, y)
        self._tf_tot = np.array(X_tf.sum(axis=0))[0]
        return X_tf

    def fit(self, X, y=None):
        """

        Args:
          X: 
          y:  (Default value = None)

        Returns:

        
        """
        _ = self.fit_transform(X)
        return self

    def transform(self, dask_documents):
        """

        Args:
          dask_documents: 

        Returns:

        
        """

        check_is_fitted(self, "_model", "The tfidf vector is not fitted")

        X = _series_itervals(dask_documents)
        X_tf = self._model.transform(X)
        self._tf_tot = np.array(X_tf.sum(axis=0))[0]
        return X_tf

    @property
    def ranks_(self):
        r"""Retrieve the rank of each token, for sorting. Uses summed scoring over the
        TF-IDF for each token, so that: $S_t = \Sum_{d\text{TF-IDF}_t$

        Args:

        Returns:
           np.array: token ranks
        
        """
        check_is_fitted(self, "_model", "The tfidf vector is not fitted")
        ranks = self._tf_tot.argsort()[::-1]
        if len(ranks) > self.default_kws["max_features"]:
            ranks = ranks[: self.default_kws["max_features"]]
        return ranks

    @property
    def vocab_(self):
        """
        ordered list of tokens, rank-ordered by summed-tf-idf
        (see :func:`~nestor.keyword.TokenExtractor.ranks_`)

        Returns:
            numpy.array: extracted tokens
        """
        extracted_toks = np.array(self._model.get_feature_names())[self.ranks_]
        return extracted_toks

    @property
    def scores_(self):
        """
        Returns actual scores of tokens, for progress-tracking (min-max-normalized)

        Returns:
            numpy.array:
        """
        scores = self._tf_tot[self.ranks_]
        return (scores - scores.min()) / (scores.max() - scores.min())


def generate_vocabulary_df(transformer, filename=None, init=None):
    """ make correctly formatted entity vocabulary (token->tag+type)

    Helper method to create a formatted pandas.DataFrame and/or a .csv containing
    the token--tag/alias--classification relationship. Formatted as jargon/slang tokens,
    the Named Entity classifications, preferred labels, notes, and tf-idf summed scores:

    tokens | NE | alias | notes | scores
    --- | --- | --- | --- | ---
    myexample| I | example | "e.g"| 0.42

    This is intended to be filled out in excel or using the Tagging Tool UI

    - [`nestor-qt`](https://github.com/usnistgov/nestor-qt)
    - [`nestor-web`](https://github.com/usnistgov/nestor-web)

    Parameters:
        transformer (TokenExtractor): the (TRAINED) token extractor used to generate the ranked list of vocab.
        filename (str, optional) the file location to read/write a csv containing a formatted vocabulary list
        init (str or pd.Dataframe, optional): file location of csv or dataframe of existing vocab list to read and update
            token classification values from

    Returns:
        pd.Dataframe: the correctly formatted vocabulary list for token:NE, alias matching
    """

    try:
        check_is_fitted(
            transformer._model, "vocabulary_", "The tfidf vector is not fitted"
        )
    except NotFittedError:
        if (filename is not None) and Path(filename).is_file():
            print("No model fitted, but file already exists. Importing...")
            return pd.read_csv(filename, index_col=0)
        elif (init is not None) and Path(init).is_file():
            print("No model fitted, but file already exists. Importing...")
            return pd.read_csv(init, index_col=0)
        else:
            raise

    df = pd.DataFrame(
        {
            "tokens": transformer.vocab_,
            "NE": "",
            "alias": "",
            "notes": "",
            "score": transformer.scores_,
        }
    )[["tokens", "NE", "alias", "notes", "score"]]
    df = df[~df.tokens.duplicated(keep="first")]
    df.set_index("tokens", inplace=True)

    if init is None:
        if (filename is not None) and Path(filename).is_file():
            init = filename
            print("attempting to initialize with pre-existing vocab")

    if init is not None:
        df.NE = np.nan
        df.alias = np.nan
        df.notes = np.nan
        if isinstance(init, Path) and init.is_file():  # filename is passed
            df_import = pd.read_csv(init, index_col=0)
        else:
            try:  # assume input pandas df
                df_import = init.copy()
            except AttributeError:
                print("File not Found! Can't import!")
                raise
        df.update(df_import)
        # print('intialized successfully!')
        df.fillna("", inplace=True)

    if filename is not None:
        df.to_csv(filename)
        print("saved locally!")
    return df


def _series_itervals(s):
    """wrapper that turns a pandas/dask dataframe into a generator of values only (for sklearn)

    Args:
      s: 

    Returns:

    """
    for n, val in s.iteritems():
        yield val


def _get_readable_tag_df(tag_df):
    """helper function to take binary tag co-occurrence matrix and make comma-sep readable columns

    Args:
      tag_df: 

    Returns:

    """
    temp_df = pd.DataFrame(index=tag_df.index)  # empty init
    for clf, clf_df in tqdm(
        tag_df.T.groupby(level=0)
    ):  # loop over top-level classes (ignore NA)
        join_em = lambda strings: ", ".join(
            [x for x in strings if x != ""]
        )  # func to join str
        strs = np.where(clf_df.T == 1, clf_df.T.columns.droplevel(0).values, "").T
        temp_df[clf] = pd.DataFrame(strs).apply(join_em)
    return temp_df


def get_multilabel_representation(tag_df):
    """Turn binary tag occurrences into strings of comma-separated tags
    
    Given a hierarchical column-set of (entity-types, tag), where each row is
    a document and the binary-valued elements indicate occurrence
    (see `nestor.tag_extractor`), use this to get something a little more
    human-readable. Columns will be entity-types, with elements as
    comma-separated strings of tags.
    
    Uses some hacks, since categorical from strings tends to assume single (not
    multi-label) categories per-document. Likely to be re-factored in the future,
    but used for the `readable=True` flag in `tag_extractor`.

    Args:
      tag_df (pd.DataFrame): binary occurrence matrix from `tag_extractor` 

    Returns:
       pd.DataFrame: document matrix with columns of tag-types, elements of
       comma-separated tags of that type. 
    
    """
    return _get_readable_tag_df(tag_df)


def get_tag_completeness(tag_df):
    """completeness, emptiness, and histograms in-between
    
    It's hard to estimate "how good of a job you've done" at annotating your
    data. One way is to calculate the fraction of documents where all tokens
    have been mapped to their normalized form (a tag). Conversely, the fraction
    that have no tokens normalized, at all.
    
    Interpolating between those extremes, we can think of the Positive
    Predictive Value (PPV, also known as Precision) of our annotations: of the
    tokens/concepts not cleaned out (ostensibly, the *relevant* ones, how many
    have been retrieved (i.e. mapped to a known tag)?

    Args:
      tag_df (pd.DataFrame): hierarchical-column df containing

    Returns:
       tuple: tuple containing:

           tag_pct(pd.Series): PPV/precision for all documents, useful for e.g. histograms
           tag_comp(float): Fraction of documents that are *completely* tagged
           tag_empt(float): Fraction of documents that are completely *untagged*
    
    """

    all_empt = np.zeros_like(tag_df.index.values.reshape(-1, 1))
    tag_pct = 1 - (
        tag_df.get(["NA", "U"], all_empt).sum(axis=1) / tag_df.sum(axis=1)
    )  # TODO: if they tag everything?
    print(f"Tag completeness: {tag_pct.mean():.2f} +/- {tag_pct.std():.2f}")

    tag_comp = (tag_df.get("NA", all_empt).sum(axis=1) == 0).sum()
    print(f"Complete Docs: {tag_comp}, or {tag_comp/len(tag_df):.2%}")

    tag_empt = (
        (tag_df.get("I", all_empt).sum(axis=1) == 0)
        & (tag_df.get("P", all_empt).sum(axis=1) == 0)
        & (tag_df.get("S", all_empt).sum(axis=1) == 0)
    ).sum()
    print(f"Empty Docs: {tag_empt}, or {tag_empt/len(tag_df):.2%}")
    return tag_pct, tag_comp, tag_empt


def tag_extractor(
    transformer, raw_text, vocab_df=None, readable=False, group_untagged=True
):
    """Turn TokenExtractor instances and raw-text into binary occurrences.
    
    Wrapper for the TokenExtractor to streamline the generation of tags from text.
    Determines the documents in `raw_text` that contain each of the tags in `vocab_df`,
    using a TokenExtractor transformer object (i.e. the tfidf vocabulary).
    
    As implemented, this function expects an existing transformer object, though in
    the future this may be changed to a class-like functionality (e.g. sklearn's
    AdaBoostClassifier, etc) which wraps a transformer into a new one.

    Args:
       transformer (object KeywordExtractor): instantiated, can be pre-trained
       raw_text (pd.Series): contains jargon/slang-filled raw text to be tagged
       vocab_df (pd.DataFrame, optional): An existing vocabulary dataframe or .csv filename, expected in the format of
           kex.generate_vocabulary_df(). (Default value = None)
       readable (bool, optional): whether to return readable, categorized, comma-sep str format (takes longer) (Default value = False)
       group_untagged (bool, optional):  whether to group untagged tokens into a catch-all "_untagged" tag

    Returns:
       pd.DataFrame: extracted tags for each document, whether binary indicator (default)
       or in readable, categorized, comma-sep str format (readable=True, takes longer)
    
    """

    try:
        check_is_fitted(
            transformer._model, "vocabulary_", "The tfidf vector is not fitted"
        )
        toks = transformer.transform(raw_text)
    except NotFittedError:
        toks = transformer.fit_transform(raw_text)

    vocab = generate_vocabulary_df(transformer, init=vocab_df).reset_index()
    untagged_alias = "_untagged" if group_untagged else vocab["tokens"]
    v_filled = vocab.replace({"NE": {"": np.nan}, "alias": {"": np.nan}}).fillna(
        {
            "NE": "NA",  # TODO make this optional
            # 'alias': vocab['tokens'],
            # "alias": "_untagged",  # currently combines all NA into 1, for weighted sum
            "alias": untagged_alias,
        }
    )
    sparse_dtype = pd.SparseDtype(int, fill_value=0.0)
    table = (  # more pandas-ey pivot, for future cat-types
        v_filled.assign(exists=1)  # placehold
        .groupby(["NE", "alias", "tokens"])["exists"]
        .sum()
        .unstack("tokens")
        .T.fillna(0)
        .astype(sparse_dtype)
    )

    A = toks[:, transformer.ranks_]
    A[A > 0] = 1

    docterm = pd.DataFrame.sparse.from_spmatrix(A, columns=v_filled["tokens"],)

    tag_df = docterm.dot(table)
    tag_df.rename_axis([None, None], axis=1, inplace=True)

    if readable:
        tag_df = _get_readable_tag_df(tag_df)

    return tag_df


def token_to_alias(raw_text, vocab):
    """Replaces known tokens with their "tag" form
    
    Useful if normalized text is needed, i.e. using the token->tag map from some
    known vocabulary list. As implemented, looks for the longest matched substrings
    first, ensuring precedence for compound tags or similar spellings, e.g.
    "thes->these" would get substituted before "the -> [article]"
    
    Needed for higher-order tag creation (see `nestor.keyword.ngram_vocab_builder`).

    Args:
      raw_text (pd.Series): contains text with known jargon, slang, etc
      vocab (pd.DataFrame): contains alias' keyed on known slang, jargon, etc.

    Returns:
       pd.Series: new text, with all slang/jargon replaced with unified tag representations
    
    """
    thes_dict = vocab[vocab.alias.replace("", np.nan).notna()].alias.to_dict()
    substr = sorted(thes_dict, key=len, reverse=True)
    if substr:
        rx = re.compile(r"\b(" + "|".join(map(re.escape, substr)) + r")\b")
        clean_text = raw_text.str.replace(rx, lambda match: thes_dict[match.group(0)])
    else:
        clean_text = raw_text
    return clean_text


def ngram_automatch(voc1, voc2):
    """auto-match tag combinations using `nestorParams.entity_rules_map`
    
    Experimental method to auto-match tag combinations into higher-level
    concepts, primarily to suggest compound entity types to a user.
    
    Used in ``nestor.ui``

    Args:
      voc1 (pd.DataFrame): known 1-gram token->tag mapping, with types
      voc2 (pd.DataFrame): current 2-gram map, with missing types to fill in from 1-grams

    Returns:
      pd.DataFrame: new 2-gram map, with type combinations partially filled (no alias')
    
    """

    NE_map = nestorParams.entity_rules_map

    vocab = voc1.copy()
    vocab.NE.replace("", np.nan, inplace=True)

    # first we need to substitute alias' for their NE identifier
    NE_dict = vocab.NE.fillna("NA").to_dict()

    NE_dict.update(
        vocab.fillna("NA")
        .reset_index()[["NE", "alias"]]
        .drop_duplicates()
        .set_index("alias")
        .NE.to_dict()
    )

    _ = NE_dict.pop("", None)

    # regex-based multi-replace
    NE_sub = sorted(NE_dict, key=len, reverse=True)
    NErx = re.compile(r"\b(" + "|".join(map(re.escape, NE_sub)) + r")\b")
    NE_text = voc2.index.str.replace(NErx, lambda match: NE_dict[match.group(0)])

    # now we have NE-soup/DNA of the original text.
    mask = voc2.alias.replace(
        "", np.nan
    ).isna()  # don't overwrite the NE's the user has input (i.e. alias != NaN)
    voc2.loc[mask, "NE"] = NE_text[mask].tolist()

    # track all combinations of NE types (cartesian prod)

    # apply rule substitutions that are defined
    voc2.loc[mask, "NE"] = voc2.loc[mask, "NE"].apply(
        lambda x: NE_map.get(x, "")
    )  # TODO ne_sub matching issue??  # special logic for custom NE type-combinations (config.yaml)

    return voc2


def pick_tag_types(tag_df, typelist):
    """convenience function to pick out one entity type (top-lvl column)
    
    tag_df (output from `tag_extractor`) contains multi-level columns. These can
    be unwieldy, especially if one needs to focus on a particular tag type,
    slicing by tag name. This function abstracts some of that logic away.
    
    Gracefully finds columns that exist, ignoring ones you want that don't.

    Args:
      tag_df(pd.DataFrame): binary tag occurrence matrix, as output by `tag_extractor`
      typelist(List[str]): names of entity types you want to slice from.

    Returns:
      (pd.DataFrameo): a sliced copy of `tag_df`, given `typelist`
    
    """
    df_types = list(tag_df.columns.levels[0])
    available = set(typelist) & set(df_types)
    return tag_df.loc[:, list(available)]


def ngram_vocab_builder(raw_text, vocab1, init=None):
    """complete pipeline for constructing higher-order tags
    
    A useful technique for analysts is to use their tags like lego-blocks,
    building up compound concepts from atomic tags. Nestor calls these *derived*
    entities, and are determined by `nestorParams.derived`. It is possible to
    construct new derived types on the fly whenever atomic or derived types are
    encountered together that match a "rule" set forth by the user. These are
    found in `nestorParams.entity_rules_map`.
    
    Doing this in pandas and sklearn requires a bit of maneuvering with the
    `TokenExtractor` objects, `token_to_alias`, and `ngram_automatch`.
    The behavior of this function is to either produce a new ngram list from
    scratch using the 1-grams and the original raw-text, or to take existing
    n-gram mappings and add novel derived types to them.
    
    This is a high-level function that may hide a lot of the other function calls.
    IT MAY SLOW DOWN YOUR CODE. The primary use is within interactive UIs that
    require a stream of new suggested derived-type instances, given user
    activity making new atomic instances.

    Args:
      raw_text(pd.Series): original merged text (output from `NLPSelect`)
      vocab1(pd.DataFrame): known 1-gram token->tag mapping (w/ aliases)
      init(pd.DataFrame): 2-gram mapping, known a priori (could be a prev. output of this function., optional):  (Default value = None)

    Returns:
      (tuple): tuple contaning:
         vocab2(pd.DataFrame): new/updated n-gram mapping
         tex(TokenExtractor): now-trained transformer that contains n-gram tf-idf scores, etc.
         replaced_text(pd.Series): raw text whose 1-gram tokens have been replaced with known tags
         replaced_again(pd.Series): replaced_text whose atomic tags have been replaced with known derived types.

    """
    # raw_text, with token-->alias replacement
    replaced_text = token_to_alias(raw_text, vocab1)

    if init is None:
        tex = TokenExtractor(ngram_range=(2, 2))  # new extractor (note 2-gram)
        tex.fit(replaced_text)
        vocab2 = generate_vocabulary_df(tex)
        replaced_again = None
    else:
        mask = (np.isin(init.NE, nestorParams.atomics)) & (init.alias != "")
        # now we need the 2grams that were annotated as 1grams
        replaced_again = token_to_alias(
            replaced_text,
            pd.concat([vocab1, init[mask]])
            .reset_index()
            .drop_duplicates(subset=["tokens"])
            .set_index("tokens"),
        )
        tex = TokenExtractor(ngram_range=(2, 2))
        tex.fit(replaced_again)
        new_vocab = generate_vocabulary_df(tex, init=init)
        vocab2 = (
            pd.concat([init, new_vocab])
            .reset_index()
            .drop_duplicates(subset=["tokens"])
            .set_index("tokens")
            .sort_values("score", ascending=False)
        )
    return vocab2, tex, replaced_text, replaced_again


def ngram_keyword_pipe(raw_text, vocab, vocab2):
    """Experimental pipeline for one-shot n-gram extraction from raw text.

    Args:
      raw_text: 
      vocab: 
      vocab2: 

    Returns:

    """
    import warnings

    warnings.warn(
        "This function is deprecated! Use `ngram_vocab_builder`.",
        DeprecationWarning,
        stacklevel=2,
    )
    print("calculating the extracted tags and statistics...")
    # do 1-grams
    print("\n ONE GRAMS...")
    tex = TokenExtractor()
    tex2 = TokenExtractor(ngram_range=(2, 2))
    tex.fit(raw_text)  # bag of words matrix.
    tag1_df = tag_extractor(tex, raw_text, vocab_df=vocab.loc[vocab.alias.notna()])
    vocab_combo, tex3, r1, r2 = ngram_vocab_builder(raw_text, vocab, init=vocab2)

    tex2.fit(r1)
    tag2_df = tag_extractor(tex2, r1, vocab_df=vocab2.loc[vocab2.alias.notna()])
    tag3_df = tag_extractor(tex3, r2, vocab_df=vocab_combo.loc[vocab2.alias.notna()])

    tags_df = tag1_df.combine_first(tag2_df).combine_first(tag3_df)

    relation_df = pick_tag_types(tags_df, nestorParams.derived)

    tag_df = pick_tag_types(tags_df, nestorParams.atomics + nestorParams.holes + ["NA"])
    return tag_df, relation_df
