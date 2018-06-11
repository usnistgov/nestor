import pandas as pd


def load_excavators(cleaned=False):
    """
    Helper function to load excavator toy dataset.

    Hodkiewicz, M., and Ho, M. (2016)
    "Cleaning historical maintenance work order data for reliability analysis"
    in Journal of Quality in Maintenance Engineering, Vol 22 (2), pp. 146-163.

    Parameters
    ----------
    cleaned : bool (default=False)
        whether to return the original dataset (False) or the dataset with
        keyword extraction rules applied (True), as described in Hodkiewicz and Ho (2016)

    Returns
    -------
    pandas.DataFrame
        columns :
            BscStartDate : initialization of MWO
            Asset : which excavator this MWO concerns (A, B, C, D, E)
            OriginalShorttext : natural language description of the MWO
            PMType : repair (PM01) or replacement (PM02)
            Cost : MWO expense (AUD)
    """
    if cleaned:
        df = pd.read_csv('excavators-cleaned.csv')
    else:
        df = pd.read_csv('excavators.csv')
    return df
