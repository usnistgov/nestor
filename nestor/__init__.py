"""
**Quantifying tacit knowledge investigatory analysis**

Nestor is a toolkit for using Natural Language Processing (NLP) with efficient
user-interaction to perform structured data extraction with minimal annotation time-cost.
"""

# __version__ = "0.2.1"

__all__ = [
    # "keyword",
    "NLPSelect",
    "TokenExtractor",
    "TagExtractor"
    # 'tagplots',
    # "tagtrees",
    "datasets",
]
from nestor.keyword import TagExtractor, TokenExtractor, NLPSelect
from nestor.settings import CFG
