from mlp import *


class FilteredClassify(object):
    """
    sklearn-style wrapper for supervised classification on only a subset
    of the available data. Useful for only selecting labeled samples for
    training, when the original sample set includes many unlabeled inputs
    (e.g. when vectorizing documents w/ unsupervised techniques).

    """
    def __init__(self, clf, mask=None, **kwargs):
        self.options = {
            'verbose': True
        }
        self.options.update(kwargs)
        if mask is not None:
            self.mask = mask
            if self.options['verbose']:
                print "retriving {} selected samples from input".format(len(self.mask))



    def fit(self, X, y):
        assert type(X) == textacy.corpus.Corpus  # Must be valid textacy corpus
        self.corpus = X
        return self

    def transform(self, X):
        return self.corpus.vectors