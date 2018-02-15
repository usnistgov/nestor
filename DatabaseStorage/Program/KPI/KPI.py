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
        query = match + "\nWHERE " + " AND ".join(where) + "\nRETURN " + ", ".join(res)
    else:
        query = match + "\nRETURN " + ", ".join(res)

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


    # def abstract_kpi_time_mwo(database, x_value, filter_value, time_value="time", count_value="count", average_value="average"):
    #     """
    #         This function create an dataframe used to print a barplot based on two element
    #         the dataframe is represented with 5 collumn (filter_value, x_value, time_value, count_value, average_value)
    #
    #         :param database:        the Neo4j database you are working on
    #         :param filter_value:    one of the value you want to be in the dataframe
    #         :param x_value:         the data represented on the x axis
    #         :param time_value:      the total time spend
    #         :param count_value:     the number of issue solved
    #         :param average_value:   the avereag of time spend per issue
    #         :return:    dataframe contains all this information
    #         """
    #     # TODO you can use MATCH (n) RETURN distinct labels(n) to find all label in the database,
    #     # or MATCH (n)
    #     # WITH DISTINCT labels(n) AS labels
    #     # UNWIND labels AS label
    #     # RETURN DISTINCT label
    #     # ORDER BY label
    #
    #     query = "MATCH (issue %s)-[%s]->(machine %s)" % \
    #             (NodeIssue.LABEL_ISSUE.value, LabelEdges.LABEL_COVERED.value, NodeMachine.LABEL_MACHINE.value)
    #     # query += "\nMATCH (machine)-[%s]->(machine_type %s)" % \
    #     #          (LabelEdges.LABEL_ISA.value, NodeMachine.LABEL_MACHINE_TYPE.value)
    #     query += "\nMATCH (issue)-[%s]->(item %s)" % \
    #             (LabelEdges.LABEL_CONTAINS.value, NodeTag.LABEL_ITEM.value)
    #     query += "\nMATCH (issue)-[%s]->(solution_action %s)" % \
    #             ( LabelEdges.LABEL_SOLUTION.value, NodeTag.LABEL_ACTION.value)
    #     query += "\nMATCH (issue)-[%s]->(problem_action %s)" % \
    #             (LabelEdges.LABEL_PROBLEM.value, NodeTag.LABEL_ACTION.value)
    #     query += "\nMATCH (issue)-[%s]->(technician %s)" % \
    #             (LabelEdges.LABEL_SOLVE.value, NodeHuman.LABEL_TECHNICIAN.value)
    #     query += "\nMATCH (issue)-[%s]->(operator %s)" % \
    #              (LabelEdges.LABEL_REQUESTED.value, NodeHuman.LABEL_OPERATOR.value)
    #
    #     query += "\nRETURN %s, %s, issue.%s AS %s, issue.%s AS %s" % \
    #              (x_value, filter_value, NodeIssue.PROPERTY_DATE_MAINTENANCE_WORK_ORDER_ISSUE.value, "issue", NodeIssue.PROPERTY_DATE_MAINTENANCE_WORK_ORDER_CLOSE.value, "close")
    #
    #     query += ", count(DISTINCT issue) as %s"%(count_value)
    #     results = database.runQuery(query)
    #     dataframe = pd.DataFrame({x_value: [], filter_value: [], time_value:[], count_value:[]})
    #     for result in results:
    #         time = timeBetweenIsoStringDates(result['issue'], result['close'])
    #         if time is not None:
    #             time = time.total_seconds() / 60 / 60
    #         dataframe = dataframe.append({x_value: result[x_value], filter_value: result[filter_value], time_value: time, count_value: result[count_value]}, ignore_index=True)
    #     dataframe = dataframe.groupby([x_value, filter_value]).sum().reset_index()
    #     dataframe[average_value] = dataframe[time_value] / dataframe[count_value]
    #     return dataframe
    #
    # def abstract_kpi_timeline(database, filter_value, date_value, time_value="time", count_value="count", average_value="average"):
    #     """
    #     This function create an dataframe used to print a plot based on timeline
    #     the dataframe is represented with 5 collumn (filter_value, date_value, time_value, count_value, average_value)
    #
    #     :param database:        the Neo4j database you are working on
    #     :param filter_value:    one of the value you want to be in the dataframe
    #     :param date_value:      the data of the timeline
    #     :param time_value:      the total time spend
    #     :param count_value:     the number of issue solved
    #     :param average_value:   the avereag of time spend per issue
    #     :return:    dataframe contains all this information
    #     """
    #
    #     # TODO you can use MATCH (n) RETURN distinct labels(n) to find all label in the database,
    #     # or MATCH (n)
    #     # WITH DISTINCT labels(n) AS labels
    #     # UNWIND labels AS label
    #     # RETURN DISTINCT label
    #     # ORDER BY label
    #
    #     query = "MATCH (issue %s)-[%s]->(machine %s)" % \
    #             (NodeIssue.LABEL_ISSUE.value, LabelEdges.LABEL_COVERED.value, NodeMachine.LABEL_MACHINE.value)
    #     # query += "\nMATCH (machine)-[%s]->(machine_type %s)" % \
    #     #          (LabelEdges.LABEL_ISA.value, NodeMachine.LABEL_MACHINE_TYPE.value)
    #     query += "\nMATCH (issue)-[%s]->(item %s)" % \
    #             (LabelEdges.LABEL_CONTAINS.value, NodeTag.LABEL_ITEM.value)
    #     query += "\nMATCH (issue)-[%s]->(solution_action %s)" % \
    #             ( LabelEdges.LABEL_SOLUTION.value, NodeTag.LABEL_ACTION.value)
    #     query += "\nMATCH (issue)-[%s]->(problem_action %s)" % \
    #             (LabelEdges.LABEL_PROBLEM.value, NodeTag.LABEL_ACTION.value)
    #     query += "\nMATCH (issue)-[%s]->(technician %s)" % \
    #             (LabelEdges.LABEL_SOLVE.value, NodeHuman.LABEL_TECHNICIAN.value)
    #     query += "\nMATCH (issue)-[%s]->(operator %s)" % \
    #              (LabelEdges.LABEL_REQUESTED.value, NodeHuman.LABEL_OPERATOR.value)
    #
    #     query += "\nRETURN %s, %s, issue.%s AS %s, issue.%s AS %s" % \
    #              (date_value, filter_value, NodeIssue.PROPERTY_DATE_MAINTENANCE_WORK_ORDER_ISSUE.value, "issue", NodeIssue.PROPERTY_DATE_MAINTENANCE_WORK_ORDER_CLOSE.value, "close")
    #
    #     query += ", count(DISTINCT issue) as %s"%(count_value)
    #     results = database.runQuery(query)
    #     dataframe = pd.DataFrame({date_value: [], filter_value: [], time_value:[], count_value:[]})
    #     for result in results:
    #         if result[date_value] is not None:
    #             time = timeBetweenIsoStringDates(result['issue'], result['close'])
    #             if time is not None:
    #                 time = time.total_seconds() / 60 / 60
    #             date = datetime(year=int(result[date_value][:4]), month=int(result[date_value][5:7]), day=1)
    #             dataframe = dataframe.append({date_value: date, filter_value: result[filter_value], time_value: time, count_value: result[count_value]}, ignore_index=True)
    #
    #     dataframe = dataframe.groupby([filter_value, date_value]).sum().reset_index()
    #     dataframe[average_value] = dataframe[time_value] / dataframe[count_value]
    #     return dataframe
    #
    #
    # """ This are the KPI write without the general KPI parser"""
    #
    # """
    #
    #
    # def DateMonth_Machine(database, var1= "date", var2= "machine"):
    #
    #     query = 'MATCH (issue:ISSUE)-[:COVERED]->(mach:MACHINE) ' \
    #             'WHERE exists(issue.date_maintenance_work_order_issue)' \
    #             '\nRETURN issue.date_maintenance_work_order_issue AS %s, mach.name AS %s' % (var1, var2)
    #
    #     results = database.runQuery(query)
    #     dataframe = pd.DataFrame({var2: [], var1: []})
    #     for result in results:
    #         #date = isoStringToDate(result[var1])
    #         date = datetime(year=int(result[var1][:4]), month=int(result[var1][5:7]), day=1)
    #         dataframe = dataframe.append({var1: date, var2: result[var2]}, ignore_index=True)
    #     return dataframe
    #
    #
    #
    #
    #
    # def MaintenanceTechnician_Problem(database, var1= "technician", var2= "problem", var3="count"):
    #
    #     query = 'MATCH (tech:TECHNICIAN)<-[:SOLVE_BY]-(issue:ISSUE)' \
    #             '\nRETURN tech.name AS %s, issue.description_of_problem AS %s, count(issue) AS %s'%(var1,var2,var3)
    #     results = database.runQuery(query)
    #     dataframe = pd.DataFrame({var3:[],var2:[],var1:[]})
    #     for result in results:
    #         dataframe = dataframe.append({var1:result[var1], var2:result[var2], var3:result[var3]}, ignore_index=True)
    #     return dataframe
    #
    # def MaintenanceTechnician_Solution(database, var1= "technician", var2= "solution", var3= "count"):
    #
    #     query = 'MATCH (tech:TECHNICIAN)<-[:SOLVE_BY]-(issue:ISSUE)' \
    #             '\nRETURN tech.name AS %s, issue.description_of_solution AS %s, count(issue) AS %s' % (
    #                 var1, var2, var3)
    #     results = database.runQuery(query)
    #     dataframe = pd.DataFrame({var3: [], var2: [], var1: []})
    #     for result in results:
    #         dataframe = dataframe.append({var1: result[var1], var2: result[var2], var3: result[var3]}, ignore_index=True)
    #     return dataframe
    #
    # def Skill_Description(database, skill=None):
    #     pass
    #
    # def Craft_Description(database, craft=None):
    #     pass
    #
    # def Skill_Solution(database, skill=None):
    #     pass
    #
    # def Craft_Solution(database, craft=None):
    #     pass
    #
    # def MaintenanceTechnician_Machine(database, var1= "technician", var2= "machine", var3="count"):
    #
    #     query = 'MATCH (tech:TECHNICIAN)<-[:SOLVE_BY]-(issue:ISSUE)-[:COVERED]->(mach:MACHINE)' \
    #             '\nRETURN tech.name AS %s, mach.name AS %s, count(issue) AS %s'%(var1,var2,var3)
    #     results = database.runQuery(query)
    #     dataframe = pd.DataFrame({var3:[],var2:[],var1:[]})
    #     for result in results:
    #         dataframe = dataframe.append({var1:result[var1], var2:result[var2], var3:result[var3]}, ignore_index=True)
    #     return dataframe
    #
    # def MaintenanceTechnician_MachineType(database , var1= "technician", var2= "machine_type", var3="count"):
    #
    #     query = 'MATCH (tech:TECHNICIAN)<-[:SOLVE_BY]-(issue:ISSUE)-[:COVERED]->(:MACHINE)-[:IS_A]->(type:MACHINE_TYPE)' \
    #             '\nRETURN tech.name AS %s, type.type AS %s, count(issue) AS %s' % (var1, var2, var3)
    #     results = database.runQuery(query)
    #     dataframe = pd.DataFrame({var3: [], var2: [], var1: []})
    #     for result in results:
    #         dataframe = dataframe.append({var1: result[var1], var2: result[var2], var3: result[var3]}, ignore_index=True)
    #     return dataframe
    #
    # def MaintenanceTechnician_Machine_WorkOrderCompletionTime(database, var1= "technician", var2= "machine", var3="completion_time" ):
    #     query = 'MATCH (tech:TECHNICIAN)<-[:SOLVE_BY]-(issue:ISSUE)-[:COVERED]->(mach:MACHINE)' \
    #             '\nRETURN tech.name AS %s, mach.name AS %s , issue.date_maintenance_work_order_issue AS %s, issue.date_maintenance_work_order_close AS %s' % (
    #                 var1, var2, 'issue', 'close')
    #     results = database.runQuery(query)
    #     dataframe = pd.DataFrame({var3: [], var2: [], var1: []})
    #     for result in results:
    #         time = timeBetweenIsoStringDates(result['issue'],result['close'])
    #         if time is not None:
    #             time = time.total_seconds()/60/60
    #         dataframe = dataframe.append({var1: result[var1], var2: result[var2], var3: time}, ignore_index=True)
    #     return dataframe
    #
    # def MaintenanceTechnician_MachineType_WorkOrderCompletionTime(database, technician_name=None, machine_type=None):
    #     pass
    #
    # def MaintenanceTechnician_Item(database, var1="technician", var2="item", var3="count"):
    #     query = 'MATCH (tech%s)<-[%s]-(issue%s)-[%s]->(item%s)'\
    #         %(NodeHuman.LABEL_TECHNICIAN.value, LabelEdges.LABEL_SOLVE.value, NodeIssue.LABEL_ISSUE.value, LabelEdges.LABEL_CONTAINS.value, NodeTag.LABEL_ITEM.value)
    #     query += '\nRETURN tech.%s AS %s, item.%s AS %s, count(issue) AS %s ' \
    #              % (NodeHuman.PROPERTY_NAME.value, var1, NodeTag.PROPERTY_KEYWORD.value, var2, var3)
    #     results = database.runQuery(query)
    #     dataframe = pd.DataFrame({var3: [], var2: [], var1: []})
    #     for result in results:
    #         dataframe = dataframe.append({var1: result[var1], var2: result[var2], var3: result[var3]}, ignore_index=True)
    #     return dataframe
    #
    # def MaintenanceTechnician_ProblemAction(database, var1="technician", var2="problem", var3="count"):
    #     query = 'MATCH (tech%s)<-[%s]-(issue%s)-[%s]->(action%s)' \
    #             % (NodeHuman.LABEL_TECHNICIAN.value, LabelEdges.LABEL_SOLVE.value, NodeIssue.LABEL_ISSUE.value,
    #                LabelEdges.LABEL_PROBLEM.value, NodeTag.LABEL_ACTION.value)
    #     query += '\nRETURN tech.%s AS %s, action.%s AS %s, count(issue) AS %s ' \
    #              % (NodeHuman.PROPERTY_NAME.value, var1, NodeTag.PROPERTY_KEYWORD.value, var2, var3)
    #     results = database.runQuery(query)
    #     dataframe = pd.DataFrame({var3: [], var2: [], var1: []})
    #     for result in results:
    #         dataframe = dataframe.append({var1: result[var1], var2: result[var2], var3: result[var3]}, ignore_index=True)
    #     return dataframe
    #
    # def MaintenanceTechnician_SolutionAction(database, var1="technician", var2="solution", var3="count"):
    #     query = 'MATCH (tech%s)<-[%s]-(issue%s)-[%s]->(action%s)' \
    #             % (NodeHuman.LABEL_TECHNICIAN.value, LabelEdges.LABEL_SOLVE.value, NodeIssue.LABEL_ISSUE.value,
    #                LabelEdges.LABEL_SOLUTION.value, NodeTag.LABEL_ACTION.value)
    #     query += '\nRETURN tech.%s AS %s, action.%s AS %s, count(issue) AS %s ' \
    #              % (NodeHuman.PROPERTY_NAME.value, var1, NodeTag.PROPERTY_KEYWORD.value, var2, var3)
    #     results = database.runQuery(query)
    #     dataframe = pd.DataFrame({var3: [], var2: [], var1: []})
    #     for result in results:
    #         dataframe = dataframe.append({var1: result[var1], var2: result[var2], var3: result[var3]}, ignore_index=True)
    #     return dataframe
    #
    # def Skill_Item(database, skill=None, item=None):
    #     pass
    #
    # def Craft_Item(database, craft=None, item=None):
    #     pass
    #
    # def Skill_ProblemAction(database, skill=None, problem_action=None):
    #     pass
    #
    # def Crafts_ProblemAction(database, craft=None, problem_action=None):
    #     pass
    #
    # def MaintenanceTechnician_Item_WorkOrderCompletionTime(database, var1="technician", var2="solution", var3="completion_time"):
    #     query = 'MATCH (tech%s)<-[%s]-(issue%s)-[%s]->(item%s)' \
    #             % (NodeHuman.LABEL_TECHNICIAN.value, LabelEdges.LABEL_SOLVE.value, NodeIssue.LABEL_ISSUE.value,
    #                LabelEdges.LABEL_CONTAINS.value, NodeTag.LABEL_ITEM.value)
    #     query += '\nRETURN tech.%s AS %s, item.%s AS %s, issue.%s AS %s, issue.%s AS %s' \
    #              % (NodeHuman.PROPERTY_NAME.value, var1, NodeTag.PROPERTY_KEYWORD.value, var2,
    #                 NodeIssue.PROPERTY_DATE_MAINTENANCE_WORK_ORDER_ISSUE.value, "issue", NodeIssue.PROPERTY_DATE_MAINTENANCE_WORK_ORDER_CLOSE.value, "close")
    #     results = database.runQuery(query)
    #     dataframe = pd.DataFrame({var3: [], var2: [], var1: []})
    #     for result in results:
    #         time = timeBetweenIsoStringDates(result['issue'], result['close'])
    #         if time is not None:
    #             time = time.total_seconds() / 60 / 60
    #         dataframe = dataframe.append({var1: result[var1], var2: result[var2], var3: time}, ignore_index=True)
    #     return dataframe
    #
    # def MaintenanceTechnician_ProblemAction_WorkOrderCompletionTime(database, technician_name=None, problem_action=None):
    #     pass
    #
    # def MaintenanceTechnician_SolutionAction_WorkOrderCompletionTime(database, technician_name=None, solution_action=None):
    #     pass
    #
    # def Machine_TimeBetweenWorkOrder(database, machine_name=None):
    #     pass
    #
    # def MachineType_TimeBetweenWorkOrder(database, machine_type=None):
    #     pass
    #
    # def Machine_WorkOrderCompletionTime(database, machine_name=None):
    #     pass
    #
    # def MachineType_WorkOrderCompletionTime(database, machine_type=None):
    #     pass
    #
    # def Machine_TimeBetweenWorkOrder_Item(database, machine_name=None):
    #     pass
    #
    # def Machine_TimeBetweenWorkOrder_ProblemAction(database, machine_name=None, problem_action=None):
    #     pass
    #
    # def Machine_TimeBetweenWorkOrder_SolutionAction(database, machine_name=None, solution_action=None):
    #     pass
    #
    # def Machine_WorkOrderCompletionTime_Item(database, machine_name=None, item=None):
    #     pass
    #
    # def Machine_WorkOrderCompletionTime_ProblemAction(database, machine_name=None, problem_action=None):
    #     pass
    #
    # def Machine_WorkOrderCompletionTime_SolutionAction(database, machine_name=None, solution_action=None):
    #     pass
    #
    # def MachineType_TimeBetweenWorkOrder_Item(database, machine_type=None, item=None):
    #     pass
    #
    # def MachineType_TimeBetweenWorkOrder_ProblemAction(database, machine_type=None, problem_action=None):
    #     pass
    #
    # def MachineType_TimeBetweenWorkOrder_SolutionAction(database, machine_type=None, solution_action=None):
    #     pass
    #
    # def MachineType_WorkOrderCompletionTime_Item(database, machine_type=None, item=None):
    #     pass
    #
    # def MachineType_WorkOrderCompletionTime_ProblemAction(database, machine_type=None, problem_action=None):
    #     pass
    #
    # def MachineType_WorkOrderCompletionTime_SolutionAction(database, machine_type=None, solution_action=None):
    #     pass
    #
    # def Operator_ProblemAction(database, operator_name=None, problem_action=None):
    #     pass
    #
    # def Operator_ProblemItem(database, operator_name=None, item=None):
    #     pass
    #
    # def Operator_ProblemItem_WorkOrderCompletionTime(database, operator_name=None, item=None):
    #     pass
    #
    # def Item_TimeBetweenWorkOrder(database, item=None):
    #     pass
    #
    # def Item_WorkOrderCompletionTime(database, item=None):
    #     pass
    #
    # def ProblemAction_TimeBetweenWorkOrder(database, problem_action_None):
    #     pass
    #
    # def ProblemAction_WorkOrderCompletionTime(database, problem_action_None):
    #     pass
    #
    # def SolutionAction_WorkOrderCompletionTime(database, solution_action=None):
    #     pass
    #
    # def SolutionAction_TimeBetweenWorkOrder(database, solution_action=None):
    #     pass
    #
    #
    #
    #
    # """
    #
    #
    #
    # """
    #
    # varTechnician = "technician"
    # varProblem = "problem"
    # varCount = "count"
    #
    # dataframe = MaintenanceTechnician_Problem(database, varTechician, varProblem, varCount)
    #
    #
    # ## GREYSTONE ##
    #     # Lyle Cookson
    #
    # # filter = ["Lyle Cookson"]
    # # #filter = ["Lyle Cookson","Jon Cousineau"]
    # # data=dataframe[(dataframe[varTechnician].isin(filter))].sort_values(by=[varCount], ascending=False)
    # # ax = sns.barplot(y=varProblem, x=varCount,hue=varTechician,  data=data)
    # # ax.set(xlabel='Problem', ylabel='Number of Issue Solved', title='Number of issue solved by %s per raw text problem'%(filter) )
    #
    #
    #
    # filter = ["Accumulator check requested", "Hydraulic leak"]
    # data=dataframe[(dataframe[varProblem].isin(filter)) & (dataframe["count"]>0)].sort_values(by=["count"], ascending=False)
    # ax = sns.barplot(y=varTechician, x=varCount,hue=varProblem,  data=data)
    # ax.set(xlabel='Problem', ylabel='Number of Issue Solved', title='Number of issue solved by Technicians about %s'%(filter) )
    #
    #
    #
    #
    # --------------------------------------------
    #
    #
    #
    # varTechnician = "technician"
    # varMachine = "machine"
    # varTime = "completion_time"
    # varCount = "count"
    # varAVG = "avereage"
    #
    # Dataframe = MaintenanceTechnician_Machine_WorkOrderCompletionTime(database, varTechnician, varMachine,varTime)
    # data = Dataframe[pd.notnull(Dataframe[varTime])]
    # data[varCount]=1
    # data = data.groupby([varMachine, varTechnician]).sum().reset_index()
    # data[varAVG] = data[varTime]/data[varCount]
    #
    #
    # # filter = ["Lyle Cookson"]
    # # data=data[(data[varTechnician].isin(filter))].sort_values(by=[varAVG], ascending=False)
    # # ax = sns.barplot(y=varAVG, x=varMachine, hue=varTechnician,  data=data)
    # # ax.set(xlabel='Machine', ylabel='Avereage WorkOrderCompletionTime', title='Avereage WorkOrderCompletionTime by %s per machine'%(filter) )
    #
    # # filter = ["H16"]
    # # data=data[(data[varMachine].isin(filter))].sort_values(by=[varAVG], ascending=False)
    # # ax = sns.barplot(y=varAVG, x=varTechnician, hue=varMachine, data=data)
    # # ax.set(xlabel='Machine', ylabel='Avereage WorkOrderCompletionTime', title='Avereage WorkOrderCompletionTime on %s per Technician'%(filter) )
    #
    #
    # # filter = ["Lyle Cookson"]
    # # data=data[(data[varTechnician].isin(filter))].sort_values(by=[varCount], ascending=False)
    # # ax = sns.barplot(y=varCount, x=varMachine, hue=varTechnician,  data=data)
    # # ax.set(xlabel='Machine', ylabel='Number of Issue', title='Number of Issue by %s per machine'%(filter) )
    #
    # filter = ["H16"]
    # data=data[(data[varMachine].isin(filter))].sort_values(by=[varCount], ascending=False)
    # ax = sns.barplot(y=varCount, x=varTechnician, hue=varMachine,  data=data)
    # ax.set(xlabel='Machine', ylabel='Number of Issue', title='Number of Issue on %s per Technician'%(filter) )
    #
    #
    #
    # """
