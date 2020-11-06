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
# # Output tags in IOB format for NER analysis
# ### Make function that takes a vocab list and a set of MWOs and returns MWOs in bio format
# #### TODO: Handle SI, PI, longer ngrams
#
# #### https://pythonprogramming.net/using-bio-tags-create-named-entity-lists/

# %%
import pandas as pd
from pathlib import Path
from nestor import keyword as kex
import nestor.datasets as nd

# %%
# Get raw MWOs
df = (nd.load_excavators(cleaned=False)  # already formats dates
      .rename(columns={'BscStartDate': 'StartDate'})
      )

# Change date column to DateTime objects
df.head(5)

# %%
# Get tagged MWOs
tags = pd.read_csv(Path.home()/'Documents'/'datasets'/'1g_original.csv')
tags.head(5)

# %%
# Get vocab file (unigrams)
vocab = kex.generate_vocabulary_df(
      kex.TokenExtractor(),  # doesn't need to be fitted, since vocab exists
      filename=Path.home()/'Documents'/'datasets'/'1g_original.csv'
)
vocab.head(5)

# %%
# merge and cleanse NLP-containing columns of the data
nlp_select = kex.NLPSelect(columns=['OriginalShorttext'])
raw_text = nlp_select.transform(df)  # Series
raw_text

# %%
# TODO: make sure tokens are aliased
# tex = kex.TokenExtractor()
# # toks = tex.fit_transform(raw_text)
# replaced_text = kex.token_to_alias(raw_text, vocab)  # raw_text, with token-->alias replacement
# toks = tex.fit_transform(replaced_text)


# %%
iob = kex.iob_extractor(raw_text, vocab)
iob


