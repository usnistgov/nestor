import nestor.settings as ns
import pytest_check as check
import pytest

small_dict = {
        'I': {'A': 1},
        'II': 'B',
        'III': {
            'C': {'2': 'a'},
            'D': {'3': 'b'},
        }
    }

nestorParams = ns.nestor_params()


@pytest.mark.parametrize(
    'test_path,retrieved',
    [('I.A', 1), ('III.C.2', 'a'), ('III.D', {'3': 'b'})]
)
def test_find_node_from_path(test_path, retrieved):
    assert ns.find_node_from_path(small_dict, test_path) == retrieved


@pytest.mark.parametrize(
    'test_val,found_path',
    [(1, 'I.A'), ('a', 'III.C.2'), ('3', 'III.D.3')]
)
def test_find_path_from_key(test_val, found_path):
    assert next(ns.find_path_from_key(small_dict, test_val)) == found_path


def test_default_entities():
    assert nestorParams.entities == ['P', 'I', 'S', 'PI', 'SI', 'U', 'X']


def test_default_atomics():
    assert set(nestorParams.atomics) == {'I', 'P', 'S'}

@pytest.mark.parametrize(
    'combine,result',
    [('P I', 'PI'), ('I P', 'PI'), ('I I', 'I'), ('P P', 'X')]
)
def test_default_rules(combine, result):
    assert nestorParams.entity_rules_map[combine] == result


def test_default_datatype():
    names = list(nestorParams.datatype_search('name'))

    assert (
        'technician.name' in names
    ) and (
        names[0] in nestorParams.datatypes
    )
