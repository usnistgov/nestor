import datatest as dt
import nestor.datasets as nd
import numpy as np
import pandas as pd
import pytest
from datatest import Deviation, Extra, Invalid, Missing, accepted

pytestmark = pytest.mark.filterwarnings("ignore:subset and superset warning")


@pytest.fixture(scope="session", autouse=True)
def pandas_integration():
    dt.register_accessors()


# @pytest.fixture(scope="session")
# @dt.working_directory(get_nestor_cache_dir())
# def data_dir():
#     return Path('data')  # Returns DataFrame.


@pytest.fixture(params=[True, False])
def clean_version(request):
    return request.param


class TestExcavators:
    @pytest.fixture
    def df(self, clean_version):
        df = nd.load_excavators(cleaned=clean_version)
        return df

    @pytest.fixture
    def col_names(self, clean_version):
        if clean_version:
            cols = [
                "BscStartDate",
                "Asset",
                "OriginalShorttext",
                "PMType",
                "Cost",
                "RunningTime",
                "MajorSystem",
                "Part",
                "Action",
                "Variant",
                "FM",
                "Location",
                "Comments",
                "FuncLocation",
                "SuspSugg",
                "Rule",
            ]
        else:
            cols = ["BscStartDate", "Asset", "OriginalShorttext", "PMType", "Cost"]
        return cols

    def test_column_names(self, df, col_names):
        df.columns.validate(col_names)

    def test_datatypes(self, df):
        required_types = {
            "BscStartDate": np.dtype("<M8[ns]"),
            "Asset": nd.excavators.AssetType,
            "OriginalShorttext": pd.StringDtype(),
            "PMType": nd.excavators.PMType,
            "Cost": np.dtype(float),
        }
        with accepted(Extra):
            df.dtypes.validate(required_types)


class TestVocab:
    @pytest.fixture(params=["excavators"] + [x.value for x in nd.vocab.VocabOption])
    def vocab_name(self, request):
        return request.param

    @pytest.fixture(params=[True, False])
    def compound2g(self, request):
        return request.param

    @pytest.fixture(params=[True, False])
    def base1g(self, request):
        return request.param

    @pytest.fixture(params=[True, False])
    def remote(self, request):
        return request.param

    @pytest.fixture
    def vocab(self, vocab_name, compound2g, base1g, remote):
        return nd.load_vocab(
            vocab_name, base1g=base1g, compound2g=compound2g, remote=remote
        )

    def test_vocab_headers(self, vocab):
        required_headers = {"NE", "alias"}
        possible_headers = required_headers | {"score", "notes"}
        vocab.columns.validate.superset(required_headers)
        vocab.columns.validate.subset(possible_headers)

    def test_vocab_index(self, vocab):
        vocab.index.validate(str)
        assert vocab.index.name == "tokens"


if __name__ == "__main__":
    import sys

    sys.exit(pytest.main(sys.argv))
