# ml-py
Maintenance Language Processing: python NLP for manufacturing-based structured data extraction

NOTE: this repository is under construction, and tutorial .ipynb documents are still being written. 
To see the most current work, see [recent source code](/mlp/keyword.py). 
For a look at planned functionality, you can brave the Jupyter Notebook [sandbox](/DictTags.ipynb), which contains raw-source code for a specific use-case.
## Pre-requisites
- scikit-learn
- pandas
- Textacy (+Spacy)
- tqdm
- gensim
## Purpose
There is often a large amount of maintenance data available for use in Smart Manufacturing Systems, but in a currently-unusable form: service tickets and maintenance logs. ML-py is a framework to use NLP for structured data extraction when only very few of the maintenance logs have been tagged appropriately. 

## Methods
DEPRECATED
1. Preprocess text & embed into vectors (LDA, NMF, W2V, +more via Textacy)
2. Train a classifier on the available labeled logs. Currently SVM (via SGD with sklearn)

## Upcoming/under-way
DEPRECATED
- ability to cross-validate and grid-search over the entire pipline (not currently supported in sklearn)
- addition of transduction menthods (label propagation) and other clf methods to train labeler. 
