from mlp import *


class FilteredClassify(object):
    """
    sklearn-style wrapper for supervised classification on only a subset
    of the available data. Useful for only selecting labeled samples for
    training, when the original sample set includes many unlabeled inputs
    (e.g. when vectorizing documents w/ unsupervised techniques).

    """
    def __init__(self, clf, **kwargs):
        # self.options = {}
        # self.options.update(kwargs)
        # self.mask = None
        self.clf = clf(**kwargs)  # an sklearn object with a predict method.


    def fit(self, X, y):

        mask = y != -1
        X_strip = X[mask]
        y_strip = y[mask]

        self.clf.fit(X_strip, y_strip)
        return self

    def score(self, X, y):
        mask = y != -1
        X_strip = X[mask]
        y_strip = y[mask]
        return self.clf.score(X_strip, y_strip)

    def predict(self, X):
        return self.clf.predict(X)
