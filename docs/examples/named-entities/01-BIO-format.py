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
#

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
vocab=nd.load_vocab('excavators')#.dropna(subset=['alias'])
vocab

# %%
# %timeit iob = kex.iob_extractor(df.OriginalShorttext, vocab)
iob
