# from mlp import *
from embed import TopicVectors, SemanticVectors
from predict import FilteredClassify
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer


from sklearn.ensemble import ExtraTreesClassifier
from sklearn.linear_model import SGDClassifier

import preprocess as pre
corpus = pre.get_corpus()
df = pre.get_df()

y = pre.get_labeled_data(df['labels'].values)
# y = df['labels'].values
# sgd_w2v = Pipeline([
#     ('word2vec embedding', SemanticVectors()),
#     ('extract_labeled', FunctionTransformer(pre.get_labeled_data, validate=False)),  # extract labeled points
#     ('SGD Lin-SVC w/ElasticNet', SGDClassifier(class_weight='balanced',  # compensate for class freqs
#                                                penalty='elasticnet',   # L1 + L2 regularized
#                                                alpha=0.001,
#                                                n_iter=10))
# ])

sgd_w2v = Pipeline([
    ('word2vec embedding', SemanticVectors()),
    ('extract_labeled', FunctionTransformer(pre.get_labeled_data, validate=False)),  # extract labeled points
    ('SGD Lin-SVC w/ElasticNet', SGDClassifier(class_weight='balanced',  # compensate for class freqs
                                                  penalty='elasticnet',   # L1 + L2 regularized
                                                  alpha=0.001,
                                                  n_iter=10)
     )
])


# sgd_w2v.set_params(anova__k=10, svc__C=.1).fit(corpus, y)
sgd_w2v.fit(corpus, y)

print "score: {:2f}%".format((sgd_w2v.score(corpus, y))*100.)
