import pytest
import datatest as dt
import pandas as pd
import nestor.keyword as kex

# todo: add testing for combined NE labels

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
                "one brown fox"
            ],
            "NE": ["I", "I", "I", "V", "I", "I", "X", "U", "N", "N I", "I", "N", "N I"],
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
                "one brown_animal"
            ],
            "notes": "",
            "score": [6.0, 5.0, 4.0, 3.0, 2.0, 1.0, 0.0, 0.0, 7.0, 8.0, 2.0, 1.5, 1.1],
        }
    ).set_index("tokens")


@pytest.fixture(scope="module")
def raw_text():
    return pd.Series(
        ["the quick brown fox jumped over the lazy dog",
         "the fox jumped over the dog",
         "the dog jumped over ten dogs",
         "the one brown fox"
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
         "the one brown_animal"
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
            ("quick", "I"),
            ("brown", "I"),
            ("fox", "I"),
            ("jumped", "V"),
            ("over", "O"),
            ("the", "O"),
            ("lazy", "I"),
            ("dog", "I"),
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
            ("dog", "I"),
            ("jumped", "V"),
            ("over", "O"),
            ("ten", "N I"),
            ("dogs", "N I"),
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
            ("one", "N I"),
            ("brown", "N I"),
            ("fox", "N I"),
        ],
    )

