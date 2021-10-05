__author__ = "Thurston Sexton"

import re
import string
from pathlib import Path
from functools import cached_property
from typing import Union, Optional, Pattern
from enum import Enum
import numpy as np
import pandas as pd
from sklearn.base import TransformerMixin
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.utils.validation import NotFittedError, check_is_fitted
from tqdm import tqdm

from .settings import CFG as nestorParams  # global settings for nestor tags
from .utils import documented_at, _series_itervals


__all__ = ["NLPSelect", "TokenExtractor", "TagExtractor"]


def generate_vocabulary_df(
    transformer, filename=None, init: Optional[Union[str, pd.DataFrame]] = None
):
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
        filename (str, optional): the file location to read/write a csv containing a formatted vocabulary list
        init (str or pd.Dataframe, optional): file location of csv or dataframe of existing vocab list to read and update
            token classification values from

    Returns:
        pd.Dataframe: the correctly formatted vocabulary list for token:NE, alias matching
    """

    try:
        check_is_fitted(
            transformer._model, "vocabulary_", msg="The tfidf vector is not fitted"
        )
    except NotFittedError:
        if (filename is not None) and Path(filename).is_file():
            print("No model fitted, but file already exists. Importing...")
            return pd.read_csv(filename, index_col=0)
        elif isinstance(init, str):
            assert Path(
                init
            ).is_file(), "Assumed path-like was passed, but does not exist!"
            print("No model fitted, but file already exists. Importing...")
            return pd.read_csv(init, index_col=0)
        else:
            raise

    df = (
        pd.DataFrame(
            {
                "tokens": transformer.vocab_,
                "NE": "",
                "alias": "",
                "notes": "",
                "score": transformer.scores_,
            }
        )
        # .loc[:,["tokens", "NE", "alias", "notes", "score"]]
        .pipe(lambda df: df[~df.tokens.duplicated(keep="first")]).set_index("tokens")
    )

    if init is None:
        if (filename is not None) and Path(filename).is_file():
            init = filename
            print("attempting to initialize with pre-existing vocab")

    if init is not None:
        df.NE = np.nan
        df.alias = np.nan
        df.notes = np.nan
        if isinstance(init, pd.DataFrame):
            df_import = init.copy()
        elif isinstance(init, str):
            assert Path(init).is_file(), "`filename` does not exist!"
            df_import = pd.read_csv(init, index_col=0)
        else:
            import warnings

            warnings.warn("File not Found! Can't import!")
            raise IOError
        df.update(df_import)
        df.fillna("", inplace=True)

    if filename is not None:
        df.to_csv(filename)
        print("saved locally!")
    return df


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


def get_tag_completeness(tag_df, verbose=True):
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

    tag_comp = (tag_df.get("NA", all_empt).sum(axis=1) == 0).sum()

    tag_empt = (
        (tag_df.get("I", all_empt).sum(axis=1) == 0)
        & (tag_df.get("P", all_empt).sum(axis=1) == 0)
        & (tag_df.get("S", all_empt).sum(axis=1) == 0)
    ).sum()

    def _report_completeness():
        print(f"Complete Docs: {tag_comp}, or {tag_comp / len(tag_df):.2%}")
        print(f"Tag completeness: {tag_pct.mean():.2f} +/- {tag_pct.std():.2f}")
        print(f"Empty Docs: {tag_empt}, or {tag_empt / len(tag_df):.2%}")

    if verbose:
        _report_completeness()
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
            transformer._model, "vocabulary_", msg="The tfidf vector is not fitted"
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
    if group_untagged:  # makes no sense to keep NE for "_untagged" tags...
        v_filled = v_filled.assign(
            NE=v_filled.NE.mask(v_filled.alias == "_untagged", "NA")
        )
    sparse_dtype = pd.SparseDtype(dtype=int, fill_value=0.0)
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


def regex_match_vocab(vocab_iter, tokenize=False) -> Pattern[str]:
    """regex-based multi-replace

    Fast way to get all matches for a list of vocabulary (e.g. to replace them with preferred labels).

    NOTE: This will avoid nested matches by sorting the vocabulary by length! This means ambiguous substring
    matches will default to the longest match, only.

    > e.g. with vocabulary `['these','there', 'the']` and text `'there-in'`
    > the match will defer to `there` rather than `the`.
    Args:
      vocab_iter (Iterable[str]): container of strings. If a dict is pass, will operate on keys.
      tokenize (bool): whether the vocab should include all valid token strings from tokenizer

    Returns:
      re.Pattern: a compiled regex pattern for finding all vocabulary.
    """
    sort = sorted(vocab_iter, key=len, reverse=True)
    vocab_str = r"\b(?:" + r"|".join(map(re.escape, sort)) + r")\b"

    if (not sort) and tokenize:  # just do tokenizer
        return nestorParams.token_pattern
    elif not sort:
        rx_str = r"(?!x)x"  # match nothing, ever
    elif tokenize:
        # the non-compiled token_pattern version accessed by __getitem__ (not property/attr)
        rx_str = r"({}|{})".format(
            vocab_str, r"(?:" + nestorParams["token_pattern"] + r")",
        )
    else:  # valid vocab -> match them in order of len
        rx_str = r"\b(" + "|".join(map(re.escape, sort)) + r")\b"

    return re.compile(rx_str)


def regex_thesaurus_normalizer(thesaurus: dict, text: pd.Series) -> pd.Series:
    """Quick way to replace text substrings in a Series with a dictionary of replacements (thesaurus)"""
    rx = regex_match_vocab(thesaurus)
    clean_text = text.str.replace(rx, lambda match: thesaurus.get(match.group(0)))
    return clean_text


def iob_extractor(raw_text, vocab_df_1grams, vocab_df_ngrams=None):
    """Use Nestor named entity tags to create IOB format output for NER tasks

    This function provides IOB-formatted tagged text, which allows for further NLP analysis. In the output,
    each token is listed sequentially, as they appear in the raw text. Inside and Beginning Tokens are labeled with
    "I-" or "B-" and their Named Entity tags; any multi-token entities all receive the same label.
    Untagged tokens are labeled as "O" (Outside).

    Example output (in this example, "PI" is "Problem Item":

    token | NE | doc_id
    an | O | 0
    oil | B-PI | 0
    leak | I-PI | 0

    Args:
       raw_text (pd.Series): contains jargon/slang-filled raw text to be tagged
       vocab_df_1grams (pd.DataFrame): An existing vocabulary dataframe or .csv filename, expected in the format of
           kex.generate_vocabulary_df(), containing tagged 1-gram tokens
        vocab_df_ngrams (pd.DataFrame, optional): An existing vocabulary dataframe or .csv filename, expected in
        the format of kex.generate_vocabulary_df(), containing tagged n-gram tokens (Default value = None)

    Returns:
        pd.DataFrame: contains row for each token ("token", "NE" (IOB format tag), and "doc_id")

    Parameters
    ----------
    raw_text
    vocab_df_1grams
    vocab_df_ngrams
    """

    # Create IOB output DataFrame
    # iob = pd.DataFrame(columns=["token", "NE", "doc_id"])

    if vocab_df_ngrams is not None:
        # Concatenate 1gram and ngram dataframes
        vocab_df = pd.concat([vocab_df_1grams, vocab_df_ngrams])
        # Get aliased text using ngrams
        # raw_text = token_to_alias(raw_text, vocab_df_ngrams)
    else:
        # Only use 1gram vocabulary provided
        vocab_df = vocab_df_1grams.copy()
        # Get aliased text
        # raw_text = token_to_alias(raw_text, vocab_df_1grams)
        #
    vocab_thesaurus = vocab_df.alias.dropna().to_dict()
    NE_thesaurus = vocab_df.NE.fillna("U").to_dict()

    rx_vocab = regex_match_vocab(vocab_thesaurus, tokenize=True)
    # rx_NE = regex_match_vocab(NE_thesaurus)
    #
    def beginning_token(df: pd.DataFrame) -> pd.DataFrame:
        """after tokens are split and iob column exists"""
        b_locs = df.groupby("token_id", as_index=False).nth(0).index
        df.loc[df.index[b_locs], "iob"] = "B"
        return df

    def outside_token(df: pd.DataFrame) -> pd.DataFrame:
        """after tokens are split and iob,NE columns exist"""
        is_out = df["NE"].isin(nestorParams.holes)
        return df.assign(iob=df["iob"].mask(is_out, "O"))

    tidy_tokens = (  # unpivot the text into one-known-token-per-row
        raw_text.rename("text")
        .rename_axis("doc_id")
        .str.lower()
        .str.findall(rx_vocab)
        # longer series, one-row-per-token
        .explode()
        # it's a dataframe now, with doc_id column
        .reset_index()
        # map tokens to NE, _fast tho_
        .assign(NE=lambda df: regex_thesaurus_normalizer(NE_thesaurus, df.text))
        # regex replace doesnt like nan, so we find the non-vocab tokens and make them unknown
        .assign(NE=lambda df: df.NE.where(df.NE.isin(NE_thesaurus.values()), "U"))
        # now split on spaces and underscores (nestor's compound tokens)
        .assign(token=lambda df: df.text.str.split(r"[_\s]"))
        .rename_axis("token_id")  # keep track of which nestor token was used
        .explode("token")
        .reset_index()
        .assign(iob="I")
        .pipe(beginning_token)
        .pipe(outside_token)
    )
    iob = (
        tidy_tokens.loc[:, ["token", "NE", "doc_id"]]
        .assign(
            NE=tidy_tokens["NE"].mask(tidy_tokens["iob"] == "O", np.nan)
        )  # remove unused NE's
        .assign(
            NE=lambda df: tidy_tokens["iob"]
            .str.cat(df["NE"], sep="-", na_rep="")
            .str.strip("-")
        )  # concat iob-NE
    )
    return iob


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
    return regex_thesaurus_normalizer(thes_dict, raw_text)


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

    NE_text = regex_thesaurus_normalizer(NE_dict, voc2.index)

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
    tag3_df = tag_extractor(
        tex3,
        r2,
        vocab_df=vocab_combo.loc[vocab_combo.index.isin(vocab2.alias.dropna().index)],
    )

    tags_df = tag1_df.combine_first(tag2_df).combine_first(tag3_df)

    relation_df = pick_tag_types(tags_df, nestorParams.derived)

    tag_df = pick_tag_types(tags_df, nestorParams.atomics + nestorParams.holes + ["NA"])
    return tag_df, relation_df


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
        ngram_range=(1, 1),
        stop_words="english",
        sublinear_tf=True,
        smooth_idf=False,
        max_features=5000,
        token_pattern=nestorParams.token_pattern,
        **tfidf_kwargs,
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
                "token_pattern": token_pattern,
            }
        )

        self.default_kws.update(tfidf_kwargs)
        self._model = TfidfVectorizer(**self.default_kws)
        self._tf_tot = None

        self._ranks = None
        self._vocab = None
        self._scores = None

    def fit(self, documents, y=None):
        """
        Learn a vocabulary dictionary of tokens in raw documents.
        Args:
          documents (pd.Series, Iterable): Iterable of raw documents
          y:  (Default value = None)

        Returns:
          self
        """
        _ = self.fit_transform(documents)
        return self

    def transform(self, documents):
        """transform documents into document-term matrix

        Args:
          documents:

        Returns:
          X_tf: array of shape (n_samples, n_features)
                document-term matrix


        """

        check_is_fitted(self._model, msg="The tfidf vector is not fitted")

        if isinstance(documents, pd.Series):
            X = _series_itervals(documents)
        X_tf = self._model.transform(X)
        self.sumtfidf_ = X_tf.sum(axis=0)
        return X_tf

    def fit_transform(self, documents, y=None, **fit_params):
        """transform a container of text documents to TF-IDF Sparse Matrix

        Args:
          documents (pd.Series, Iterable): Iterable of raw documents
          y:  (Default value = None) unused
          **fit_params: kwargs passed to underlying TfidfVectorizer

        Returns:
          X_tf: array of shape (n_samples, n_features)
                document-term matrix

        """
        if isinstance(documents, pd.Series):
            documents = _series_itervals(documents)
        if y is None:
            X_tf = self._model.fit_transform(documents)
        else:
            X_tf = self._model.fit_transform(documents, y)
        self.sumtfidf_ = X_tf.sum(axis=0)

        ranks = self.sumtfidf_.argsort()[::-1]
        if len(ranks) > self.default_kws["max_features"]:
            ranks = ranks[: self.default_kws["max_features"]]
        self.ranks_ = ranks

        self.vocab_ = np.array(self._model.get_feature_names())[self.ranks_]
        scores = self.sumtfidf_[self.ranks_]
        self.scores_ = (scores - scores.min()) / (scores.max() - scores.min())
        return X_tf

    @property
    def sumtfidf_(self):
        """sum of the tf-idf scores for each token over all documents.

        Thought to approximate mutual information content of a given string.
        """
        return self._tf_tot

    @sumtfidf_.setter
    def sumtfidf_(self, sparse_docterm_sum):
        self._tf_tot = np.array(sparse_docterm_sum)[0]

    @property
    def ranks_(self):
        """Retrieve the rank of each token, for sorting. Uses summed scoring over the
        TF-IDF for each token, so that: $S_t = \Sum_{d\text{TF-IDF}_t$
        """
        return self._ranks

    @ranks_.setter
    def ranks_(self, rank_data: pd.Series):
        self._ranks = rank_data

    @property
    def vocab_(self):
        """
        ordered list of tokens, rank-ordered by summed-tf-idf
        (see :func:`~nestor.keyword.TokenExtractor.ranks_`)
        """
        return self._vocab

    @vocab_.setter
    def vocab_(self, rankedlist):
        self._vocab = rankedlist

    @property
    def scores_(self):
        """
        Returns actual scores of tokens, for progress-tracking (min-max-normalized)

        Returns:
            numpy.array:
        """
        return self._scores

    @scores_.setter
    def scores_(self, scoreframe: pd.Series):
        self._scores = scoreframe

    @documented_at(generate_vocabulary_df, transformer="self")
    def thesaurus_template(self, filename=None, init=None):
        return generate_vocabulary_df(self, filename=filename, init=init)


class TagRep(str, Enum):
    """available representation of tags in documents

    """

    binary = "binary"
    multilabel = "multilabel"
    iob = "iob"


class TagExtractor(TokenExtractor):
    """Wrapper for [TokenExtractor](nestor.keyword.TokenExtractor) to apply a *Nestor* thesaurus or vocabulary
    definition on-top of the token extraction process. Also provides several useful methods as a result.
    """

    def __init__(
        self,
        thesaurus=None,
        group_untagged=True,
        filter_types=None,
        verbose=False,
        output_type: TagRep = TagRep["binary"],
        **tfidf_kwargs,
    ):
        """
        Identical to the [TokenExtractor](nestor.keyword.TokenExtractor) initialization,
        Except for the addition of an optional `vocab` argument that allows for pre-defined
        thesaurus/dictionary mappings of tokens to named entities
        (see [generate_vocabulary_df](nestor.keyword.generate_vocabulary_df))
        to get used in the transformation doc-term form.

        Rather than outputting a TF-IDF-weighted sparse matrix, this transformer outputs a Multi-column
        `pd.DataFrame` with the top-level columns being current tag-types in `nestor.CFG`, and the sub-level
        being the actual tokens/compound-tokens.

        """
        # super().__init__()
        default_kws = dict(
            input="content",
            ngram_range=(1, 1),
            stop_words="english",
            sublinear_tf=True,
            smooth_idf=False,
            max_features=5000,
            token_pattern=nestorParams.token_pattern,
        )
        default_kws.update(**tfidf_kwargs)

        super().__init__(**default_kws)  # get internal attrs from parent
        self._tokenmodel = TokenExtractor(
            **default_kws
        )  # persist an instance for composition

        self.group_untagged = group_untagged
        self.filter_types = filter_types
        self.output_type = output_type
        self._verbose = verbose
        self._thesaurus = thesaurus
        self.tfidf_ = None

        self.tag_df_ = None
        self.iob_rep_ = None
        self.multi_rep_ = None

        self.tag_completeness_ = None
        self.num_complete_docs_ = None
        self.num_empty_docs_ = None

    @cached_property
    def thesaurus(self):
        return self._tokenmodel.thesaurus_template(init=self._thesaurus)

    @property
    def tfidf(self):
        return self.tfidf_

    @tfidf.setter
    def tfidf(self, sparse_docterm):
        self.tfidf_ = sparse_docterm

    @property
    def tag_df(self):
        return self.tag_df_

    @tag_df.setter
    def tag_df(self, binary_df):
        self.tag_df_ = binary_df

    @property
    def tag_completeness(self):
        return self.tag_completeness_

    @property
    def num_complete_docs(self):
        return self.num_complete_docs_

    @property
    def num_empty_docs(self):
        return self.num_empty_docs_

    def set_stats(self):
        check_is_fitted(self)
        (
            self.tag_completeness_,
            self.num_complete_docs_,
            self.num_empty_docs_,
        ) = get_tag_completeness(self.tag_df_, verbose=False)

    def report_completeness(self):
        print(
            f"Complete Docs: {self.num_complete_docs}, or {self.num_complete_docs / len(self.tag_df):.2%}"
        )
        print(
            f"Tag completeness: {self.tag_completeness.mean():.2f} +/- {self.tag_completeness.std():.2f}"
        )
        print(
            f"Empty Docs: {self.num_empty_docs}, or {self.num_empty_docs / len(self.tag_df):.2%}"
        )

    @property
    def tags_as_lists(self):
        return self.multi_rep_

    @tags_as_lists.setter
    def tags_as_lists(self, tag_df):
        self.multi_rep_ = _get_readable_tag_df(tag_df)

    @property
    def tags_as_iob(self):
        return self.iob_rep_

    @tags_as_iob.setter
    def tags_as_iob(self, documents):
        self.iob_rep_ = iob_extractor(documents, self.thesaurus)

    def fit(self, documents, y=None):
        # self._tokenmodel.fit(documents)
        self.tfidf_ = self._tokenmodel.fit_transform(documents)
        # check_is_fitted(self._tokenmodel, msg="The tfidf vector is not fitted")
        tag_df = tag_extractor(
            self._tokenmodel,
            documents,
            vocab_df=self.thesaurus,
            group_untagged=self.group_untagged,
        )
        if self.filter_types:
            tag_df = pick_tag_types(tag_df, self.filter_types)

        self.tag_df = tag_df
        self.tags_as_iob = documents
        self.tags_as_lists = tag_df
        self.set_stats()
        if self._verbose:
            self.report_completeness()
        return self

    def transform(self, documents, y=None):
        """
        """
        check_is_fitted(self, "tag_df_")

        if self.output_type == TagRep.multilabel:
            return self.tags_as_lists
        elif self.output_type == TagRep.iob:
            return self.tags_as_iob
        else:
            return self.tag_df

    @documented_at(tag_extractor, transformer="self")
    def fit_transform(self, documents, y=None):
        """Fit transformer on `documents` and return the binary, hierarchical """
        self.fit(documents)

        return self.transform(documents)

    # __init__.__doc__ += TokenExtractor.__init__.__doc__
