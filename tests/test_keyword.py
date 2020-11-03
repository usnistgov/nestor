import pytest
import datatest as dt
import pandas as pd
import nestor.keyword as kex


@pytest.fixture(scope="module")
def vocab():
    return pd.DataFrame(
        {
            "tokens": [
                "fox",
                "brown fox",
                "quick brown fox",
                "jumped",
                "dog",
                "lazy dog",
                "the",
                "over",
            ],
            "NE": ["I", "I", "I", "V", "I", "I", "X", "U"],
            "alias": [
                "fox",
                "brown_animal",
                "fast_animal",
                "jump",
                "dog",
                "slow_animal",
                "",
                "",
            ],
            "notes": "",
            "score": [6.0, 5.0, 4.0, 3.0, 2.0, 1.0, 0.0, 0.0],
        }
    ).set_index("tokens")


@pytest.fixture(scope="module")
def raw_text():
    return pd.Series(
        ["the quick brown fox jumped over the lazy dog", "the fox jumped over the dog",]
    )


def test_token_to_alias(raw_text, vocab):
    clean_text = kex.token_to_alias(raw_text, vocab)
    dt.validate(clean_text, str)
    dt.validate(
        clean_text,
        {"the fast_animal jump over the slow_animal", "the fox jump over the dog"},
    )
