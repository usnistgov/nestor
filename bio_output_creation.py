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
bio = kex.get_iob_output(raw_text, vocab)
bio


