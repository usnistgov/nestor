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


def openYAMLFile(yaml_path):
    """
    open a Yaml file based on the given path
    :return: a dictionary
    """
    with open(yaml_path, 'r') as yamlfile:
        d = yaml.load(yamlfile)
        print("yaml file open")
    return d


def isoStringToDate(date):
    """
    convert a ISO8601 String date format to a DateTime format

    :param date: a ISO date in String format
    :return: a DateTime date
    """
    try:
        return datetime(year=int(date[:4]), month=int(date[5:7]), day=int(date[8:10]), hour=int(date[11:13]), minute=int(date[14:16]))
    except (AttributeError, ValueError):
        pass

    try:
        return datetime(year=int(date[:4]), month=int(date[5:7]), day=int(date[8:10]), hour=int(date[11:13]))
    except (AttributeError, ValueError):
        pass

    try:
        return datetime(year=int(date[:4]), month=int(date[5:7]), day=int(date[8:10]))
    except (AttributeError, ValueError):
        pass

    return None


def timeBetweenIsoStringDates(date1, date2):
    """
    return the time spen between date1 and date2

    :param date1: ISO string format of the early date
    :param date2: ISO string format of the last date
    :return: timedelta of the difference
    """
    if date1 is None or date1 is "" or date2 is None or date2 is "":
        return None
    if date1 > date2:
        return None
    return isoStringToDate(date2) - isoStringToDate(date1)

def updateDict(d, u):
    """
    recursivly merge 2 dictionary
    :param d:
    :param u:
    :return:
    """
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            d[k] = updateDict(d.get(k, {}), v)
        else:
            d[k] = v
    return d


def resultToObservationDataframe(result):
    """
    transforn a result into a observation dataframe
    :return: the observation dataframe
    """
    dataframe_observation= None
    if result:
        dataframe_observation = pd.DataFrame([r.values() for r in tqdm(result.records())], columns=result.keys())
        #TODO convert the date into ISO date
    else:
        print("The dataframe cannot be created")
    return dataframe_observation


def standardizeString(string):
    """
    clean the string for all the string input into the database
    "\" create problem because Cypher check for the value after as a special char, it has to be change into "\\"
    "'" create a problem because it is the char to end a sting has to change to "\'"
    :param string: non clean string
    :return: a clean string
    """
    return string.replace('\\','\\\\').replace("'","\\'").lstrip()


def getListCollumnDataframe(dataframe, rownumber, classification):
    """
    for a given dataframe , a row number and a classification,
    Return a Serie of the 1 value
    """
    serie = dataframe[classification].iloc[rownumber]
    return serie[serie > 0].index.values


def getListIndexDataframe(dataframe, keyword, classification):
    serie = dataframe[classification][keyword]

    return serie[serie > 0].axes[0].tolist()

