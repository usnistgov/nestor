# ---
# jupyter:
#   jupytext:
#     formats: py:light,ipynb
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.2
#   kernelspec:
#     display_name: nestor
#     language: python
#     name: nist-nestor-tUZR9SdD-py3.8
# ---

import os
import pandas as pd
from nestor import datasets as ds
from nestor import keyword as kex
import nltk

import spacy
import en_core_web_sm

# Get dataset and Nestor vocab files  #todo : update import statements to use DVC
df = pd.read_csv(
    "/Users/amc8/nestor/SMALL_data_combined_and_tagged.csv"
)

df_1grams = pd.read_csv(
    "/Users/amc8/nestor/vocab1g.csv",
    index_col=0
)

df_ngrams = pd.read_csv(
    "/Users/amc8/nestor/vocabNg.csv",
    index_col=0
)

nlp_select = kex.NLPSelect(columns = ['Description.1', 'Long Text'])
raw_text = nlp_select.transform(df.head(30))   #fixme (using abridged dataset here for efficiency)

iob = kex.iob_extractor(raw_text, df_1grams, vocab_df_ngrams=df_ngrams) #, vocab_df_ngrams=df_ngrams  #fixme (handle multi tokens)

# iob.to_csv('out.csv')
# iob = pd.read_csv(
#     "/Users/amc8/nestor/out.csv",
#     index_col=0
# )

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
    iob[["token", "NE"]].to_csv(ner_file_path, sep="\t", index=False, header=False)


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
    os.system("python -m spacy convert -c ner -s -n 10 -b en_core_web_sm iob_data.iob .")


# pathname/document title should match what is in `congif.cfg file`
create_iob_format_data(iob, "iob_data.iob")
convert_iob_to_spacy_file("iob_data.iob")


# Run data through basic spacy training for proof of concept.
"""
THIS REQUIRES .spacy FILE NAMES TO MATCH THE FILE NAMES LISTED IN [paths] IN spacy_config.cfg
FOR NOW, I MANUALLY COPIED `iob_data.spacy` TO CREATE `iob_valid.spacy'.
STILL NEED TO SPLIT INTO ACTUAL TRAINING/VALIDATION DATA, SO MODEL RESULTS ARE GARBAGE, BUT IT RUNS ;)
"""
os.system("python -m spacy train spacy_config.cfg --output ./output")