from DatabaseStorage.Program.Others.MyDate import *
from DatabaseStorage.Program.Database.Database_Properties import *
from tqdm import tqdm

import pandas as pd

"""
This files is used to store all function to create and execute a query for the given KPI
And return a DataFrame with the result
"""


def cypher_from_kpi(objects):
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


def pandas_from_cypher_kpi(database, query):
    results, done = database.runQuery(query)
    records = results.records()
    if done == 1:
        print("the query has been executed with succes")
    else:
        print("ERROR the query has not been exetuced !!!!! ")
    # dataframe = pd.DataFrame([r.values() for r in records], columns=results.keys())
    dataframe = pd.DataFrame([r.values() for r in tqdm(records, )], columns=results.keys())

    return dataframe
