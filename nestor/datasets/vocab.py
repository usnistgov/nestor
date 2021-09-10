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
        return "vocab-{}-{}g.csv".format(self, ng)

    def location(self, ngram: bool = False, remote: bool = False) -> Path:
        def location_local() -> Path:
            module_path = Path(__file__).parent
            return module_path / "resources" / self.filename(ngram)

        def location_gitlab() -> str:

            url = (
                "https://gitlab.nist.gov/gitlab/kea/nestor-suite/nestor/-/raw/"
                "bio-vocab/nestor/datasets/resources/{}"
            ).format(self.filename(ngram))
            return url

        def location_github() -> str:
            raise NotImplementedError("Not pushed to github yet!")
            return "NOT IMPLEMENTED"

        if not remote:
            return location_local()

        else:
            try:
                url = location_github()
            except NotImplementedError:
                from warnings import warn

                warn("GitHub Download not implemented yet!")
                url = location_gitlab()
            finally:
                # TODO: should we allow cache overwrites?
                return download_datafile(url, self.filename(ngram))


def load_vocab(
    vocab_option: VocabOption,
    base1g: bool = True,
    compound2g: bool = True,
    remote=False,
) -> pd.DataFrame:
    """convenience function to load provided nestor-compatible vocabulary files

    for a list of currently-provided options, see the [`VocabOptions` class](nestor.datasets.vocab.VocabOptions)

    """

    vocab_option = VocabOption[
        vocab_option
    ]  # coerce, allowing users to pass vanilla str

    def load_vocab_csv(filename: Path) -> pd.DataFrame:
        return pd.read_csv(filename, index_col=0)

    if not (base1g or compound2g):
        from warnings import warn

        warn("Must at least choose one vocab type... defaulting to 1g!")

    if compound2g:
        vocab2g = load_vocab_csv(vocab_option.location(ngram=True, remote=remote))

        if base1g:
            vocab = load_vocab_csv(vocab_option.location(ngram=False, remote=remote))
            return pd.concat([vocab, vocab2g])
        else:
            return vocab2g
    else:  # assume 1g
        return load_vocab_csv(vocab_option.location(ngram=False, remote=remote))
