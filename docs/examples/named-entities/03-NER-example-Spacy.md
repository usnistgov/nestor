# NER Example: Using IOB output SpaCy


```python
import os
import pandas as pd
from nestor import keyword as kex
import nestor.datasets as dat
from sklearn.model_selection import train_test_split
```

    /opt/miniconda3/envs/nestor-docs/lib/python3.9/site-packages/poetry_dynamic_versioning/__init__.py:416: TqdmExperimentalWarning: Using `tqdm.autonotebook.tqdm` in notebook mode. Use `tqdm.tqdm` instead to force console mode (e.g. in jupyter console)
      module = _state.original_import_func(name, globals, locals, fromlist, level)


## Helper functions


```python
def create_iob_format_data(df_iob: pd.DataFrame, ner_file_path: str):
    """
    Create .iob file with token-per-line IOB format
    (see https://github.com/explosion/spaCy/blob/master/extra/example_data/ner_example_data/ner-token-per-line.iob
        for example format)

    Parameters
    ----------
    df_iob: DataFrame created by kex.iob_extractor()
    ner_file_path: pathname for where to save the file in IOB-formatted output, use ".iob" extension

    Returns
    -------

    """
    # to do: make sure that
    # Convert IOB DataFrame to token-per-line tsv file
    df_iob[["token", "NE"]].to_csv(ner_file_path, sep="\t", index=False, header=False)
```


```python
def convert_iob_to_spacy_file(ner_file_path: str):
    """

    Parameters
    ----------
    ner_file_path: pathname for where to save the file in IOB-formatted output, use ".iob" extension, must be in format
        as shown here: https://github.com/explosion/spaCy/blob/master/extra/example_data/ner_example_data/ner-token-per-line.iob

    Returns
    -------

    """
    # todo: make this command customizable, handle tokens better (actually need to group by MWO)
    os.system("python -m spacy convert -c ner -s -n 10 -b en_core_web_sm " + ner_file_path + " .")
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

Split data into training and test sets.


```python
nlp_select = kex.NLPSelect(columns = ['OriginalShorttext'])
raw_text = nlp_select.transform(df)   
train, test = train_test_split(raw_text, test_size=0.2, random_state=1, shuffle=False)
test = test.reset_index(drop=True)
```

    /Users/amc8/nestor/nestor/keyword.py:144: FutureWarning: The default value of regex will change from True to False in a future version.
      s.str.lower()  # all lowercase


Pass text data and vocab files from Nestor through `iob_extractor`


```python
iob_train = kex.iob_extractor(train, df_vocab)
iob_test = kex.iob_extractor(test, df_vocab)
```

    /opt/miniconda3/envs/nestor-docs/lib/python3.9/site-packages/pandas/core/indexing.py:1732: SettingWithCopyWarning: 
    A value is trying to be set on a copy of a slice from a DataFrame
    
    See the caveats in the documentation: https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
      self._setitem_single_block(indexer, value, name)


Create `.iob` files (these are essentially tsv files with proper IOB tag format). Convert `.iob` files to `.spacy` binary files


```python
# pathname/document title should match what is in `congif.cfg file`
create_iob_format_data(iob_train, "iob_data.iob")
convert_iob_to_spacy_file("iob_data.iob")
create_iob_format_data(iob_test, "iob_valid.iob")
convert_iob_to_spacy_file("iob_valid.iob")
```

    [38;5;4mℹ Auto-detected token-per-line NER format[0m
    [38;5;4mℹ Grouping every 10 sentences into a document.[0m
    [38;5;4mℹ Segmenting sentences with parser from model 'en_core_web_sm'.[0m
    [38;5;2m✔ Generated output file (3 documents): iob_data.spacy[0m
    [38;5;4mℹ Auto-detected token-per-line NER format[0m
    [38;5;4mℹ Grouping every 10 sentences into a document.[0m
    [38;5;4mℹ Segmenting sentences with parser from model 'en_core_web_sm'.[0m
    [38;5;2m✔ Generated output file (2 documents): iob_valid.spacy[0m


## SpaCy model

Run data through basic spaCy training (relies on `spacy_config.cfg`). This stage can be customized as needed for your particular modeling and analysis.


```python
# Run data through basic spacy training for proof of concept.
os.system("python -m spacy train spacy_config.cfg --output ./output")
```

    [2021-09-13 16:05:18,151] [INFO] Set up nlp object from config
    [2021-09-13 16:05:18,158] [INFO] Pipeline: ['tok2vec', 'ner']
    [2021-09-13 16:05:18,161] [INFO] Created vocabulary
    [2021-09-13 16:05:18,161] [INFO] Finished initializing nlp object
    [2021-09-13 16:05:20,132] [INFO] Initialized pipeline components: ['tok2vec', 'ner']


    [38;5;4mℹ Saving to output directory: output[0m
    [38;5;4mℹ Using CPU[0m
    [1m
    =========================== Initializing pipeline ===========================[0m
    [38;5;2m✔ Initialized pipeline[0m
    [1m
    ============================= Training pipeline =============================[0m
    [38;5;4mℹ Pipeline: ['tok2vec', 'ner'][0m
    [38;5;4mℹ Initial learn rate: 0.001[0m
    E    #       LOSS TOK2VEC  LOSS NER  ENTS_F  ENTS_P  ENTS_R  SCORE 
    ---  ------  ------------  --------  ------  ------  ------  ------
      0       0          0.00   4978.96   41.83   32.95   57.26    0.42
     66     200      16074.04  325701.04   78.63   78.54   78.72    0.79
    133     400      12938.59  16834.67   79.33   79.40   79.25    0.79
    200     600       7677.68   5585.41   79.80   79.20   80.42    0.80
    266     800       5287.22   3012.98   80.88   80.22   81.56    0.81
    333    1000       4091.20   2108.87   81.15   80.79   81.52    0.81
    400    1200       3428.38   1523.10   81.52   81.34   81.71    0.82
    466    1400       2744.81   1197.14   81.34   80.50   82.20    0.81
    533    1600       2719.90   1080.46   81.74   81.61   81.86    0.82
    600    1800       2572.00    924.06   81.55   81.17   81.93    0.82
    666    2000       2198.79    778.36   80.02   79.01   81.07    0.80
    733    2200       2591.83    842.59   80.89   80.28   81.52    0.81
    800    2400       1806.06    614.88   80.42   80.27   80.57    0.80
    866    2600       1772.40    517.44   80.72   80.57   80.88    0.81
    933    2800       2164.69    563.90   80.20   79.80   80.61    0.80
    1000    3000       2872.69    603.25   80.55   80.49   80.61    0.81
    1066    3200       1715.34    479.58   80.19   79.62   80.76    0.80
    [38;5;2m✔ Saved pipeline to output directory[0m
    output/model-last





    0




```python

```
