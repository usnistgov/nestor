# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.6.0
#   kernelspec:
#     display_name: Python [conda env:bio_output]
#     language: python
#     name: conda-env-bio_output-py
# ---

# %% [markdown]
# # Output tags in BIO format for NER analysis
# ### Make function that takes a vocab list and a set of MWOs and returns MWOs in bio format
# #### TODO: BIO or IOB?
# #### TODO: Handle SI, PI, longer ngrams
#
# #### https://pythonprogramming.net/using-bio-tags-create-named-entity-lists/

# %%
import pandas as pd
import json
from nestor import keyword as kex

def get_iob_output(text, vocab):
    """

    Parameters
    ----------
    text : pandas.DataFrame
    vocab : pandas.DataFrame

    Returns
    -------
    str

    """
    # Create BIO output
    bio = list()

    for i in text.index:
        # Get each MWO as list of tokens
        mwo = text.iat[i].replace('\\', ' ')
        mwo = mwo.split()
        # default BIO tag is O
        ne_tag = 'O'
        labels = list()
        # Go through token list for MWO
        # TODO: Refactor this ***
        for token in mwo:
            found = vocab.loc[vocab['tokens'].str.fullmatch(token)]
            if len(found) > 0:
                ne = found.iloc[0].loc['NE']
                if (ne == 'S') or (ne == 'I') or (ne == 'P'):
                    if ne_tag == 'B_':  # FIXME: check for bigrams (once aliasing works for multi-token ngrams)
                        ne_tag = 'I_'
                    else:
                        ne_tag = 'B_'
                else:
                    ne_tag = 'O'
                    ne = ''
            else:
                ne_tag = 'O'

            text_tag = (token, str(ne_tag) + str(ne))
            # print(text_tag)
            labels.append(text_tag)
        # Add MWO's tagged token list to BIO output
        bio.append(labels)

    # TODO: format output file (JSON?)
    return bio


# %%
# Get raw MWOs
df = (pd.read_csv('/Users/amc8/Documents/datasets/MWOs.csv')
      .rename(columns={'BscStartDate': 'StartDate'})
      )

# Change date column to DateTime objects
df.StartDate = pd.to_datetime(df['StartDate'])
df.head(5)

# %%
# Get tagged MWOs
tags = pd.read_csv('/Users/amc8/Documents/datasets/READABLE_TAGS.csv')
tags.head(5)

# %%
# Get vocab file (unigrams)
vocab = pd.read_csv('/Users/amc8/Documents/datasets/1g_original.csv')
vocab.head(5)

# %%
# merge and cleanse NLP-containing columns of the data
nlp_select = kex.NLPSelect(columns=['OriginalShorttext'])
raw_text = nlp_select.transform(df)  # Series
raw_text

# %%
# TODO: make sure tokens are aliased
tex = kex.TokenExtractor()
# toks = tex.fit_transform(raw_text)
replaced_text = kex.token_to_alias(raw_text, vocab)  # raw_text, with token-->alias replacement
toks = tex.fit_transform(replaced_text)


# %%
bio = get_iob_output(raw_text, vocab)
bio


