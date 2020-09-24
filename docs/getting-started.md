# Getting Started
To install `nestor`, utilize a python installation (preferrably an environment like `pyenv` or `conda`) to install from the Pypi repository:

```bash
pip install nist-nestor
```

The core `nestor` module is intended to assist analysts (and the UIs or pipelines the may create) in annotating technical text. If you just want to jump in to a more polished experience, head over to the [GUI Links](docs/gui-links.md) page. 

What does assistance in annotation *mean*? 


## Motivation 

NLP in technical domains often involves 

1. Narrowing down the set of concepts written about to a subset of *relevant*, well-defined, possibly related ones;
2. Annotating whether/where those concepts occur within documents of a dataset, for training or validation purposes.

This can take the form of named entity recognition (NER) training sets, lists of domain-specific stopwords, etc. 
In medical NLP, this often uses agreed-upon named-entity sets that have been added *by-hand* to several corpuses. 
Check out the [scispacy](https://allenai.github.io/scispacy/) page from Allen AI for an example: one set uses `disease` and `chemical`, another uses `dna`, `protein`, `cell-type`, `cell-line`, and `rna`, etc. 

Creating the set of concepts in a way that enough people can agree on a method for tagging their occurrence is incredibly time-consuming. 
Often, an analyst needs to iterate and prototype various entity sets, and test their coverage and usefulness in a specific task. 
This analyst needs a way to rapidly estimate the sets of entities --- the "tags" they will use --- that meaningfully represent the data at hand. 
The insight we bring to bear is that this does not need to be done *document-by-document* in order to be data-driven. 

## Workflow 

```mermaid
graph LR;
  text --> keywords
  keywords --> priorities
  keywords --> relationships
  priorities --> user[user typing]
  relationships --> user
  user --> keywords
end
```


### Core Idea

Nestor starts out with a dataset of records with certain columns containing text.
This text is cleaned up and scanned for **keywords** that are statistically important to the corpus (e.g. using sum-tfidf; [see @horn2017exploring]). 

This gives an analyst an overview of terms that happen often or in special contexts, and must be dealt with as relevant (or not) to their analyses.
Especially important are the term **priorities**: as one travels further down the list, terms are deemed less important *to the machine*, giving the user a sense of how algorithms are "seeing" the corpus. 

However, in techical text, shorthands and jargon quickly develop. 
What started out being called "hydraulic" or "air conditioning unit" may eventually be called "hyd" or "ACU", obscuring statistical significance of both. 
These **relationships** can be determined through similarity in a number of ways: in our experience a useful similarity is to use variations on *Levenstein distance* to catch misspellings or abbreviations, but there are many others. 

Both the keyterms and their relationships can now be passed to a user for them to **type** as needed, structuring the now-named-entities as needed. 
Importantly, this is done in order of percieved importance, minimizing wasted time!

> *types* available are determined by`entities` property of  the `nestor.CFG` configuration object, which is set to use a maintenance-centric entity type system by default (`problem`, `item`, `solution`). Future releases will allow customization of this list!

### The "too-hot" problem

Often a keyword won't make sense out-of-context: if "hot" is important to an HVAC maintenance dataset, it is definitely important! 
But it may refer to a room being "too hot" (a problem), or perhaps "hot water" (just an object). 
This means the user can't know what to *type* the "hot" entity without more context. 

Nestor uses the idea of *derived types*, so that context-sensitive keywords can be built out of otherwise ambiguous blocks. 

> Derived types are governed by the `derived` property of `nestor.CFG`. 
> Rules for creating them from atomic types are defined by the `entity_rules_map` property. 



