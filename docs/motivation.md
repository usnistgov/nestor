# Getting Started
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
