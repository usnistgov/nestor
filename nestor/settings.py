from pathlib import Path
from itertools import product
import yaml


__all__ = [
    "nestor_params",
    "NestorParams",
]


def nestor_fnames():
    """return defult file being used by nestor (could use environment
    variables, etc. in the future), in order of priority"""

    default_cfg = Path(__file__).parent / "settings.yaml"

    return default_cfg


def nestor_params_from_files(fname):
    """Build up a :class:`nestor.NestorParams` object from the default
    config file locations"""

    settings_dict = yaml.safe_load(open(fname))
    cfg = NestorParams(**settings_dict)
    return cfg


def nestor_params():
    """function to instantiate a :class:`nestor.NestorParams` instance from
    the default nestor config/type .yaml files"""
    fnames = nestor_fnames()
    # could check they exist, probably
    return nestor_params_from_files(fnames)


class NestorParams(dict):
    def __init__(self, *arg, **kw):
        super(NestorParams, self).__init__(*arg, **kw)
        self._datatypes = None
        self._entities = None
        self._entity_rules = None
        self._atomics = None
        self._holes = None
        self._derived = None

    def datatype_search(self, property_name):
        return find_path_from_key(self["datatypes"], property_name)

    @property
    def datatypes(self):
        if self._datatypes is None:
            self._datatypes = flatten_dict(self["datatypes"])
        return self._datatypes

    @property
    def entities(self):
        if self._entities is None:
            self._entities = leafnames(self["entities"]["types"])
        return self._entities

    @property
    def atomics(self):
        if self._atomics is None:
            self._atomics = find_node_from_path(
                self, next(find_path_from_key(self, "atomic"))
            ).keys()
        return list(self._atomics)

    @property
    def holes(self):
        if self._holes is None:
            self._holes = find_node_from_path(
                self, next(find_path_from_key(self, "hole"))
            ).keys()
        return list(self._holes)

    @property
    def derived(self):
        if self._derived is None:
            self._derived = find_node_from_path(
                self, next(find_path_from_key(self, "derived"))
            ).keys()
        return list(self._derived)

    @property
    def entity_rules_map(self):
        if self._entity_rules is None:
            raw_rules = self["entities"]["rules"]
            rules = {k: [set(i) for i in v] for k, v in raw_rules.items()}

            entity_comb = {  # all combinations of entities
                " ".join(i) for i in product(self.entities, repeat=2)
            }

            def apply_rules(pair):
                ent_set = set(pair.split(" "))  # ordering doesn't matter
                query = (e for e, rul in rules.items() if ent_set in rul)
                return next(query, "")  # if no match

            self._entity_rules = dict(zip(entity_comb, map(apply_rules, entity_comb)))
        return self._entity_rules


def find_node_from_path(data_dict, pathstr):
    """
    Gets a specific leaf/branch of a nested dict, by passing a `.`-separated
    string of keys. NB: Requires all accessed keys in `dataDict` to be `str`!
    Parameters
    ----------
    data_dict: dict
        potentially nested, keyed on strings
    pathstr: string of dot-separated key path to traverse/retrieve

    Returns
    -------
    object
    """
    maplist = pathstr.split(".")
    first, rest = maplist[0], ".".join(maplist[1:])
    if rest:
        # if `rest` is not empty, run the function recursively
        return find_node_from_path(data_dict[first], rest)

    return data_dict[first]


def find_path_from_key(deep_dict, value, join="."):
    """
    Lookup a value or key in a nested dict, yielding the path(s) that reach
    it as concatenated strings (e.g. for making pandas columns)

    If `value` is a key in any of the levels, will yield a string of all keys to
    reach it (inclusive). If `value` is a value, string will be exclusively keys

    hackey pattern matching

    Parameters
    ----------
    deep_dict: dict
        Must have keys/values of type str
    value: str
        value (or key) to search for
    join: str
        connector between key names
    """
    for key, val in deep_dict.items():
        # check if not leaf of tree
        if isinstance(val, dict):
            # reached the desired key
            if value in val.keys():
                yield join.join([key] + [value])
            # recursively check keys
            for path in find_path_from_key(val, value, join=join):
                if path:  # non-empty
                    yield join.join([key] + [path])
        # if we've reached a leaf
        elif val == value:
            yield key


def flatten_dict(deep_dict):
    """Turn `deep_dict` into a one-level dict keyed on `.`-joined
    path strings"""
    new_dict = {}
    for key, value in deep_dict.items():
        if isinstance(value, dict):
            _dict = {
                ".".join([key, _key]): _value
                for _key, _value in flatten_dict(value).items()
            }
            new_dict.update(_dict)
        else:
            new_dict[key] = value
    return new_dict


def leafnames(deep_dict):
    """
    Find keys of leaf-items in a nested dict, using recursion.
    Parameters
    ----------
    deep_dict

    Returns
    -------

    """
    keylist = []

    def get_keys(doc):
        if isinstance(doc, dict):
            for key, val in doc.items():
                if not isinstance(val, dict):
                    keylist.append(key)  # side-effect :(
                get_keys(val)

    get_keys(deep_dict)
    return keylist
