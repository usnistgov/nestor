# ---
# jupyter:
#   jupytext:
#     formats: py:light,ipynb
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.3
#   kernelspec:
#     display_name: nist-nestor-tUZR9SdD-py3.8
#     language: python
#     name: nist-nestor-tuzr9sdd-py3.8
# ---

# # NER Example: Using IOB output SpaCy

import os
import pandas as pd
from nestor import keyword as kex
from sklearn.model_selection import train_test_split


# ## Helper functions

def create_iob_format_data(df_iob: pd.DataFrame, ner_file_path: str):
    """
    Create .iob file with token-per-line IOB format
    (see https://github.com/explosion/spaCy/blob/master/extra/example_data/ner_example_data/ner-token-per-line.iob
        for example format)

    Parameters
    ----------
    df_iob: DataFrame created by kex.iob_extractor()
    ner_file_path: pathname for where to save the file in IOB-formatted output, use ".iob" extension

    Returns
    -------

    """
    # to do: make sure that
    # Convert IOB DataFrame to token-per-line tsv file
    df_iob[["token", "NE"]].to_csv(ner_file_path, sep="\t", index=False, header=False)


def convert_iob_to_spacy_file(ner_file_path: str):
    """

    Parameters
    ----------
    ner_file_path: pathname for where to save the file in IOB-formatted output, use ".iob" extension, must be in format
        as shown here: https://github.com/explosion/spaCy/blob/master/extra/example_data/ner_example_data/ner-token-per-line.iob

    Returns
    -------

    """
    # todo: make this command customizable, handle tokens better (actually need to group by MWO)
    os.system("python -m spacy convert -c ner -s -n 10 -b en_core_web_sm " + ner_file_path + " .")


# ## Load data

# Here, we are loading the excavator dataset and associated vocabulary from the Nestor package. 
#
# To use this workflow with your own dataset and Nestor tagging, set up the following dataframes:
#     
# ```
# df = pd.read_csv(
#     "original_data.csv"
# )
#
# df_1grams = pd.read_csv(
#     "vocab1g.csv",
#     index_col=0
# )
#
# df_ngrams = pd.read_csv(
#     "vocabNg.csv",
#     index_col=0
# )
# ```

df = dat.load_excavators()
# This vocab data inclues 1grams and Ngrams
df_vocab = dat.load_vocab("excavators")

# ## Prepare data for modeling

# Select column(s) that inlcude text.

# Split data into training and test sets.

nlp_select = kex.NLPSelect(columns = ['OriginalShorttext'])
raw_text = nlp_select.transform(df)   
train, test = train_test_split(raw_text, test_size=0.2, random_state=1, shuffle=False)
test = test.reset_index(drop=True)

# Pass text data and vocab files from Nestor through `iob_extractor`

iob_train = kex.iob_extractor(train, df_1grams, vocab_df_ngrams=df_ngrams)
iob_test = kex.iob_extractor(test, df_1grams, vocab_df_ngrams=df_ngrams)

# Create `.iob` files (these are essentially tsv files with proper IOB tag format). Convert `.iob` files to `.spacy` binary files

# pathname/document title should match what is in `congif.cfg file`
create_iob_format_data(iob_train, "iob_data.iob")
convert_iob_to_spacy_file("iob_data.iob")
create_iob_format_data(iob_test, "iob_valid.iob")
convert_iob_to_spacy_file("iob_valid.iob")


# ## SpaCy model

# Run data through basic spaCy training (relies on `spacy_config.cfg`). This stage can be customized as needed for your particular modeling and analysis.

# Run data through basic spacy training for proof of concept.
os.system("python -m spacy train spacy_config.cfg --output ./output")
