"""
author: Thurston Sexton     DEPRECATED SkLearn Pipeline experiment
"""
from mlp import *
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.utils.validation import check_X_y, check_array, check_is_fitted
from sklearn.utils.multiclass import unique_labels
from sklearn.linear_model import SGDClassifier
from sklearn.svm import LinearSVC


class FilteredClassify(BaseEstimator, ClassifierMixin):
    """
    sklearn-style wrapper for supervised classification on only a subset
    of the available data. Useful for only selecting labeled samples for
    training, when the original sample set includes many unlabeled inputs
    (e.g. when vectorizing documents w/ unsupervised techniques).

    """
    def __init__(self, **kwargs):
        # self.options = {}
        # self.options.update(kwargs)
        # self.mask = None
        # self.clf = clf(**kwargs)  # an sklearn object with a predict method.
        self.clf = SGDClassifier(**kwargs)
        # self.clf = LinearSVC(**kwargs)

    def fit(self, X, y):

        mask = y != -1

        X, y = check_X_y(X, y)
        self.classes_ = unique_labels(y[mask])

        self.X_ = X[mask]
        self.y_ = y[mask]

        self.clf.fit(self.X_, self.y_)
        return self

    def score(self, X, y, sample_weight=None):
        mask = y != -1
        X_strip = X[mask]
        y_strip = y[mask]

        return super(FilteredClassify, self).score(X_strip, y_strip)

    def predict(self, X):
        check_is_fitted(self, ['X_', 'y_'])
        X = check_array(X)
        picks = self.clf.predict(X)
        return picks
