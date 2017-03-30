from mlp import *
from sklearn.base import BaseEstimator, TransformerMixin

class SemanticVectors(BaseEstimator, TransformerMixin):
    """
    sklearn-style class for retrieving word2vec vector embedding of a document
    corpus via textacy. Used in a Pipeline.
    """
    def __init__(self):
        # Must be valid textacy corpus
        self.corpus = None
        # reads in a Textacy corpus

    def fit(self, X, y):
        assert type(X) == textacy.corpus.Corpus  # Must be valid textacy corpus
        self.corpus = X
        return self

    def transform(self, X):
        return self.corpus.vectors


class WordBagVectors(BaseEstimator, TransformerMixin):
    """
    Returns term-frequency or tf-idf embedding of document corpus via textacy in
    an sklearn-compatible format for use in Pipelines.

    Uses 2nd-order (3-term) phrase model, lemmatization, stop-word filtering, and
    punctuation filtering by default.

    If using LDA, it is recommended to use tf weighting, and no/false normalization or
    smooth_idf in the initialization keywords.
    """
    def __init__(self, **kwargs):
        self.corpus = None
        self.id2term = None
        self.doc_term_matrix = None
        self.options = {
            'weighting': 'tfidf',  # change to tf if using LDA
            'normalize': True,  # turn off if using LDA
            'smooth_idf': True,  # turn off if using LDA
            'min_df': 2,  # each token in > 2 docs
            'max_df': 0.95  # each token in < 95% of docs
        }
        self.options.update(kwargs)

    def fit(self, X, y):
        assert type(X) == textacy.corpus.Corpus  # Must be valid textacy corpus
        self.corpus = X

        return self

    def transform(self, X):
        self.doc_term_matrix, self.id2term = textacy.vsm.doc_term_matrix(
            (doc.to_terms_list(ngrams=(1, 2, 3),
                               normalize=u'lemma',
                               named_entities=True,
                               filter_stops=True,
                               filter_punct=True,
                               as_strings=True)
             for doc in self.corpus), **self.options)
        return self.doc_term_matrix


class TopicVectors(BaseEstimator, TransformerMixin):
    """
    sklearn-style class for retrieving word2vec vector embedding of a document
    corpus via textacy. Used in a Pipeline.

    it is possible to change the default Bag of Words parameters by passing
    the needed keyworded values to bow_kws.

    If using LDA, it is recommended to use tf weighting, and no/false normalization or
    smooth_idf in the bow_kws keywords.
    """
    def __init__(self, model='lsa', bow_kws={}, options={'n_topics': 30}, **kwargs):
        assert model in ['lda', 'nmf', 'lsa']  # only 3 available topic models
        self.topic_type = model
        self.corpus = None
        self.bow_model = None
        self.topic_model = None
        self.options = options
        self.options.update(kwargs)
        self.bow_options = bow_kws
        self.doc_term_matrix = None
        self.doc_topic_matrix = None

    def fit(self, X, y):
        print type(X)
        assert type(X) == textacy.corpus.Corpus  # Must be valid textacy corpus
        self.corpus = X
        self.bow_model = WordBagVectors()
        self.bow_model.fit(X)
        self.bow_model.options.update(self.bow_options)
        self.doc_term_matrix = self.bow_model.transform(X)

        self.topic_model = textacy.tm.TopicModel(self.topic_type, **self.options)
        self.topic_model.fit(self.doc_term_matrix)
        return self

    def transform(self, X):
        self.doc_topic_matrix = self.topic_model.transform(self.doc_term_matrix)
        return self.doc_topic_matrix

