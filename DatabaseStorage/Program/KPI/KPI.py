from DatabaseStorage.Program.Others.MyDate import *
from DatabaseStorage.Program.Database.Database_Properties import *
from DatabaseStorage.Program.Database.Database_Properties import NodeIssue

from tqdm import tqdm

import pandas as pd

"""
This files is used to store all function to create and execute a query for the given KPI
And return a DataFrame with the result
"""


def cypher_from_kpi(objects):
    """
    create a Cypher query from a list of objects
    :param objects:
    :return:
    """
    match = ""
    where = []
    res = []
    for obj in objects:
        m, w, r = obj.cypher_kpi()
        match += m + "\n"
        if w:
            where.append(w)
        [res.append(x) for x in r]
    if where:
        query = match + "\nWHERE " + " AND ".join(where) + "\nRETURN " + ", ".join(res) + ", count(issue) AS issue_count"
    else:
        query = match + "\nRETURN " + ", ".join(res) + ", count( DISTINCT issue) AS issue_count"


    if len(res) !=0:
        res.append("issue_count")

    return query, res


def pandas_from_cypher_kpi(database, query, results=None):
    """
    Used the Cypher query to speak to the database and return the result into a pandas dataframe
    :param database:
    :param query:
    :param results:
    :return:
    """

    res, done = database.runQuery(query)
    records = res.records()
    if done == 1:
        print("the query has been executed with succes")
    else:
        print("ERROR the query has not been exetuced !!!!! ")
    # dataframe = pd.DataFrame([r.values() for r in records], columns=res.keys())
    dataframe = pd.DataFrame([r.values() for r in tqdm(records)], columns=res.keys())
    dataframe = dataframe_to_converte_date(dataframe)
    dataframe, results = dataframe_to_create_time(dataframe, results)

    return dataframe, results


def dataframe_to_converte_date(dataframe):
    """
    transform date in a pandas dataframe (the result of the query) from String ISO8601 to pandas.DateTime value
    :param dataframe:
    :return:
    """
    if f'issue.{NodeIssue.PROPERTY_DATE_MAINTENANCE_WORK_ORDER_CLOSE.value}' in dataframe.keys():
        dataframe[f'issue.{NodeIssue.PROPERTY_DATE_MAINTENANCE_WORK_ORDER_CLOSE.value}'] = pd.to_datetime(dataframe[f'issue.{NodeIssue.PROPERTY_DATE_MAINTENANCE_WORK_ORDER_CLOSE.value}'])
    if f'issue.{NodeIssue.PROPERTY_DATE_MAINTENANCE_WORK_ORDER_ISSUE.value}' in dataframe.keys():
        dataframe[f'issue.{NodeIssue.PROPERTY_DATE_MAINTENANCE_WORK_ORDER_ISSUE.value}'] = pd.to_datetime(dataframe[f'issue.{NodeIssue.PROPERTY_DATE_MAINTENANCE_WORK_ORDER_ISSUE.value}'])
    if f'issue.{NodeIssue.PROPERTY_DATE_MACHINE_DOWN.value}' in dataframe.keys():
        dataframe[f'issue.{NodeIssue.PROPERTY_DATE_MACHINE_DOWN.value}'] = pd.to_datetime(dataframe[f'issue.{NodeIssue.PROPERTY_DATE_MACHINE_DOWN.value}'])
    if f'issue.{NodeIssue.PROPERTY_DATE_MACHINE_UP.value}' in dataframe.keys():
        dataframe[f'issue.{NodeIssue.PROPERTY_DATE_MACHINE_UP.value}'] = pd.to_datetime(dataframe[f'issue.{NodeIssue.PROPERTY_DATE_MACHINE_UP.value}'])
    if f'issue.{NodeIssue.PROPERTY_DATE_TECHNICIAN_ARRIVE.value}' in dataframe.keys():
        dataframe[f'issue.{NodeIssue.PROPERTY_DATE_TECHNICIAN_ARRIVE.value}'] = pd.to_datetime(dataframe[f'issue.{NodeIssue.PROPERTY_DATE_TECHNICIAN_ARRIVE.value}'])
    if f'issue.{NodeIssue.PROPERTY_DATE_PROBLEM_FOUND.value}' in dataframe.keys():
        dataframe[f'issue.{NodeIssue.PROPERTY_DATE_PROBLEM_FOUND.value}'] = pd.to_datetime(dataframe[f'issue.{NodeIssue.PROPERTY_DATE_PROBLEM_FOUND.value}'])
    if f'issue.{NodeIssue.PROPERTY_DATE_PROBLEM_SOLVE.value}' in dataframe.keys():
        dataframe[f'issue.{NodeIssue.PROPERTY_DATE_PROBLEM_SOLVE.value}'] = pd.to_datetime(dataframe[f'issue.{NodeIssue.PROPERTY_DATE_PROBLEM_SOLVE.value}'])
    if f'issue.{NodeIssue.PROPERTY_DATE_PART_ORDER.value}' in dataframe.keys():
        dataframe[f'issue.{NodeIssue.PROPERTY_DATE_PART_ORDER.value}'] = pd.to_datetime(dataframe[f'issue.{NodeIssue.PROPERTY_DATE_PART_ORDER.value}'])
    if f'issue.{NodeIssue.PROPERTY_DATE_MAINTENANCE_TECHNICIAN_REPAIR_PROBLEM.value}' in dataframe.keys():
        dataframe[f'issue.{NodeIssue.PROPERTY_DATE_MAINTENANCE_TECHNICIAN_REPAIR_PROBLEM.value}'] = pd.to_datetime(dataframe[f'issue.{NodeIssue.PROPERTY_DATE_MAINTENANCE_TECHNICIAN_REPAIR_PROBLEM.value}'])

    return dataframe

