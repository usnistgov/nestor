from pathlib import Path
from itertools import product
import yaml

__author__ = "Thurston Sexton"
__all__ = [
    "nestor_params_from_files",
    "nestor_params",
    "NestorParams",
]


def nestor_fnames():
    """
    Get nestor's default config filepath

    Return default file being used by nestor ( in the future,
    could use environment variables, etc.), in order of priority

    Returns:
        pathlib.Path
    """
    default_cfg = Path(__file__).parent / "settings.yaml"

    return default_cfg


def nestor_params_from_files(fname):
    """
    Build up a `nestor.NestorParams` object from a passed config file locations
    
    Args:
        fname (pathlib.Path): location of a valid `.yaml` that defines a NestorParams object

    Returns:
        nestor.NestorParams: context-setting config object for other nestor behavior
    """

    settings_dict = yaml.safe_load(open(fname))
    cfg = NestorParams(**settings_dict)
    return cfg


def nestor_params():
    """Function to instantiate a :class:`nestor.NestorParams` instance from
    the default nestor config/type .yaml files

    For now, provides the default `settings.yaml`, based on maintenance work-orders.

    Returns:
        nestor.NestorParams: context-setting config object for other nestor behavior
    """
    fnames = nestor_fnames()
    # could check they exist, probably
    return nestor_params_from_files(fnames)


class NestorParams(dict):
    """Temporary subclass of `dict` to manage nestor contexts.

    > To be re-factored as typed dataclasses.  

    > TODO: allow context-based switching (a.k.a matplotlib xParams style)
    A valid nestor config `yaml` is formated with these feilds:

    ```yaml
    entities:
      types:
        atomic:
            code: description
            ...
        derived:
            ...
        hole:
            ...
      rules:
        code:
          - [codeA,codeB]
          ...
        ...

    datatypes:
        ...
    ```

    For the default `nestor.CFG`, we provide a schema based on nestor's roots
    in manufacturing maintenance:

    ```yaml
    entities:
      types:
        'atomic': # atomic types
          'P': 'Problem'
          'I': 'Item'
          'S': 'Solution'
        'derived':  # only made from atoms
          'PI': 'Object Fault'
          'SI': 'Object Resolution'
        'hole':
          'U': 'Unknown'
          'X': 'Non Entity'
          # 'NA': 'Not Annotated'

      rules:
        # two items makes one new item
        'I':
          - ['I','I']
        'PI':
          - ['P','I']
        'SI':
          - ['S','I']
        # redundancies
        'X':
          - ['P', 'P']
          - ['S', 'S']
          - ['P', 'S']
      # note: could try ordered as 'X':{1:'P',2:'S'}, etc.

    datatypes:
      issue:
        description:
          problem: 'Description of Problem'
          solution: 'Description of Solution'
          cause: 'Description of Cause'
          effect: 'Description of Observed Symptoms (Effects)'
        machine_down: 'Machine Up/Down'
        necessary_part: 'Necessary Part'
        part_in_process: 'Part in Process'
        cost: 'Maintenance Cost'
        id: 'MWO ID Number'
        date:
          machine_down: 'Machine Down Time-stamp'
          workorder_start: 'Work Order Start Time-stamp'
          maintenance_technician_arrive: 'Maintenance Technician Arrives Time-stamp'
          solution_found: 'Problem Found Time-stamp'
          part_ordered: 'Part(s) Ordered Time-stamp'
          part_received: 'Part(s) Received Time-stamp'
          solution_solve: 'Problem Solved Time-stamp'
          machine_up: 'Machine Up Time-stamp'
          workorder_completion: 'Work Order Completion Time-stamp'

      technician:
        name: 'Maintenance Technician'
        skills: 'Skill(s)'
        crafts: 'Craft(s)'

      operator:
        name: 'Operator'

      machine:
        name: 'Asset ID'
        manufacturer: 'Original Equipment Manufacturer'
        type: 'Machine Type'

      location:
        name: "Location"

    ```
    While future releases are focused on bringing more flexibility to users
    to define their own types, it is still possible to use these settings for a
    wide variety of tasks. 
    """

    def __init__(self, *arg, **kw):
        super(NestorParams, self).__init__(*arg, **kw)
        self._datatypes = None
        self._entities = None
        self._entity_rules = None
        self._atomics = None
        self._holes = None
        self._derived = None

    def datatype_search(self, property_name):
        """find any datatype that has a specific key
        """
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

    Parameters:
        data_dict (dict): potentially nested, keyed on strings
        pathstr (str):  dot-separated key path to traverse/retrieve

    Returns:
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

    Parameters:
        deep_dict (dict): Must have keys/values of type str
        value (str): value (or key) to search for
        join (str): connector between key names
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
    Parameters:
        deep_dict (dict): nested dictionary

    Returns:
        list: list of keys that map to leaves of a deeply nested dict

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
