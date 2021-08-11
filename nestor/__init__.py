"""
**Quantifying tacit knowledge investigatory analysis**

Nestor is a toolkit for using Natural Language Processing (NLP) with efficient
user-interaction to perform structured data extraction with minimal annotation time-cost.
"""

# __version__ = "0.2.1"

__all__ = [
    "keyword",
    # 'tagplots',
    "tagtrees",
    "datasets",
]

from nestor.settings import nestor_params
import os
from pathlib import Path

CFG = nestor_params()

DEFAULT_CACHE = Path.home() / ".nestor"


def get_nestor_cache_dir() -> Path:
    """return the location of nestor's cache directory

    Looks for a `$NESTOR_CACHE` environment variable.
    If none exists, returns the default `$HOME/.nestor/`
    """
    cache_str = os.environ.get("NESTOR_CACHE", str(DEFAULT_CACHE))
    return Path(cache_str)


def set_nestor_cache_dir(dir: Path, migrate: bool = False) -> None:
    pass
