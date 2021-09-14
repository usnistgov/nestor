# Output tags in IOB format for NER analysis



```python
import pandas as pd
from pathlib import Path
from nestor import keyword as kex
import nestor.datasets as nd
```


```python
# Get raw MWOs
df = (nd.load_excavators(cleaned=False)  # already formats dates
#       .rename(columns={'BscStartDate': 'StartDate'})
      )

# Change date column to DateTime objects
df.head(5)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>BscStartDate</th>
      <th>Asset</th>
      <th>OriginalShorttext</th>
      <th>PMType</th>
      <th>Cost</th>
    </tr>
    <tr>
      <th>ID</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2004-07-01</td>
      <td>A</td>
      <td>BUCKET WON'T OPEN</td>
      <td>PM01</td>
      <td>183.05</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2005-03-20</td>
      <td>A</td>
      <td>L/H BUCKET CYL LEAKING.</td>
      <td>PM01</td>
      <td>407.40</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2006-05-05</td>
      <td>A</td>
      <td>SWAP BUCKET</td>
      <td>PM01</td>
      <td>0.00</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2006-07-11</td>
      <td>A</td>
      <td>FIT BUCKET TOOTH</td>
      <td>PM01</td>
      <td>0.00</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2006-11-10</td>
      <td>A</td>
      <td>REFIT BUCKET TOOTH</td>
      <td>PM01</td>
      <td>1157.27</td>
    </tr>
  </tbody>
</table>
</div>




```python
vocab=nd.load_vocab('excavators')#.dropna(subset=['alias'])
vocab
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>NE</th>
      <th>alias</th>
      <th>notes</th>
      <th>score</th>
    </tr>
    <tr>
      <th>tokens</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>replace</th>
      <td>S</td>
      <td>replace</td>
      <td>NaN</td>
      <td>0.033502</td>
    </tr>
    <tr>
      <th>bucket</th>
      <td>I</td>
      <td>bucket</td>
      <td>NaN</td>
      <td>0.018969</td>
    </tr>
    <tr>
      <th>repair</th>
      <td>S</td>
      <td>repair</td>
      <td>NaN</td>
      <td>0.017499</td>
    </tr>
    <tr>
      <th>grease</th>
      <td>I</td>
      <td>grease</td>
      <td>NaN</td>
      <td>0.017377</td>
    </tr>
    <tr>
      <th>leak</th>
      <td>P</td>
      <td>leak</td>
      <td>NaN</td>
      <td>0.016591</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>1boily 19</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0.000046</td>
    </tr>
    <tr>
      <th>shd 1fitter</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0.000046</td>
    </tr>
    <tr>
      <th>19 01</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0.000046</td>
    </tr>
    <tr>
      <th>01 10</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0.000046</td>
    </tr>
    <tr>
      <th>1fitter 1boily</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0.000046</td>
    </tr>
  </tbody>
</table>
<p>6767 rows × 4 columns</p>
</div>




```python
iob = kex.iob_extractor(df.OriginalShorttext, vocab)
iob
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>token</th>
      <th>NE</th>
      <th>doc_id</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>bucket</td>
      <td>B-I</td>
      <td>0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>won</td>
      <td>O</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>open</td>
      <td>O</td>
      <td>0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>bucket</td>
      <td>B-I</td>
      <td>1</td>
    </tr>
    <tr>
      <th>4</th>
      <td>cyl</td>
      <td>B-I</td>
      <td>1</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>24663</th>
      <td>fault</td>
      <td>B-P</td>
      <td>5484</td>
    </tr>
    <tr>
      <th>24664</th>
      <td>front</td>
      <td>O</td>
      <td>5484</td>
    </tr>
    <tr>
      <th>24665</th>
      <td>found</td>
      <td>O</td>
      <td>5484</td>
    </tr>
    <tr>
      <th>24666</th>
      <td>wire</td>
      <td>B-I</td>
      <td>5484</td>
    </tr>
    <tr>
      <th>24667</th>
      <td>no</td>
      <td>O</td>
      <td>5484</td>
    </tr>
  </tbody>
</table>
<p>24668 rows × 3 columns</p>
</div>


