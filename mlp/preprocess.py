"""
author: Thurston Sexton     DEPRECATED SkLearn Pipeline experiment
"""
from mlp import *
import os
from sklearn.preprocessing import LabelEncoder
import codecs

# TODO: make preprocessing Class with df, csv, corpus attributes.

data_directory = os.path.join('..', 'data')
raw_excel_filepath = os.path.join(data_directory,
                                  'Maintenance_All_Clean.xlsx')
assert os.path.isfile(raw_excel_filepath)
sheet = "Sheet1"
df = pd.read_excel(raw_excel_filepath, sheetname=sheet, encoding='utf-8')

# deal with sparse labeling (Effect Column)

df[["Effect", "Machine Area"]] = df[["Effect", "Machine Area"]].fillna(value="NaN")
# print df["Machine Area"].value_counts()

df['labels'] = df["Machine Area"]
min_count = 3 # Filter labels occurring less than this

value_counts = df["labels"].value_counts()  # Specific column
to_remove = value_counts[value_counts < min_count].index
df['labels'].replace(to_remove, 'MISC', inplace=True)
df["labels"] = df["labels"].astype('category')
# df["labels"][df["labels"]!=-1] = df["labels"][df["labels"]!=-1].cat.codes


area_labeler = LabelEncoder()
df["labels"] = area_labeler.fit_transform(df["labels"])

missing_label = df['labels'].value_counts().argmax()  # assumes most common label is the missing label.
m_eq = df["labels"] == missing_label
df.loc[m_eq, "labels"] = -1  # to make a "non-category"

# shift higher cats down.
m_gt = df["labels"] > missing_label
df.loc[m_gt, "labels"] -= 1


def old_encode(x):
    return np.where(x > missing_label, x+1, x)  # so that we can undo this ungodly frankensteining later

raw_csv_filepath = os.path.join(data_directory,
                                   'raw_csv_logs.csv')
# if not os.path.isfile(raw_csv_filepath):


corpus_filepath = os.path.join(data_directory,
                               'SpacyCorpus')

def get_corpus():
    # if not os.path.isdir(corpus_filepath):
    #     os.makedirs(corpus_filepath)
    #     df.to_csv(raw_csv_filepath, encoding='utf-8', header=False)
    #     docs = textacy.fileio.read.read_csv(raw_csv_filepath, encoding='utf-8')
    #     content_stream, metadata_stream = textacy.fileio.split_record_fields(docs, 6)  # Descriptions in Col 6
    #     corpus = textacy.Corpus(u'en', texts=content_stream, metadatas=metadata_stream)
    #     corpus.save(corpus_filepath, name='maint_logs', compression='gzip')
    # else:
    #     corpus = textacy.Corpus.load(corpus_filepath, name='maint_logs', compression='gzip')

    df.to_csv(raw_csv_filepath, encoding='utf-8', header=False)
    docs = textacy.fileio.read.read_csv(raw_csv_filepath, encoding='utf-8')
    content_stream, metadata_stream = textacy.fileio.split_record_fields(docs, 6)  # Descriptions in Col 6
    corpus = textacy.Corpus(u'en', texts=content_stream, metadatas=metadata_stream)
    print(corpus)
    return corpus


def get_df():
    return df


def get_og_labeling(x):
    return area_labeler.inverse_transform(old_encode(x))

def get_labeled_data(x):
    labeled_index = df["labels"] != -1
    return x[labeled_index.values]