def dataframe_to_create_time(dataframe, results):
    """
    Used to create the time from Mike's paper (time to dispatch, time to repair ...) as well as the average for each resords
    if the user query date information
    the value is retrived as Nanoseconds but change into minutes (define by the variable divided_by) as an integer
    :param dataframe:
    :param results:
    :return:
    """
    divided_by = 1000000000/60/60

    if f'issue.{NodeIssue.PROPERTY_DATE_MACHINE_UP.value}' in results and f'issue.{NodeIssue.PROPERTY_DATE_MACHINE_DOWN.value}' in results:
        dataframe[f'issue.{NodeIssue.PROPERTY_TIME_REPAIR.value}'] = dataframe[f'issue.{NodeIssue.PROPERTY_DATE_MACHINE_UP.value}'] - dataframe[f'issue.{NodeIssue.PROPERTY_DATE_MACHINE_DOWN.value}']
        dataframe[f'issue.{NodeIssue.PROPERTY_TIME_REPAIR.value}'] = pd.to_numeric(dataframe[f'issue.{NodeIssue.PROPERTY_TIME_REPAIR.value}'])/divided_by

        dataframe[f'issue.{NodeIssue.PROPERTY_AVG_REPAIR.value}'] = dataframe[f'issue.{NodeIssue.PROPERTY_TIME_REPAIR.value}'] / dataframe[f'issue_count']

        results.append(f'issue.{NodeIssue.PROPERTY_TIME_REPAIR.value}')
        results.append(f'issue.{NodeIssue.PROPERTY_AVG_REPAIR.value}')

    if f'issue.{NodeIssue.PROPERTY_DATE_MAINTENANCE_WORK_ORDER_CLOSE.value}' in results and f'issue.{NodeIssue.PROPERTY_DATE_MAINTENANCE_WORK_ORDER_ISSUE.value}' in results:
        dataframe[f'issue.{NodeIssue.PROPERTY_TIME_WORK_ORDER_COMPLETION.value}'] = dataframe[f'issue.{NodeIssue.PROPERTY_DATE_MAINTENANCE_WORK_ORDER_CLOSE.value}'] - dataframe[f'issue.{NodeIssue.PROPERTY_DATE_MAINTENANCE_WORK_ORDER_ISSUE.value}']
        dataframe[f'issue.{NodeIssue.PROPERTY_TIME_WORK_ORDER_COMPLETION.value}'] = pd.to_numeric(dataframe[f'issue.{NodeIssue.PROPERTY_TIME_WORK_ORDER_COMPLETION.value}'])/divided_by

        dataframe[f'issue.{NodeIssue.PROPERTY_AVG_WORK_ORDER_COMPLETION.value}'] = dataframe[f'issue.{NodeIssue.PROPERTY_TIME_WORK_ORDER_COMPLETION.value}']/ dataframe[f'issue_count']

        results.append(f'issue.{NodeIssue.PROPERTY_TIME_WORK_ORDER_COMPLETION.value}')
        results.append(f'issue.{NodeIssue.PROPERTY_AVG_WORK_ORDER_COMPLETION.value}')

    if f'issue.{NodeIssue.PROPERTY_DATE_TECHNICIAN_ARRIVE.value}' in results and f'issue.{NodeIssue.PROPERTY_DATE_MACHINE_DOWN.value}' in results:
        dataframe[f'issue.{NodeIssue.PROPERTY_TIME_DISPATCH.value}'] = dataframe[f'issue.{NodeIssue.PROPERTY_DATE_TECHNICIAN_ARRIVE.value}'] - dataframe[f'issue.{NodeIssue.PROPERTY_DATE_MACHINE_DOWN.value}']
        dataframe[f'issue.{NodeIssue.PROPERTY_TIME_DISPATCH.value}'] = pd.to_numeric(dataframe[f'issue.{NodeIssue.PROPERTY_TIME_DISPATCH.value}'])/divided_by

        dataframe[f'issue.{NodeIssue.PROPERTY_AVG_DISPATCH.value}'] = dataframe[f'issue.{NodeIssue.PROPERTY_TIME_DISPATCH.value}'] / dataframe[f'issue_count']

        results.append(f'issue.{NodeIssue.PROPERTY_TIME_DISPATCH.value}')
        results.append(f'issue.{NodeIssue.PROPERTY_AVG_DISPATCH.value}')

    if f'issue.{NodeIssue.PROPERTY_DATE_MACHINE_UP.value}' in results and f'issue.{NodeIssue.PROPERTY_DATE_TECHNICIAN_ARRIVE.value}' in results:
        dataframe[f'issue.{NodeIssue.PROPERTY_TIME_RETURN_OPERATION.value}'] = dataframe[f'issue.{NodeIssue.PROPERTY_DATE_MACHINE_UP.value}'] - dataframe[f'issue.{NodeIssue.PROPERTY_DATE_TECHNICIAN_ARRIVE.value}']
        dataframe[f'issue.{NodeIssue.PROPERTY_TIME_RETURN_OPERATION.value}'] = pd.to_numeric(dataframe[f'issue.{NodeIssue.PROPERTY_TIME_RETURN_OPERATION.value}'])/divided_by

        dataframe[f'issue.{NodeIssue.PROPERTY_AVG_RETURN_OPERATION.value}']= dataframe[f'issue.{NodeIssue.PROPERTY_TIME_RETURN_OPERATION.value}'] / dataframe[f'issue_count']

        results.append(f'issue.{NodeIssue.PROPERTY_TIME_RETURN_OPERATION.value}')
        results.append(f'issue.{NodeIssue.PROPERTY_AVG_RETURN_OPERATION.value}')

    if f'issue.{NodeIssue.PROPERTY_DATE_MAINTENANCE_WORK_ORDER_ISSUE.value}' in results and f'issue.{NodeIssue.PROPERTY_DATE_MACHINE_DOWN.value}' in results:
        dataframe[f'issue.{NodeIssue.PROPERTY_TIME_ISSUE_WORK_ORDER.value}'] = dataframe[f'issue.{NodeIssue.PROPERTY_DATE_MAINTENANCE_WORK_ORDER_ISSUE.value}'] - dataframe[f'issue.{NodeIssue.PROPERTY_DATE_MACHINE_DOWN.value}']
        dataframe[f'issue.{NodeIssue.PROPERTY_TIME_ISSUE_WORK_ORDER.value}'] = pd.to_numeric(dataframe[f'issue.{NodeIssue.PROPERTY_TIME_ISSUE_WORK_ORDER.value}'])/divided_by

        dataframe[f'issue.{NodeIssue.PROPERTY_AVG_ISSUE_WORK_ORDER.value}'] = dataframe[f'issue.{NodeIssue.PROPERTY_TIME_ISSUE_WORK_ORDER.value}'] / dataframe[f'issue_count']

        results.append(f'issue.{NodeIssue.PROPERTY_TIME_ISSUE_WORK_ORDER.value}')
        results.append(f'issue.{NodeIssue.PROPERTY_AVG_ISSUE_WORK_ORDER.value}')

    if f'issue.{NodeIssue.PROPERTY_DATE_TECHNICIAN_ARRIVE.value}' in results and f'issue.{NodeIssue.PROPERTY_DATE_MAINTENANCE_WORK_ORDER_ISSUE.value}' in results:
        dataframe[f'issue.{NodeIssue.PROPERTY_TIME_TRAVEL.value}'] = dataframe[f'issue.{NodeIssue.PROPERTY_DATE_TECHNICIAN_ARRIVE.value}'] - dataframe[f'issue.{NodeIssue.PROPERTY_DATE_MAINTENANCE_WORK_ORDER_ISSUE.value}']
        dataframe[f'issue.{NodeIssue.PROPERTY_TIME_TRAVEL.value}'] = pd.to_numeric(dataframe[f'issue.{NodeIssue.PROPERTY_TIME_TRAVEL.value}'])/divided_by

        dataframe[f'issue.{NodeIssue.PROPERTY_AVG_TRAVEL.value}']= dataframe[f'issue.{NodeIssue.PROPERTY_TIME_TRAVEL.value}'] / dataframe[f'issue_count']

        results.append(f'issue.{NodeIssue.PROPERTY_TIME_TRAVEL.value}')
        results.append(f'issue.{NodeIssue.PROPERTY_AVG_TRAVEL.value}')

    if f'issue.{NodeIssue.PROPERTY_DATE_PROBLEM_SOLVE.value}' in results and f'issue.{NodeIssue.PROPERTY_DATE_TECHNICIAN_ARRIVE.value}' in results:
        dataframe[f'issue.{NodeIssue.PROPERTY_TIME_SOLVE_PROBLEM.value}'] = dataframe[f'issue.{NodeIssue.PROPERTY_DATE_PROBLEM_SOLVE.value}'] - dataframe[f'issue.{NodeIssue.PROPERTY_DATE_TECHNICIAN_ARRIVE.value}']
        dataframe[f'issue.{NodeIssue.PROPERTY_TIME_SOLVE_PROBLEM.value}'] = pd.to_numeric(dataframe[f'issue.{NodeIssue.PROPERTY_TIME_SOLVE_PROBLEM.value}'])/divided_by

        dataframe[f'issue.{NodeIssue.PROPERTY_AVG_SOLVE_PROBLEM.value}'] = dataframe[f'issue.{NodeIssue.PROPERTY_TIME_SOLVE_PROBLEM.value}'] / dataframe[f'issue_count']

        results.append(f'issue.{NodeIssue.PROPERTY_TIME_SOLVE_PROBLEM.value}')
        results.append(f'issue.{NodeIssue.PROPERTY_AVG_SOLVE_PROBLEM.value}')

    if f'issue.{NodeIssue.PROPERTY_DATE_PROBLEM_FOUND.value}' in results and f'issue.{NodeIssue.PROPERTY_DATE_TECHNICIAN_ARRIVE.value}' in results:
        dataframe[f'issue.{NodeIssue.PROPERTY_TIME_DIAGNOSE.value}'] = dataframe[f'issue.{NodeIssue.PROPERTY_DATE_PROBLEM_FOUND.value}'] - dataframe[f'issue.{NodeIssue.PROPERTY_DATE_TECHNICIAN_ARRIVE.value}']
        dataframe[f'issue.{NodeIssue.PROPERTY_TIME_DIAGNOSE.value}'] = pd.to_numeric(dataframe[f'issue.{NodeIssue.PROPERTY_TIME_DIAGNOSE.value}'])/divided_by

        dataframe[f'issue.{NodeIssue.PROPERTY_AVG_DIAGNOSE.value}'] = dataframe[f'issue.{NodeIssue.PROPERTY_TIME_DIAGNOSE.value}']/ dataframe[f'issue_count']

        results.append(f'issue.{NodeIssue.PROPERTY_TIME_DIAGNOSE.value}')
        results.append(f'issue.{NodeIssue.PROPERTY_AVG_DIAGNOSE.value}')

    if f'issue.{NodeIssue.PROPERTY_DATE_PART_ORDER.value}' in results and f'issue.{NodeIssue.PROPERTY_DATE_PROBLEM_FOUND.value}' in results:
        dataframe[f'issue.{NodeIssue.PROPERTY_TIME_ORDER.value}'] = dataframe[f'issue.{NodeIssue.PROPERTY_DATE_PART_ORDER.value}'] - dataframe[f'issue.{NodeIssue.PROPERTY_DATE_PROBLEM_FOUND.value}']
        dataframe[f'issue.{NodeIssue.PROPERTY_TIME_ORDER.value}'] = pd.to_numeric(dataframe[f'issue.{NodeIssue.PROPERTY_TIME_ORDER.value}'])/divided_by

        dataframe[f'issue.{NodeIssue.PROPERTY_AVG_ORDER.value}'] = dataframe[f'issue.{NodeIssue.PROPERTY_TIME_ORDER.value}'] / dataframe[f'issue_count']

        results.append(f'issue.{NodeIssue.PROPERTY_TIME_ORDER.value}')
        results.append(f'issue.{NodeIssue.PROPERTY_AVG_ORDER.value}')

    if f'issue.{NodeIssue.PROPERTY_DATE_MAINTENANCE_TECHNICIAN_REPAIR_PROBLEM.value}' in results and f'issue.{NodeIssue.PROPERTY_DATE_PART_ORDER.value}' in results:
        dataframe[f'issue.{NodeIssue.PROPERTY_TIME_LEAD_PART.value}'] = dataframe[f'issue.{NodeIssue.PROPERTY_DATE_MAINTENANCE_TECHNICIAN_REPAIR_PROBLEM.value}'] - dataframe[f'issue.{NodeIssue.PROPERTY_DATE_PART_ORDER.value}']
        dataframe[f'issue.{NodeIssue.PROPERTY_TIME_LEAD_PART.value}'] = pd.to_numeric(dataframe[f'issue.{NodeIssue.PROPERTY_TIME_LEAD_PART.value}'])/divided_by

        dataframe[f'issue.{NodeIssue.PROPERTY_AVG_LEAD_PART.value}'] = dataframe[f'issue.{NodeIssue.PROPERTY_TIME_LEAD_PART.value}'] / dataframe[f'issue_count']

        results.append(f'issue.{NodeIssue.PROPERTY_TIME_LEAD_PART.value}')
        results.append(f'issue.{NodeIssue.PROPERTY_AVG_LEAD_PART.value}')

    if f'issue.{NodeIssue.PROPERTY_DATE_PROBLEM_SOLVE.value}' in results and f'issue.{NodeIssue.PROPERTY_DATE_MAINTENANCE_TECHNICIAN_REPAIR_PROBLEM.value}' in results:
        dataframe[f'issue.{NodeIssue.PROPERTY_TIME_FIX.value}'] = dataframe[f'issue.{NodeIssue.PROPERTY_DATE_PROBLEM_SOLVE.value}'] - dataframe[f'issue.{NodeIssue.PROPERTY_DATE_MAINTENANCE_TECHNICIAN_REPAIR_PROBLEM.value}']
        dataframe[f'issue.{NodeIssue.PROPERTY_TIME_FIX.value}'] = pd.to_numeric(dataframe[f'issue.{NodeIssue.PROPERTY_TIME_FIX.value}'])/divided_by

        dataframe[f'issue.{NodeIssue.PROPERTY_AVG_FIX.value}'] = dataframe[f'issue.{NodeIssue.PROPERTY_TIME_FIX.value}'] / dataframe[f'issue_count']

        results.append(f'issue.{NodeIssue.PROPERTY_TIME_FIX.value}')
        results.append(f'issue.{NodeIssue.PROPERTY_AVG_FIX.value}')

    if f'issue.{NodeIssue.PROPERTY_DATE_MACHINE_UP.value}' in results and f'issue.{NodeIssue.PROPERTY_DATE_PROBLEM_SOLVE.value}' in results:
        dataframe[f'issue.{NodeIssue.PROPERTY_TIME_TURN_ON.value}'] = dataframe[f'issue.{NodeIssue.PROPERTY_DATE_MACHINE_UP.value}'] - dataframe[f'issue.{NodeIssue.PROPERTY_DATE_PROBLEM_SOLVE.value}']
        dataframe[f'issue.{NodeIssue.PROPERTY_TIME_TURN_ON.value}'] = pd.to_numeric(dataframe[f'issue.{NodeIssue.PROPERTY_TIME_TURN_ON.value}'])/divided_by

        dataframe[f'issue.{NodeIssue.PROPERTY_AVG_TURN_ON.value}'] = dataframe[f'issue.{NodeIssue.PROPERTY_TIME_REPAIR.value}'] / dataframe[f'issue_count']

        results.append(f'issue.{NodeIssue.PROPERTY_TIME_TURN_ON.value}')
        results.append(f'issue.{NodeIssue.PROPERTY_AVG_TURN_ON.value}')

    return dataframe, results