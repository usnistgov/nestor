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
#     display_name: Python [conda env:nestor-dev]
#     language: python
#     name: conda-env-nestor-dev-py
# ---

import os
import pandas as pd
from nestor import keyword as kex
from sklearn.model_selection import train_test_split


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
train, test = train_test_split(raw_text, test_size=0.2, random_state=1, shuffle=False)
test = test.reset_index(drop=True)

iob_train = kex.iob_extractor(train, df_1grams, vocab_df_ngrams=df_ngrams)
iob_test = kex.iob_extractor(test, df_1grams, vocab_df_ngrams=df_ngrams)

# pathname/document title should match what is in `congif.cfg file`
create_iob_format_data(iob_train, "iob_data.iob")
convert_iob_to_spacy_file("iob_data.iob")
create_iob_format_data(iob_test, "iob_valid.iob")
convert_iob_to_spacy_file("iob_valid.iob")


# Run data through basic spacy training for proof of concept.
os.system("python -m spacy train spacy_config.cfg --output ./output")
