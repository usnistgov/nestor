from datetime import *

"""
This files store all interaction with the date of the KPI.

It is used to extract the date from the CSV to store it in a standards format

as well as transform the extracted date from the database (Neo4j does not allow date format)
"""


def isoStringToDate(date):
    """
    convert a ISO8601 String date format to a DateTime format

    :param date: a ISO date in String format
    :return: a DateTime date
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
    """
    return the time spen between date1 and date2

    :param date1: ISO string format of the early date
    :param date2: ISO string format of the last date
    :return: timedelta of the difference
    """
    if date1 is None or date1 is "" or date2 is None or date2 is "":
        return None
    if date1> date2:
        return None
    return isoStringToDate(date2) - isoStringToDate(date1)



def clean_GS_date(date, time="0000"):
    """
    clean the date from GS data

    :param date: the date
    :param time: the time
    :return: a DateTime
    """

####    DATE ####
    if date is "":
        return None

    date = date.replace(" ","").split("/")

    date[2] = "20" + date[2]

    if len(date[0]) is 1:
        date[0] = "0" + date[0]
    else:
        date[0] = date[0]

    if len(date[1]) is 1:
        date[1] = "0" + date[1]
    else:
        date[1] = date[1]

#### TIME ####
    while len(time) < 4:
        time = "0" + time.replace(" ", "")

    return datetime(year=int(date[2]), month=int(date[0]), day=int(date[1]), hour=int(time[:2]), minute=int(time[2:]))




