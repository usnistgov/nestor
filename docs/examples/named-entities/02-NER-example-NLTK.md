# NER Example: Using IOB output with NLTK

Much of the code in this example is adapted from the following tutorial:

https://towardsdatascience.com/named-entity-recognition-and-classification-with-scikit-learn-f05372f07ba2


```python
import numpy as np
import pandas as pd
from sklearn.feature_extraction import DictVectorizer
from sklearn.model_selection import train_test_split
```


```python
from nestor import keyword as kex
```

    /opt/miniconda3/envs/nestor-docs/lib/python3.9/site-packages/poetry_dynamic_versioning/__init__.py:416: TqdmExperimentalWarning: Using `tqdm.autonotebook.tqdm` in notebook mode. Use `tqdm.tqdm` instead to force console mode (e.g. in jupyter console)
      module = _state.original_import_func(name, globals, locals, fromlist, level)



```python
import sklearn_crfsuite
from sklearn_crfsuite import scorers
from sklearn_crfsuite import metrics
from collections import Counter
import nestor.datasets as dat
```

## Load data

Here, we are loading the excavator dataset and associated vocabulary from the Nestor package. 

To use this workflow with your own dataset and Nestor tagging, set up the following dataframes:
    
```
df = pd.read_csv(
    "original_data.csv"
)

df_1grams = pd.read_csv(
    "vocab1g.csv",
    index_col=0
)

df_ngrams = pd.read_csv(
    "vocabNg.csv",
    index_col=0
)
```


```python
df = dat.load_excavators()
# This vocab data inclues 1grams and Ngrams
df_vocab = dat.load_vocab("excavators")
```

## Prepare data for modeling

Select column(s) that inlcude text.


```python
nlp_select = kex.NLPSelect(columns=['OriginalShorttext'])
raw_text = nlp_select.transform(df.head(100))  # fixme (using abridged dataset here for efficiency)
```

    /Users/amc8/nestor/nestor/keyword.py:144: FutureWarning: The default value of regex will change from True to False in a future version.
      s.str.lower()  # all lowercase


Pass text data and vocab files from Nestor through `iob_extractor`


```python
iob = kex.iob_extractor(raw_text, df_vocab)
```

    /opt/miniconda3/envs/nestor-docs/lib/python3.9/site-packages/pandas/core/indexing.py:1732: SettingWithCopyWarning: 
    A value is trying to be set on a copy of a slice from a DataFrame
    
    See the caveats in the documentation: https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
      self._setitem_single_block(indexer, value, name)


Create X and y data, where y is the IOB labels


```python
X = iob.drop('NE', axis=1)
v = DictVectorizer(sparse=False)
X = v.fit_transform(X.to_dict('records'))
y = iob.NE.values
classes = np.unique(y)
classes = classes.tolist()
```

## SentenceGetter helper class


```python
class SentenceGetter(object):

    def __init__(self, data):
        self.n_sent = 1
        self.data = data
        self.empty = False
        agg_func = lambda s: [(w, t) for w, t in zip(s['token'].values.tolist(),
                                                           s['NE'].values.tolist())]
        self.grouped = self.data.groupby('doc_id').apply(agg_func)
        self.sentences = [s for s in self.grouped]

    def get_next(self):
        try:
            s = self.grouped['Sentence: {}'.format(self.n_sent)]
            self.n_sent += 1
            return s
        except:
            return None
```

## Feature vector helper functions


```python
def word2features(sent, i):
    """
        Creates feature vectors, accounting for surrounding tokens and whether or not the token is a number
    """
    word = sent[i][0]

    features = {
        'bias': 1.0,
        'word.lower()': word.lower(),
        'word[-3:]': word[-3:],
        'word[-2:]': word[-2:],
        'word.isdigit()': word.isdigit(),
    }
    if i > 0:
        word1 = sent[i - 1][0]
        features.update({
            '-1:word.isdigit()': word1.isdigit(),
        })
    else:
        features['BOS'] = True
    if i < len(sent) - 1:
        word1 = sent[i + 1][0]
        features.update({
            '+1:word.isdigit()': word1.isdigit(),
        })
    else:
        features['EOS'] = True

    return features
```


```python
def sent2features(sent):
    return [word2features(sent, i) for i in range(len(sent))]
```


```python
def sent2labels(sent):
    return [label for token, label in sent]
```


```python
def sent2tokens(sent):
    return [token for token, label in sent]
```

## Prepare data for modeling


```python
getter = SentenceGetter(iob)
mwos = getter.sentences
```


```python
X = [sent2features(mwo) for mwo in mwos]
y = [sent2labels(mwo) for mwo in mwos]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=0)
```

## Train and test model 

This example uses a CFR model; however, this is only one of many ways to perform NER


```python
crf = sklearn_crfsuite.CRF(
    algorithm='lbfgs',
    c1=0.1,
    c2=0.1,
    max_iterations=100,
    all_possible_transitions=True
)
```


```python
new_classes = classes.copy()
new_classes.pop()
```




    'O'




```python
crf.fit(X_train, y_train)
y_pred = crf.predict(X_test)
print(metrics.flat_classification_report(y_test, y_pred, labels = new_classes))
```

                  precision    recall  f1-score   support
    
             B-I       0.90      0.72      0.80        61
             B-P       0.57      0.80      0.67         5
            B-PI       0.67      1.00      0.80         2
             B-S       0.80      0.67      0.73        12
            B-SI       0.67      0.91      0.77        11
             I-I       0.33      0.38      0.35         8
            I-PI       0.67      1.00      0.80         2
             I-S       1.00      1.00      1.00         1
            I-SI       0.71      0.91      0.80        11
    
       micro avg       0.76      0.74      0.75       113
       macro avg       0.70      0.82      0.75       113
    weighted avg       0.79      0.74      0.75       113
    

