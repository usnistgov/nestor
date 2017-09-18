"""
author: Thurston Sexton
"""

from mlp.tools import *

import numpy as np
import pandas as pd
from tqdm import tqdm
# import sys
import textacy


class KeywordExtractor(object):

    def __init__(self, xlsx_fname,
                 nlp_cols=None,
                 meta_cols=None,
                 keep_temp_files=True,
                 pd_kws=None,
                 special_replace=None,
                 wdir='data'):

        self.data_directory = os.path.join(os.getcwd(), wdir)
        self.vocab = None
        self.raw_excel_filepath = None
        self.df = None
        self.corpus = None

        self.raw_excel_filepath = os.path.join(self.data_directory, xlsx_fname)
        assert os.path.isfile(self.raw_excel_filepath), 'Please provide a valid xlsx_fname path (in \'wdir\')'
        raw_txt_filepath = os.path.join(self.data_directory,
                                        'TEMP_init.txt')
        bigram_logs_filepath = os.path.join(self.data_directory,
                                            'TEMP_bigram.csv')
        raw_csv_filepath = os.path.join(self.data_directory,
                                        'nlp_raw.csv')

        if nlp_cols is None:
            nlp_cols = {'RawText': 0}

        if meta_cols is not None:
            relevant_data = dict(nlp_cols, **meta_cols)
            relevant_names, relevant_cols = tuple(map(list, zip(*relevant_data.items())))
        else:
            relevant_names, relevant_cols = tuple(map(list, zip(*nlp_cols.items())))
            meta_cols = []

        default_pd_kws = {
            'header':1,
            'encoding':'utf-8'
        }  # privide some default assumptions
        if pd_kws is not None:
            default_pd_kws.update(pd_kws)

        self.df = pd.read_excel(self.raw_excel_filepath,
                                names=relevant_names, parse_cols=relevant_cols,
                                **pd_kws)

        for nlp_col in nlp_cols.keys():
            # replace empty NL descriptions with empty string. Replace '\n' inside descriptions with ' '.
            self.df[nlp_col] = self.df[nlp_col].fillna('').apply(lambda x: x.replace('\n', ' '))

        # for now, we're combining all NLP into one "description" --> RawText
        self.df['RawText'] = self.df[list(nlp_cols.keys())].apply(lambda x: '. '.join(x), axis=1)
        self.df['RawText'].to_csv(raw_txt_filepath, sep='\t', index=False)

        # Find and replace bigrams using the Phrase Model from gensim (see tools.py)
        bigram_kws = {'data_directory': self.data_directory,
                      'special': None}
        if special_replace is not None:
            bigram_kws['special'] = special_replace
        bigram_docs(raw_txt_filepath, bigram_logs_filepath, **bigram_kws)
        self.df['RawText'] = pd.read_csv(bigram_logs_filepath, sep='\t')

        # for now, we don't care about the separate NLP cols (future ver.)
        # So, remove all empty NLP work-orders (nothing to extract).
        csv_df = self.df[['RawText']+meta_cols].dropna(subset=['RawText'])
        csv_df.to_csv(raw_csv_filepath, header=False, encoding='utf-8')

        docs = textacy.fileio.read.read_csv(raw_csv_filepath, encoding='utf-8')
        content_stream, metadata_stream = textacy.fileio.split_record_fields(docs, 1)  # Descriptions in RawText col
        self.corpus = textacy.Corpus(u'en', texts=content_stream, metadatas=metadata_stream)

        # FUTURE: Try using python's tempfile module
        if not keep_temp_files:
            os.remove(raw_txt_filepath)
            os.remove(bigram_logs_filepath)

    def fit(self, vocab_filename, notes=True):
        """

        :param vocab_filename: file containing a classified thesaurus for keyword extraction.
        must contain 3 or 4 columns: the token list, the classifications, the preferred labels,
        and any notes (optional).
        :return:
        """
        if notes:
            add_num, add_name= ([4], ['note'])
        else:
            add_num, add_name = ([], [])

        vocab_filepath = os.path.join(self.data_directory, vocab_filename)
        self.vocab = pd.read_csv(vocab_filepath, header=0, encoding='utf-8',
                                 names=['token', 'NE', 'alias']+add_name, index_col=0, na_values=['nan'],
                                 usecols=[1, 2, 3]+add_num)
        self.vocab = self.vocab.dropna(subset=['NE'])  # remove named entities that are NaN
        self.vocab.alias = self.vocab.apply(lambda x: np.where(pd.isnull(x.alias), x.name, x.alias),
                                            axis=1)  # alias to original if blank
        self.vocab = self.vocab[~self.vocab.index.duplicated(keep='first')]

    def transform(self, corpus=None, vocab=None, save=True):

        if corpus is None:
            corpus = self.corpus
        if vocab is None:
            vocab = self.vocab

        def get_norm_tokens(doc_n, doc_term_mat, id2term):
            doc = doc_term_mat[doc_n].toarray()
            return [id2term[i] for i in doc.nonzero()[1]]

        def doc_to_tags(tokens, thes):
            #     tokens = get_norm_terms(doc)
            tags = {'I': [], 'P': [], 'S': []}
            untagged = []
            vocab_list = thes.index.tolist()
            for tok in tokens:
                if tok in vocab_list:  # recognized token?
                    typ = thes.loc[tok]['NE']

                    if typ in tags.keys():  # I, P, or S?
                        tags[typ] = list(set(tags[typ] + [thes.loc[tok]['alias'].tolist()]))
                    else:  # R or X?
                        pass  # skip'em
                elif np.any([i in vocab_list for i in tok.split(' ')]):
                    # If any subset of `tok` is itself a recognized token, skip'em
                    pass
                else:  # not recognized :(
                    untagged += [tok]
            return tags, list(set(untagged))

        def tag_corpus(corpus, thes):
            RT, I, S, P, UK = ([], [], [], [], [])

            # make the tf-idf embedding to tokenize with lemma/ngrams
            doc_term_matrix, id2term = textacy.vsm.doc_term_matrix(
                (doc.to_terms_list(ngrams=(1, 2, 3),
                                   normalize=u'lemma',
                                   named_entities=False,
                                   #                                filter_stops=True,  # Nope! Not needed :)
                                   filter_punct=True,
                                   as_strings=True)
                 for doc in corpus),
                weighting='tfidf',
                normalize=False,
                smooth_idf=False,
                min_df=2, max_df=0.95)  # each token in >2 docs, <95% of docs

            # iterate over all issues
            for doc_n, doc in enumerate(tqdm(corpus)):
                tokens = get_norm_tokens(doc_n, doc_term_matrix, id2term)
                tags, unknown = doc_to_tags(tokens, thes)
                UK += [', '.join(unknown)]
                RT += [doc.text]
                I += [', '.join(tags['I'])]
                S += [', '.join(tags['S'])]
                P += [', '.join(tags['P'])]
            # get back a tagged DF
            return pd.DataFrame(data={
                'RawText': RT,
                'Items': I,
                'Problem': P,
                'Solution': S,
                'UK_tok': UK  # unknown
            }, columns=['RawText', 'Items', 'Problem', 'Solution', 'UK_tok'])

        df_pred = tag_corpus(corpus, vocab)
        if save:
            df_pred.to_excel('keyword_tagged.xlsx')
        return df_pred



