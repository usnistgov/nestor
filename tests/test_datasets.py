import nestor.datasets as nd
import pytest_check as check
import pytest


@pytest.mark.parametrize(
    "cleaned,columns",
    [
        (False, ["BscStartDate", "Asset", "OriginalShorttext", "PMType", "Cost"]),
        (
            True,
            [
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
            ],
        ),
    ],
)
def test_find_node_from_path(cleaned, columns):
    assert list(nd.load_excavators(cleaned=cleaned).columns) == columns
