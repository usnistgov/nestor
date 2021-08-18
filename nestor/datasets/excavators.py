from pathlib import Path
import pandas as pd
from .utils import download_datafile

_RAW_URL = "https://prognosticsdl.systemhealthlab.com/dataset/f4780ee0-efa6-45b6-b6dc-cfc60bfb5687/resource/7c2b0da9-8a8a-4d3a-8102-5d02ea5ba57a/download/excavator_2015_raw_forpdl.csv"
_CLEAN_URL = "https://prognosticsdl.systemhealthlab.com/dataset/f4780ee0-efa6-45b6-b6dc-cfc60bfb5687/resource/72033940-667f-4815-8d6b-60dd7acbad2e/download/excavator_2015_cleaned_forpdl.csv"

AssetType = pd.CategoricalDtype(categories=list("ABCDE"))
PMType = pd.CategoricalDtype(categories=[f"PM{i:02}" for i in [1, 2, 4, 5, 6, 13]])


def _download_excavators(cleaned: bool = False, overwrite: bool = False) -> Path:

    url = _CLEAN_URL if cleaned else _RAW_URL
    fname = "excavators-cleaned.csv" if cleaned else "excavators.csv"
    path: Path = download_datafile(url, fname, overwrite=overwrite)
    return path


def load_excavators(cleaned=False):
    """
    Helper function to load excavator toy dataset.

    Hodkiewicz, M., and Ho, M. (2016)
    "Cleaning historical maintenance work order data for reliability analysis"
    in Journal of Quality in Maintenance Engineering, Vol 22 (2), pp. 146-163.

    BscStartDate| Asset | OriginalShorttext | PMType | Cost
    --- | --- | --- | --- | ---
    initialization of MWO | which excavator this MWO concerns (A, B, C, D, E)| natural language description of the MWO| repair (PM01) or replacement (PM02) | MWO expense (AUD)

    Args:
        cleaned (bool): whether to return the original dataset (False) or the dataset with
            keyword extraction rules applied (True), as described in Hodkiewicz and Ho (2016)

    Returns:
        pandas.DataFrame: raw data for use in testing nestor and subsequent workflows

    """

    csv_filename = _download_excavators(cleaned=cleaned)

    df = (
        pd.read_csv(
            csv_filename, parse_dates=["BscStartDate"], sep=",", escapechar="\\"
        )
        .astype(
            {
                "Asset": AssetType,
                "OriginalShorttext": pd.StringDtype(),
                "PMType": PMType,
                "Cost": float,
            }
        )
        .rename_axis("ID")
    )

    return df
