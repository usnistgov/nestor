from pathlib import Path
import yaml

__all__ = [
    'nestor_params',
    'NestorParams',
]


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




# class NestorParams(MutableMapping, dict):
#
#     def __init__(self, *args, **kwargs):
#         self.update(*args, **kwargs)
#
#     def __setitem__(self, key, val):
#         try:
#             if key in _deprecated_map:
#                 pass
#             try:
#                 cval = self.validate[key](val)
#             except ValueError as ve:
#                 raise ValueError("Key %s: %s" % (key, str(ve)))
#             dict.__setitem__(self, key, cval)
#         except KeyError:
#             raise KeyError(
#                 '%s is not a valid rc parameter. See rcParams.keys() for a '
#                 'list of valid parameters.' % (key,))


def flatten_dict(d):
    new_dict = {}
    for key, value in d.items():
        if type(value) == dict:
            _dict = {'.'.join([key, _key]): _value for _key, _value in flatten_dict(value).items()}
            new_dict.update(_dict)
        else:
            new_dict[key] = value
    return new_dict


# def find_key_for(input_dict, value):
#     result = []
#     for k, v in input_dict.items():
#         if value in v:
#             result.append(k)
#     return result


class NestorParams(dict):

    # TODO rewrite using dataclasses and entity-rel model (v0.4)
    def __init__(self, *arg, **kw):
        super(NestorParams, self).__init__(*arg, **kw)

    @property
    def _datatypes(self):
        return flatten_dict(self['datatypes'])

    def datatype_search(self, property_name):
        return find_key_path(self['datatypes'], property_name)

    @property
    def _entities(self):
        return ''.join(self['entities']['types']['atomic'].keys())

    @property
    def _entity_rules(self):
        raw_rules = self['entities']['rules']
        rules = {k:[set(i) for i in v] for k,v in raw_rules.items()}
        return rules

    def apply_rules(self, pair):
        s = set(pair.split(' '))
        query = (ent for ent, rules in self._entity_rules.items() if s in rules)
        return next(query, '')  # if no match


# class EntityParams(NestorParams):
#
#     @property
#     def types(self):
#         return

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











# class Settings:
#     def __init__(self, db=False):
#         self._store_path = Path(__file__).parent/'store_data'
#         self.data_types = 'csvHeader.yaml'
#         self.entity_rules = 'entity_rules.yaml'
#
#         # default to unused/unread
#         self._db_schema = None
#         if db:
#             self.db_schema = 'DatabaseSchema.yaml'
#
#     @property
#     def data_types(self):
#         # pre-defined maintenance data types
#         return self._data_types
#
#     @data_types.setter
#     def data_types(self, fname):
#         self._data_types = yaml.safe_load(
#             open(self._store_path / fname)
#         )
#
#     @property
#     def entity_rules(self):
#         return self._entity_rules
#
#     @entity_rules.setter
#     def entity_rules(self, fname):
#         # Valid tag classifications and their combo rules
#         rules = yaml.safe_load(
#             open(self._store_path / fname)
#         )
#
#         # track all combinations of NE types (cartesian prod)
#         _map = {' '.join(i): '' for i in product(rules['ne_types'], repeat=2)}
#         for typ in rules['ne_types']:
#             _map[typ] = typ
#         _map.update(rules['ne_map'])
#
#         rules['ne_map'] = _map
#         self._entity_rules = rules
#
#     @property
#     def entities(self):
#         return self.entity_rules['ne_types']
#
#     @property
#     def entity_map(self):
#         return self.entity_rules['ne_map']
#
#
#     @property
#     def db_schema(self):
#         # schema for interacting with CypherQueries
#         return self._db_schema
#
#     @db_schema.setter
#     def db_schema(self, fname):
#         self._data_types = yaml.safe_load(
#             open(self._store_path / fname)
#         )
#
# class _RCAesthetics(dict):
#     def __enter__(self):
#         # rc = mpl.rcParams
#         rc = Settings
#         self._orig = {k: rc[k] for k in self._keys}
#         self._set(self)
#
#     def __exit__(self, exc_type, exc_value, exc_tb):
#         self._set(self._orig)
#
#     def __call__(self, func):
#         @functools.wraps(func)
#         def wrapper(*args, **kwargs):
#             with self:
#                 return func(*args, **kwargs)
#         return wrapper

