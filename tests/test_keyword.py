import pytest
import datatest as dt
import pandas as pd
import nestor.keyword as kex

# todo: add testing for combined NE labels

"""
NE tags in testing: 
    I = item
    V = verb
    N = number
    NI = number-item 
"""

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
                "ten",
                "ten dogs",
                "dogs",
                "one",
                "one brown fox",
                "twenty one"
            ],
            "NE": ["I", "I", "I", "V", "I", "I", "X", "U", "N", "NI", "I", "N", "NI", "N"],
            "alias": [
                "fox",
                "brown_animal",
                "fast_animal",
                "jump",
                "dog",
                "slow_animal",
                "",
                "",
                "ten",
                "ten dogs",
                "dog",
                "one",
                "one brown_animal",
                "twenty_one"
            ],
            "notes": "",
            "score": [6.0, 5.0, 4.0, 3.0, 2.0, 1.0, 0.0, 0.0, 7.0, 8.0, 2.0, 1.5, 1.1, 1.2],
        }
    ).set_index("tokens")


@pytest.fixture(scope="module")
def raw_text():
    return pd.Series(
        ["the quick brown fox jumped over the lazy dog",
         "the fox jumped over the dog",
         "the dog jumped over ten dogs",
         "the one brown fox",
         "twenty one animals"
         ]
    )


def test_token_to_alias(raw_text, vocab):
    clean_text = kex.token_to_alias(raw_text, vocab)
    dt.validate(clean_text, str)
    dt.validate(
        clean_text,
        {"the fast_animal jump over the slow_animal",
         "the fox jump over the dog",
         "the dog jump over ten dogs",
         "the one brown_animal",
         "twenty_one animals"
         },
    )


# TODO add parametric test for plaintext/list-of-tup option
def test_iob_extractor_1g_tokens(raw_text, vocab):
    iob_format = kex.iob_extractor(raw_text, vocab)
    print(iob_format)
    dt.validate(iob_format.columns, {"token", "NE", "doc_id"})
    dt.validate(
        iob_format.query("doc_id==0")[["token", "NE"]].to_records(index=False),
        [
            ("the", "O"),
            ("quick", "B-I"),
            ("brown", "I-I"),
            ("fox", "I-I"),
            ("jumped", "B-V"),
            ("over", "O"),
            ("the", "O"),
            ("lazy", "B-I"),
            ("dog", "I-I"),
        ],
    )


def test_iob_extractor_2g_tokens(raw_text, vocab):
    iob_format = kex.iob_extractor(raw_text, vocab)
    # print(iob_format)
    dt.validate(iob_format.columns, {"token", "NE", "doc_id"})
    dt.validate(
        iob_format.query("doc_id==2")[["token", "NE"]].to_records(index=False),
        [
            ("the", "O"),
            ("dog", "B-I"),
            ("jumped", "B-V"),
            ("over", "O"),
            ("ten", "B-NI"),
            ("dogs", "I-NI"),
        ],
    )


def test_iob_extractor_extended_tokens(raw_text, vocab):
    iob_format = kex.iob_extractor(raw_text, vocab)
    # print(iob_format)
    dt.validate(iob_format.columns, {"token", "NE", "doc_id"})
    dt.validate(
        iob_format.query("doc_id==3")[["token", "NE"]].to_records(index=False),
        [
            ("the", "O"),
            ("one", "B-NI"),
            ("brown", "I-NI"),
            ("fox", "I-NI"),
        ],
    )

