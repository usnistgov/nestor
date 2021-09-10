from pathlib import Path
import pandas as pd
from enum import Enum, IntEnum
from .utils import download_datafile


class VocabOption(str, Enum):
    """Available vocabulary files provided by Nestor

    Files will be hosted in the GitHub repository (but *not* in PyPi). Filenames are expected
    to follow the template

    > `vocab-OPTION-Ng.csv`

    where `N` can be 1 or 2.

    **Valid Options**:

    `excavators` or `excavators2018sexton`
    :    Tag aliases and types used in *Benchmarking for Keyword Extraction Methodologies
         in Maintenance Work Orders* (Sexton et al, 2018). Created using the UWA Excavators
         dataset (see [`load_excavators()`](nestor.datasets.excavators.load_excavators))

    """

    excavators2018sexton = "excavators2018sexton"
    excavators = "excavators2018sexton"

    def filename(self, ngram: bool = False) -> str:
        """template for consistent vocab access"""
        ng = 2 if ngram else 1
        return "vocab-{}-{}.csv".format(self, ng)

    def location(self, ngram: bool = False, remote: bool = False) -> Path:
        def location_local() -> Path:
            module_path = Path(__file__).parent
            return module_path / "resources" / self.filename(ngram)

        def location_gitlab() -> Path:
            return

        def location_github() -> Path:
            return
