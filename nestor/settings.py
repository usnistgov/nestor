from pathlib import Path
import yaml
from itertools import product

__all__ = [
    'nestor_params',
    'NestorParams',
]


def nestor_fnames():
    """return defult file being used by nestor (could use environment
    variables, etc. in the future), in order of priority"""

    default_cfg = Path(__file__).parent/'settings.yaml'

    return default_cfg


def nestor_params_from_files(fname):
    """Build up a :class:`nestor.NestorParams` object from the default
    config file locations"""
    d = yaml.safe_load(open(fname))
    cfg = NestorParams(**d)
    return cfg


def nestor_params():
    """function to instantiate a :class:`nestor.NestorParams` instance from
    the default nestor config/type .yaml files"""
    fnames = nestor_fnames()
    # could check they exist, probably
    return nestor_params_from_files(fnames)


class NestorParams(dict):

    # TODO rewrite using dataclasses and entity-rel model (v0.4)
    def __init__(self, *arg, **kw):
        super(NestorParams, self).__init__(*arg, **kw)
        self._datatypes = None
        self._entities = None
        self._entity_rules = None
        self._atomics = None

    def datatype_search(self, property_name):
        return find_path_from_key(self['datatypes'], property_name)

    @property
    def datatypes(self):
        if self._datatypes is None:
            self._datatypes = flatten_dict(self['datatypes'])
        return self._datatypes

    @property
    def entities(self):
        if self._entities is None:
            # self._entities = ''.join(
            #     self['entities']['types']['atomic'].keys()
            # )
            self._entities = leafnames(self['entities']['types'])
            # TODO: need NON-dict members of `entities`...!
        return self._entities

    @property
    def atomics(self):
        if self._atomics is None:
            self._atomics = find_node_from_path(
                self,
                next(find_path_from_key(self, 'atomic'))
            ).keys()
        return self._atomics

    @property
    def entity_rules_map(self):
        if self._entity_rules is None:
            raw_rules = self['entities']['rules']
            rules = {k: [set(i) for i in v] for k, v in raw_rules.items()}

            NE_comb = {' '.join(i) for i in product(self.entities, repeat=2)}

            def apply_rules(pair):
                s = set(pair.split(' '))
                query = (e for e, rul in rules.items() if s in rul)
                return next(query, '')  # if no match

            self._entity_rules = dict(zip(NE_comb, map(apply_rules, NE_comb)))
        return self._entity_rules


def find_node_from_path(dataDict, pathstr):
    """
    Gets a specific leaf/branch of a nested dict, by passing a `.`-separated
    string of keys. NB: Requires all accessed keys in `dataDict` to be `str`!
    Parameters
    ----------
    dataDict: dict
        potentially nested, keyed on strings
    pathstr: string of dot-separated key path to traverse/retrieve

    Returns
    -------
    object
    """
    maplist = pathstr.split('.')
    first, rest = maplist[0], '.'.join(maplist[1:])
    if rest:
        # if `rest` is not empty, run the function recursively
        return find_node_from_path(dataDict[first], rest)
    else:
        return dataDict[first]


def find_path_from_key(d, value, join='.'):
    """
    Lookup a value or key in a nested dict, yielding the path(s) that reach
    it as concatenated strings (e.g. for making pandas columns)

    If `value` is a key in any of the levels, will yield a string of all keys to
    reach it (inclusive). If `value` is a value, string will be exclusively keys

    hackey pattern matching

    Parameters
    ----------
    d: dict
        Must have keys/values of type str
    value: str
        value (or key) to search for
    join: str
        connector between key names
    """
    for k, v in d.items():
        # check if not leaf of tree
        if isinstance(v, dict):
            # reached the desired key
            if value in v.keys():
                yield join.join([k] + [value])
            # recursively check keys
            for p in find_path_from_key(v, value, join=join):
                if p:  # non-empty
                    yield join.join([k] + [p])
        # if we've reached a leaf
        elif v == value:
            yield k


def flatten_dict(d):
    """
    Turn `d` into a one-level dict keyed on `.`-joined path strings
    Parameters
    ----------
    d: dict

    Returns
    -------
    dict
    """
    new_dict = {}
    for key, value in d.items():
        if type(value) == dict:
            _dict = {
                '.'.join([key, _key]): _value
                for _key, _value in flatten_dict(value).items()
            }
            new_dict.update(_dict)
        else:
            new_dict[key] = value
    return new_dict


def leafnames(d):
    """
    Find keys of leaf-items in a nested dict, using recursion.
    Parameters
    ----------
    d

    Returns
    -------

    """
    keylist = []

    def get_keys(doc):
        if isinstance(doc, dict):
            for k, v in doc.items():
                if not isinstance(v, dict):
                    keylist.append(k)  # side-effect :(
                get_keys(v)
        return
    get_keys(d)
    return keylist
