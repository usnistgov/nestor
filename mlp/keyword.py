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
    """A class for the automatic extraction of keywords (tags) from natural-language text

    Docs WIP, see IEEE Big Data paper submission

    Attributes
    ----------
    data_directory : :obj: `os.path`
        current folder for data- and temp-files
    vocab : :obj: `pandas.DataFrame`
        df of classified keywords, usually from a human annotator. See method: <self>.gen_vocab()
    df : :obj: `pandas.DataFrame`
        the original data (NL + meta-data), stored as a dataframe for ease-of-use.
    corpus : :obj: `textacy.Corpus`
        a corpus object containing parsed NL and metadata. Built on spacy.io

    """
    def __init__(self, xlsx_fname,
                 nlp_cols=None,
                 meta_cols=None,
                 keep_temp_files=True,
                 pd_kws=None,
                 special_replace=None,
                 wdir='data'):
        """

        Parameters
        ----------
        xlsx_fname : :obj: `str`
            The initial database, currently in the form of an .xlsx document in 'wdir'
        nlp_cols : :obj: `dict`
            Which columns (int) contain Natural Language text for keyword-extraction
        meta_cols : :obj: `list` of :obj: `int`, optional
            Which columns (int) should be kept track of for future data analysis
        keep_temp_files : bool
            whether to keep the temporary .txt and .csv files the fit creates (debug)
        pd_kws : :obj: `dict`, optional
            any options to pass to the Pandas read_csv file, useful for formatting errors
        special_replace : :obj: `dict`, optional
            provide problem substrings as keys and desired replacements as values.
        wdir : :obj: `str`, optional
            which sub-folder to store data- and temp-files in

        """
        self.data_directory = os.path.join(os.getcwd(), wdir)

        self.vocab = None
        self.vocab_filepath = None
        self.raw_excel_filepath = None
        self.df = None
        self._df_pred = None
        self.corpus = None
        self.doc_term_matrix = None
        self.id2term = None

        self.raw_excel_filepath = os.path.join(self.data_directory, xlsx_fname)
        assert os.path.isfile(self.raw_excel_filepath), 'Please provide a valid xlsx_fname path (in \'wdir\')'
        raw_txt_filepath = os.path.join(self.data_directory,
                                        'TEMP_init.txt')
        bigram_logs_filepath = os.path.join(self.data_directory,
                                            'TEMP_bigram.csv')
        raw_csv_filepath = os.path.join(self.data_directory,
                                        'TEMP_nlp_raw.csv')

        if nlp_cols is None:
            nlp_cols = {'RawText': 0}

        if meta_cols is not None:
            relevant_data = dict(nlp_cols, **meta_cols)
            relevant_names, relevant_cols = tuple(map(list, zip(*relevant_data.items())))
        else:
            relevant_names, relevant_cols = tuple(map(list, zip(*nlp_cols.items())))
            meta_cols = {}

        default_pd_kws = {
            'header':0,
            'encoding':'utf-8'
        }  # privide some default assumptions
        if pd_kws is not None:
            default_pd_kws.update(pd_kws)

        self.df = pd.read_excel(self.raw_excel_filepath,
                                names=[relevant_names[i] for i in np.argsort(relevant_cols)],
                                parse_cols=relevant_cols,
                                **default_pd_kws)

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
        self.df['RawText'] = pd.read_csv(bigram_logs_filepath, sep='\t', header=None)

        # for now, we don't care about the separate NLP cols (future ver.)
        # So, remove all empty NLP work-orders (nothing to extract).
        csv_df = self.df[['RawText']+list(meta_cols.keys())].dropna(subset=['RawText'])
        csv_df.to_csv(raw_csv_filepath, header=False, encoding='utf-8')

        docs = textacy.fileio.read.read_csv(raw_csv_filepath, encoding='utf-8')
        content_stream, metadata_stream = textacy.fileio.split_record_fields(docs, 1)  # Descriptions in RawText col
        self.corpus = textacy.Corpus(u'en', texts=content_stream, metadatas=metadata_stream)

        # FUTURE: Try using python's tempfile module
        if not keep_temp_files:
            import glob
            for filename in glob.glob(os.path.join(self.data_directory,"TEMP_*")):
                os.remove(filename)

            # os.remove(raw_txt_filepath)
            # os.remove(bigram_logs_filepath)

    def fit(self, vocab=None, notes=True):
        """Prepares the classified vocabulary list for keyword extraction

        Parameters
        ----------
        vocab : :obj: `pandas.Dataframe` or :obj: `str`
            file or pandas.Dataframe containing a classified thesaurus for
            keyword extraction. Must contain 3 or 4 columns: the token list,
            the classifications, the preferred labels, and any notes (optional).

            If a DataFrame is supplied, column names MUST be
                ['token', 'NE', 'alias'] (+'note', optional)
            else an assertion error is thrown.
        notes : bool
            whether the vocab file/object contains a 4th column with user-commentary

        Returns
        -------
        :obj: `pandas.Dataframe`
            a df containing the original NL text and the tags for each category available (I,S,P + UK)
        """
        if notes:
            add_num, add_name= ([3], ['note'])
        else:
            add_num, add_name = ([], [])

        if isinstance(vocab, pd.DataFrame):
            assert (list(vocab) == ['token', 'NE', 'alias']+add_name), 'column names must be compatible'
            self.vocab = vocab
        else:
            # if self.vocab_filepath is None:
            self.vocab_filepath = os.path.join(self.data_directory, vocab)

            assert os.path.isfile(self.vocab_filepath), "please provide a valid file!"
            self.vocab = pd.read_csv(self.vocab_filepath, header=0, encoding='utf-8',
                                     names=['token', 'NE', 'alias']+add_name, index_col=0, na_values=['nan'],
                                     usecols=[0, 1, 2]+add_num)

        self.vocab = self.vocab.dropna(subset=['NE'])  # remove named entities that are NaN
        self.vocab.alias = self.vocab.apply(lambda x: np.where(pd.isnull(x.alias), x.name, x.alias),
                                            axis=1)  # alias to original if blank
        self.vocab = self.vocab[~self.vocab.index.duplicated(keep='first')]
        if (self.doc_term_matrix is None) or (self.id2term is None):
            self._bow()
        # return self.vocab

    def transform(self, corpus=None, vocab=None, save=True):
        """Applies the known keywords to the parsed NL text, returning tagged data

        Parameters
        ----------
        corpus : :obj: `textacy.Corpus`, optional
            a corpus object containing parsed NL and metadata
            Defaults to <self>.corpus, created upon instantiation.
        vocab : obj: `pandas.DataFrame`, optional
            a DataFrame containing classified keyword lookup. Defaults to
            <self>.vocab, created via <self>.fit()
        save : bool
            whether to store the extracted tags as a class attribute <self>._df_pred (debug)

        Returns
        -------
        :obj: `pandas.Dataframe`
            a df containing the original NL text and the tags for each category available (I,S,P + UK)
        """
        if corpus is None:
            corpus = self.corpus
        if vocab is None:
            vocab = self.vocab

        # make the tf-idf embedding to tokenize with lemma/ngrams
        if (self.doc_term_matrix is None) or (self.id2term is None):
            self._bow()

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

        def tag_corpus(corpus, thes, doc_term_matrix, id2term):
            RT, I, S, P, UK = ([], [], [], [], [])
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

        df_pred = tag_corpus(corpus, vocab, self.doc_term_matrix, self.id2term)

        if save:
            self._df_pred = df_pred
            # self._df_pred.to_excel('keyword_tagged.xlsx')
            # self._df_pred = df_pred
        return df_pred

    def _bow(self):
        self.doc_term_matrix, self.id2term = textacy.vsm.doc_term_matrix(
            (doc.to_terms_list(ngrams=(1, 2, 3),
                               normalize=u'lemma',
                               named_entities=False,
                               # filter_stops=True,  # Nope! Not needed :)
                               filter_punct=True,
                               as_strings=True)
             for doc in self.corpus),
            weighting='tfidf',
            normalize=False,
            smooth_idf=False,
            min_df=2, max_df=0.95)  # each token in >2 docs, <95% of docs

    def gen_vocab(self, vocab_fname, topn=3000, notes=False):
        """ A helper method to start the keyword annotation process

        It's helpful to start out with this correctly-formatted .csv sheet.
        Also calculates the document-term-matrix, to speed up <self>.transform()
        Legacy handling of ASCII to Unicode is still intact, but scheduled for deprecation.
        Parameters
        ----------
        vocab_fname : :obj: `str`
            file name, used to create a .xlsx file for keyword annotation
        topn : int
            how many of the top (tf-idf ranked) vocabulary to write out to the .xlsx

        Returns
        -------
        None

        """
        from unicodedata import normalize

        if (self.doc_term_matrix is None) or (self.id2term is None):
            self._bow()
        # topn = 3000

        topn_tok = [self.id2term[i] for i in self.doc_term_matrix.sum(axis=0).argsort()[0, -topn:].tolist()[0][::-1]]
        top_n_filepath = os.path.join(self.data_directory, 'TEMP_top{}vocab.txt'.format(topn))
        with open(top_n_filepath, 'w+') as f:
            for i in topn_tok:
                try:
                    f.write(i + '\n')
                except UnicodeEncodeError:
                    print
                    i, '-->', normalize('NFKD', i).encode('ascii', 'ignore')
                    f.write(normalize('NFKD', i).encode('ascii', 'ignore') + '\n')

        tmp_vocab = pd.read_csv(top_n_filepath, header=None, names=['token'])
        tmp_vocab = tmp_vocab.assign(NE="", alias="")
        if notes:
            tmp_vocab = tmp_vocab.assign(notes="")

        self.vocab_filepath = os.path.join(self.data_directory, vocab_fname)
        tmp_vocab.to_csv(self.vocab_filepath, index=False)


