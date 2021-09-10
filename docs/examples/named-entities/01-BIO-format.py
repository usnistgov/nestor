# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.11.3
#   kernelspec:
#     display_name: Python [conda env:nestor-docs]
#     language: python
#     name: conda-env-nestor-docs-py
# ---

# %% [markdown]
# # Output tags in IOB format for NER analysis
# ### Make function that takes a vocab list and a set of MWOs and returns MWOs in bio format
# #### TODO: Handle SI, PI
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
#       .rename(columns={'BscStartDate': 'StartDate'})
      )

# Change date column to DateTime objects
df.head(5)

# %%
vocab=nd.load_vocab('excavators')
vocab.dropna(subset=['alias'])

# %%
iob = kex.iob_extractor(df.OriginalShorttext, vocab)
iob

# %%
# Get vocab file (bigrams)
vocab_2 = kex.generate_vocabulary_df(
      kex.TokenExtractor(),  # doesn't need to be fitted, since vocab exists
      filename=Path.home()/'Documents'/'datasets'/'2g_original.csv'
)
vocab_2.head(5)

# %%
# merge and cleanse NLP-containing columns of the data
nlp_select = kex.NLPSelect(columns=['OriginalShorttext'])
raw_text = nlp_select.transform(df)  # Series
raw_text = raw_text.head(700)


# %%
# Use iob_extractor with both 1gram and ngram vocab outputs from Nestor
iob = kex.iob_extractor(raw_text, vocab_1, vocab_df_ngrams=vocab_2)
iob
# %%

# %%

# %%
