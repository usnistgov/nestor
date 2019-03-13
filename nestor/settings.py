from pathlib import Path
import yaml
from itertools import product
from collections.abc import MutableMapping
import functools

__all__ = [
    'Settings'
]

_deprecated_map = dict()

def getFromDict(dataDict, mapstr):
    maplist = mapstr.split('.')
    first, rest = maplist[0], '.'.join(maplist[1:])
    if rest:
        # if `rest` is not empty, run the function recursively
        return getFromDict(dataDict[first], rest)
    else:
        return dataDict[first]

def find_key_path(d, value, join='.'):
    """
    Lookup a value or key in a nested dict, yielding the path(s) that reach
    it as concatenated strings (e.g. for making pandas columns)

    If `value` is a key in any of the levels, will yield a string of all keys to
    reach it (inclusive). If `value` is a value, string will be exclusively keys


    Parameters
    ----------
    d: dict
        Must have keys/values of type str
    value: str
        value (or key) to search for
    join: str
        connector between key names
    """
    for k,v in d.items():
        # check if not leaf of tree
        if isinstance(v, dict):
            # reached the desired key
            if value in v.keys():
                yield join.join([k] + [value])
            # recursively check keys
            for p in find_key_path(v, value, join=join):
                if p:  # non-empty
                    yield join.join([k] + [p])
        # if we've reached a leaf
        elif v == value:
            yield k


class NestorParams(MutableMapping, dict):

    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def __setitem__(self, key, val):
        try:
            if key in _deprecated_map:
                pass
            try:
                cval = self.validate[key](val)
            except ValueError as ve:
                raise ValueError("Key %s: %s" % (key, str(ve)))
            dict.__setitem__(self, key, cval)
        except KeyError:
            raise KeyError(
                '%s is not a valid rc parameter. See rcParams.keys() for a '
                'list of valid parameters.' % (key,))

class Settings:
    def __init__(self, db=False):
        self._store_path = Path(__file__).parent/'store_data'
        self.data_types = 'csvHeader.yaml'
        self.entity_rules = 'entity_rules.yaml'

        # default to unused/unread
        self._db_schema = None
        if db:
            self.db_schema = 'DatabaseSchema.yaml'

    @property
    def data_types(self):
        # pre-defined maintenance data types
        return self._data_types

    @data_types.setter
    def data_types(self, fname):
        self._data_types = yaml.safe_load(
            open(self._store_path / fname)
        )

    @property
    def entity_rules(self):
        return self._entity_rules

    @entity_rules.setter
    def entity_rules(self, fname):
        # Valid tag classifications and their combo rules
        rules = yaml.safe_load(
            open(self._store_path / fname)
        )

        # track all combinations of NE types (cartesian prod)
        _map = {' '.join(i): '' for i in product(rules['ne_types'], repeat=2)}
        for typ in rules['ne_types']:
            _map[typ] = typ
        _map.update(rules['ne_map'])

        rules['ne_map'] = _map
        self._entity_rules = rules

    @property
    def entities(self):
        return self.entity_rules['ne_types']

    @property
    def entity_map(self):
        return self.entity_rules['ne_map']


    @property
    def db_schema(self):
        # schema for interacting with CypherQueries
        return self._db_schema

    @db_schema.setter
    def db_schema(self, fname):
        self._data_types = yaml.safe_load(
            open(self._store_path / fname)
        )

class _RCAesthetics(dict):
    def __enter__(self):
        # rc = mpl.rcParams
        rc = Settings
        self._orig = {k: rc[k] for k in self._keys}
        self._set(self)

    def __exit__(self, exc_type, exc_value, exc_tb):
        self._set(self._orig)

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with self:
                return func(*args, **kwargs)
        return wrapper


if __name__ == '__main__':
    cfg = Settings()
    print(cfg.entities)
