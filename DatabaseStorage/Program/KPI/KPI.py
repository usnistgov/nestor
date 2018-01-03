from datetime import *
from Program.Others.MyDate import timeBetweenIsoStringDates


import pandas as pd

"""
This files is used to store all function to create and execute a query for the given KPI
And return a DataFrame with the result
"""


"""
def Test(database, technician_name=None, machine_name=None):

    query = 'MATCH (technician:TECHNICIAN'

    if technician_name is not None:
        query += ' {name: "%s"}' % (technician_name)
    query += ')<-[:SOLVE_BY]-(issue:ISSUE)-[:COVERED]->(mach:MACHINE'

    if machine_name is not None:
        query += ' {name: "%s"}' % (machine_name)

    query += ')\nRETURN technician, mach, count(issue) AS count'
    results = database.runQuery(query)
    for result in results:
        technician = Human(None)
        technician.fromCypher(result=result["technician"])

        issue = Issue(None,None)

"""
def Test(database, var1= "technician", var2= "solution", var3="count"):

    query = 'MATCH (tech:TECHNICIAN)<-[:SOLVE_BY]-(issue:ISSUE)' \
            '\nRETURN tech.name AS %s, issue.description_of_solution AS %s, count(issue.description_of_solution) AS %s' % (
            var1, var2, var3)
    results = database.runQuery(query)
    dataframe = pd.DataFrame({var3:[],var2:[],var1:[]})
    for result in results:
        dataframe = dataframe.append({var1:result[var1], var2:result[var2], var3:result[var3]}, ignore_index=True)
    return dataframe



def MaintenanceTechnician_Problem(database, var1= "technician", var2= "problem", var3="count"):

    query = 'MATCH (tech:TECHNICIAN)<-[:SOLVE_BY]-(issue:ISSUE)' \
            '\nRETURN tech.name AS %s, issue.description_of_problem AS %s, count(issue.description_of_problem) AS %s'%(var1,var2,var3)
    results = database.runQuery(query)
    dataframe = pd.DataFrame({var3:[],var2:[],var1:[]})
    for result in results:
        dataframe = dataframe.append({var1:result[var1], var2:result[var2], var3:result[var3]}, ignore_index=True)
    return dataframe

def MaintenanceTechnician_Solution(database, var1= "technician", var2= "solution", var3= "count"):

    query = 'MATCH (tech:TECHNICIAN)<-[:SOLVE_BY]-(issue:ISSUE)' \
            '\nRETURN tech.name AS %s, issue.description_of_solution AS %s, count(issue.description_of_solution) AS %s' % (
                var1, var2, var3)
    results = database.runQuery(query)
    dataframe = pd.DataFrame({var3: [], var2: [], var1: []})
    for result in results:
        dataframe = dataframe.append({var1: result[var1], var2: result[var2], var3: result[var3]}, ignore_index=True)
    return dataframe

def Skill_Description(database, skill=None):
    pass

def Craft_Description(database, craft=None):
    pass

def Skill_Solution(database, skill=None):
    pass

def Craft_Solution(database, craft=None):
    pass

def MaintenanceTechnician_Machine(database, var1= "technician", var2= "machine", var3="count"):

    query = 'MATCH (tech:TECHNICIAN)<-[:SOLVE_BY]-(issue:ISSUE)-[:COVERED]->(mach:MACHINE)' \
            '\nRETURN tech.name AS %s, mach.name AS %s, count(issue.description_of_problem) AS %s'%(var1,var2,var3)
    results = database.runQuery(query)
    dataframe = pd.DataFrame({var3:[],var2:[],var1:[]})
    for result in results:
        dataframe = dataframe.append({var1:result[var1], var2:result[var2], var3:result[var3]}, ignore_index=True)
    return dataframe

def MaintenanceTechnician_MachineType(database , var1= "technician", var2= "machine_type", var3="count"):

    query = 'MATCH (tech:TECHNICIAN)<-[:SOLVE_BY]-(issue:ISSUE)-[:COVERED]->(:MACHINE)-[:IS_A]->(type:MACHINE_TYPE)' \
            '\nRETURN tech.name AS %s, type.type AS %s, count(issue) AS %s' % (var1, var2, var3)
    results = database.runQuery(query)
    dataframe = pd.DataFrame({var3: [], var2: [], var1: []})
    for result in results:
        dataframe = dataframe.append({var1: result[var1], var2: result[var2], var3: result[var3]}, ignore_index=True)
    return dataframe

