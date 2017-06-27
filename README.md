# ml-py
Maintenance Language Processing: python NLP for manufacturing-based structured data extraction

## Pre-requisites
- sklearn
- pandas
- Textacy (+Spacy)

## Purpose
There is often a large amount of maintenance data available for use in Smart Manufacturing Systems, but in a currently-unusable form: service tickets and maintenance logs. ML-py is a framework to use NLP for structured data extraction when only very few of the maintenance logs have been tagged appropriately. 

## Methods
1. Preprocess text & embed into vectors (LDA, NMF, W2V, +more via Textacy)
2. Train a classifier on the available labeled logs. Currently SVM (via SGD with sklearn)

## Upcoming/under-way
- ability to cross-validate and grid-search over the entire pipline (not currently supported in sklearn)
- addition of transduction menthods (label propagation) and other clf methods to train labeler. 
