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
# replaced_text = kex.token_to_alias(raw_text, vocab)  # raw_text, with token-->alias replacement
# toks = tex.fit_transform(replaced_text)

# Create BIO output
bio = list()

# %%
for i in raw_text.index:
    # Get each MWO as list of tokens
    mwo = raw_text.iat[i].replace('\\', ' ')
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
                if ne_tag == 'B_':  # FIXME: check for bigrams
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

# %%
# TODO: format output file
bio

# %%
# # %%
# df_tags.loc[i_null_mask, 'I'].dropna().str.strip('[]').str.split(', ')
#
# tagged_words = list()
# space = re.compile('(\w)( )(\w)')
# underscore = re.compile('g<1>_g<3>')
#
# subset = df_tags[['I', 'P', 'S', 'P I', 'S I']].values  # Need to not get repeat tokens in same row
# subset = subset.tolist()
#
# corpus = list()
# for mwo in subset:
#     row_list = list()
#     mwo = [x for x in mwo if str(x) != 'nan']
#     for item in mwo:
#         item = re.sub(r'(\w)( )(\w)', r'\g<1>_\g<3>', item)
#         row_list.append(item)
#
#     # Turn row_list into string:
#     row = ' '.join(row_list)
#     corpus.append(row)
#
#
# %%
# from: https://github.com/NervanaSystems/nlp-architect/blob/e6b6ba0164c23ddb4dc9c2aff700e0e9e4521ade/nlp_architect/utils/text.py

# def bio_to_spans(text: List[str], tags: List[str]) -> List[Tuple[int, int, str]]:
#     """
#     Convert BIO tagged list of strings into span starts and ends
#     Args:
#         text: list of words
#         tags: list of tags
#     Returns:
#         tuple: list of start, end and tag of detected spans
#     """
#     pointer = 0
#     starts = []
#     for (
#         i,
#         t,
#     ) in enumerate(tags):
#         if t.startswith("B-"):
#             starts.append((i, pointer))
#         pointer += len(text[i]) + 1
#
#     spans = []
#     for s_i, s_char in starts:
#         label_str = tags[s_i][2:]
#         e = 0
#         e_char = len(text[s_i + e])
#         while len(tags) > s_i + e + 1 and tags[s_i + e + 1].startswith("I-"):
#             e += 1
#             e_char += 1 + len(text[s_i + e])
#         spans.append((s_char, s_char + e_char, label_str))
#     return spans
#

# %%
