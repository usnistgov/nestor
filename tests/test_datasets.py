import datatest as dt
import nestor.datasets as nd
import numpy as np
import pandas as pd
import pytest
from datatest import Deviation, Extra, Invalid, Missing, accepted


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


if __name__ == "__main__":
    import sys

    sys.exit(pytest.main(sys.argv))
