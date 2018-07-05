"""
File: helper.py
Author: Sascha MOCCOZET
Organisation:
   Departament of Commerce USA
   National Institute of Standards and Technology - NIST
   Engineering Laboratory - EL
   Systems Integration Division - SID
   Information Modeling and Testing Group - IMTG
   <Insert Project Name>
Description:
   This file contains several static function generally use
   These function are not linked to a given object
"""

import yaml
import pandas as pd
from tqdm import tqdm
from datetime import datetime
import collections

# def openYAMLFile(yaml_path, dict=None):
#     """
#     open a Yaml file based on the given path
#     the there are no file, setup the yaml file based on the given dict
#     :return: a dictionary
#     """
#     try:
#         with open(yaml_path, 'r') as yamlfile:
#             config = yaml.load(yamlfile)
#             print("yaml file open")
#         return config
#     except FileNotFoundError:
#         with open(yaml_path, 'w') as yamlfile:
#             yaml.dump(dict, yamlfile)
#             print("yaml file created")
#         return dict

def openYAMLFile(yaml_path):
    """open a Yaml file based on the given path
    :return: a dictionary

    Parameters
    ----------
    yaml_path :
        

    Returns
    -------

    """
    with open(yaml_path, 'r') as yamlfile:
        config = yaml.load(yamlfile)
        print("yaml file open")
    return config


def isoStringToDate(date):
    """convert a ISO8601 String date format to a DateTime format

    Parameters
    ----------
    date :
        a ISO date in String format

    Returns
    -------
    type
        a DateTime date

    """
    try:
        return datetime(year=int(date[:4]), month=int(date[5:7]), day=int(date[8:10]), hour=int(date[11:13]), minute=int(date[14:16]))
    except AttributeError and ValueError:
        pass

    try:
        return datetime(year=int(date[:4]), month=int(date[5:7]), day=int(date[8:10]), hour=int(date[11:13]))
    except AttributeError and ValueError:
        pass

    try:
        return datetime(year=int(date[:4]), month=int(date[5:7]), day=int(date[8:10]))
    except AttributeError and ValueError:
        pass

    return None


def timeBetweenIsoStringDates(date1, date2):
    """return the time spen between date1 and date2

    Parameters
    ----------
    date1 :
        ISO string format of the early date
    date2 :
        ISO string format of the last date

    Returns
    -------
    type
        timedelta of the difference

    """
    if date1 is None or date1 is "" or date2 is None or date2 is "":
        return None
    if date1 > date2:
        return None
    return isoStringToDate(date2) - isoStringToDate(date1)

def updateDict(d, u):
    """recursivly merge 2 dictionary

    Parameters
    ----------
    d :
        param u:
    u :
        

    Returns
    -------

    """
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            d[k] = updateDict(d.get(k, {}), v)
        else:
            d[k] = v
    return d


def resultToObservationDataframe(result):
    """transforn a result into a observation dataframe
    :return: the observation dataframe

    Parameters
    ----------
    result :
        

    Returns
    -------

    """
    dataframe_observation= None
    if result:
        dataframe_observation = pd.DataFrame([r.values() for r in tqdm(result.records())], columns=result.keys())
        #TODO convert the date into ISO date
    else:
        print("The dataframe cannot be created")
    return dataframe_observation