def MaintenanceTechnician_Machine_WorkOrderCompletionTime(database, var1= "technician", var2= "machine", var3="completion_time" ):
    query = 'MATCH (tech:TECHNICIAN)<-[:SOLVE_BY]-(issue:ISSUE)-[:COVERED]->(mach:MACHINE)' \
            '\nRETURN tech.name AS %s, mach.name AS %s , issue.date_maintenance_work_order_issue AS %s, issue.date_maintenance_work_order_close AS %s' % (
                var1, var2, 'issue', 'close')
    results = database.runQuery(query)
    dataframe = pd.DataFrame({var3: [], var2: [], var1: []})
    for result in results:
        time = timeBetweenIsoStringDates(result['issue'],result['close'])
        if time is not None:
            time = time.total_seconds()/60/60
        dataframe = dataframe.append({var1: result[var1], var2: result[var2], var3: time}, ignore_index=True)
    return dataframe


def MaintenanceTechnician_MachineType_WorkOrderCompletionTime(database, technician_name=None, machine_type=None):
    pass

def MaintenanceTechnician_Item(database, technician_name=None, item=None):
    pass

def MaintenanceTechnician_ProblemAction(database, technician_name=None, problem_action=None):
    pass

def MaintenanceTechnician_SolutionAction(database, technician_name=None, solution_action=None):
    pass

def Skill_Item(database, skill=None, item=None):
    pass

def Craft_Item(database, craft=None, item=None):
    pass

def Skill_ProblemAction(database, skill=None, problem_action=None):
    pass

def Crafts_ProblemAction(database, craft=None, problem_action=None):
    pass

def MaintenanceTechnician_Item_WorkOrderCompletionTime(database, technician_name=None, item=None):
    pass

def MaintenanceTechnician_ProblemAction_WorkOrderCompletionTime(database, technician_name=None, problem_action=None):
    pass

def MaintenanceTechnician_SolutionAction_WorkOrderCompletionTime(database, technician_name=None, solution_action=None):
    pass

def Machine_TimeBetweenWorkOrder(database, machine_name=None):
    pass

def MachineType_TimeBetweenWorkOrder(database, machine_type=None):
    pass

def Machine_WorkOrderCompletionTime(database, machine_name=None):
    pass

def MachineType_WorkOrderCompletionTime(database, machine_type=None):
    pass

def Machine_TimeBetweenWorkOrder_Item(database, machine_name=None):
    pass

def Machine_TimeBetweenWorkOrder_ProblemAction(database, machine_name=None, problem_action=None):
    pass

def Machine_TimeBetweenWorkOrder_SolutionAction(database, machine_name=None, solution_action=None):
    pass

def Machine_WorkOrderCompletionTime_Item(database, machine_name=None, item=None):
    pass

def Machine_WorkOrderCompletionTime_ProblemAction(database, machine_name=None, problem_action=None):
    pass

def Machine_WorkOrderCompletionTime_SolutionAction(database, machine_name=None, solution_action=None):
    pass

def MachineType_TimeBetweenWorkOrder_Item(database, machine_type=None, item=None):
    pass

def MachineType_TimeBetweenWorkOrder_ProblemAction(database, machine_type=None, problem_action=None):
    pass

def MachineType_TimeBetweenWorkOrder_SolutionAction(database, machine_type=None, solution_action=None):
    pass

def MachineType_WorkOrderCompletionTime_Item(database, machine_type=None, item=None):
    pass

def MachineType_WorkOrderCompletionTime_ProblemAction(database, machine_type=None, problem_action=None):
    pass

def MachineType_WorkOrderCompletionTime_SolutionAction(database, machine_type=None, solution_action=None):
    pass

def Operator_ProblemAction(database, operator_name=None, problem_action=None):
    pass

def Operator_ProblemItem(database, operator_name=None, item=None):
    pass

def Operator_ProblemItem_WorkOrderCompletionTime(database, operator_name=None, item=None):
    pass

def Item_TimeBetweenWorkOrder(database, item=None):
    pass

def Item_WorkOrderCompletionTime(database, item=None):
    pass

def ProblemAction_TimeBetweenWorkOrder(database, problem_action_None):
    pass

def ProblemAction_WorkOrderCompletionTime(database, problem_action_None):
    pass

def SolutionAction_WorkOrderCompletionTime(database, solution_action=None):
    pass

def SolutionAction_TimeBetweenWorkOrder(database, solution_action=None):
    pass

def DateMonth_Machine(database, var1= "date", var2= "machine"):

    query = 'MATCH (issue:ISSUE)-[:COVERED]->(mach:MACHINE) ' \
            'WHERE exists(issue.date_maintenance_work_order_issue)' \
            '\nRETURN issue.date_maintenance_work_order_issue AS %s, mach.name AS %s' % (var1, var2)

    results = database.runQuery(query)
    dataframe = pd.DataFrame({var2: [], var1: []})
    for result in results:
        #date = isoStringToDate(result[var1])
        date = datetime(year=int(result[var1][:4]), month=int(result[var1][5:7]), day=1)
        dataframe = dataframe.append({var1: date, var2: result[var2]}, ignore_index=True)
    return dataframe