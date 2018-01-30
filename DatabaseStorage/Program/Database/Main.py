import csv

from Program.Database.Database_Properties import *
from Program.Objects.Human import *
from Program.Objects.Issue import *
from Program.Objects.Machine import *
from Program.Objects.MaintenanceWorkOrder import *
from Program.Objects.Tag import *
from Program.Others.MyDate import clean_GS_date
from tqdm import tqdm
import os
import pandas as pd


"""
This files contains all the function to extract the MWOs from a CSV format to store it in a Neo4J Database

The localisation is a dictionary which describe the CSV file (what column contains what information):
 localization = {NodeHuman.VALUE_TECHNICIAN.value: ,
                    NodeHuman.VALUE_OPERATOR.value: ,
                    NodeHuman.VALUE_CRAFTS.value:,
                    NodeHuman.VALUE_SKILLS.value:,

                    NodeTag.VALUE_ITEM.value: ,
                    NodeTag.VALUE_PROBLEM.value: ,
                    NodeTag.VALUE_SOLUTION.value: ,

                    NodeMachine.VALUE_MACHINE.value: ,
                    NodeMachine.VALUE_TYPE.value:,
                    NodeMachine.VALUE_MANUFACTURER.value:,
                    NodeMachine.VALUE_LOCASION.value:,

                    NodeIssue.VALUE_DESCRIPTION_PROBLEM.value: ,
                    NodeIssue.VALUE_DESCRIPTION_SOLUTION.value: ,
                    NodeIssue.VALUE_DESCRIPTION_CAUSE.value:,
                    NodeIssue.VALUE_DESCRIPTION_EFFECT.value:,
                    NodeIssue.VALUE_PART_PROCESS.value: ,
                    NodeIssue.PROPERTY_NECESSARY_PART.value: ,
                    NodeIssue.VALUE_DATE_MACHINE_DOWN.value:,
                    NodeIssue.VALUE_DATE_MACHINE_UP.value:,
                    NodeIssue.VALUE_DATE_MAINTENANCE_WORK_ORDER_ISSUE.value:,
                    NodeIssue.VALUE_DATE_MAINTENANCE_WORK_ORDER_CLOSE.value:,
                    NodeIssue.VALUE_DATE_TECHNICIAN_ARRIVE.value:,
                    NodeIssue.VALUE_DATE_PROBLEM_FOUND.value:,
                    NodeIssue.VALUE_DATE_PROBLEM_SOLVE.value:,
                    NodeIssue.VALUE_DATE_PART_ORDER.value:,
                    NodeIssue.VALUE_DATE_MAINTENANCE_TECHNICIAN_REPAIR_PROBLEM.value:,

                    }
"""

def graph_database_from_csv(database, file_path, localization, date_cleanizer = None):
    """

    :param database: the Neo4j database in which you want to store the data
    :param file_path: the path of your CSV file
    :param localization: a dictionary with the description of your csv file (where is which record) :
            localization = {NodeHuman.VALUE_TECHNICIAN.value: ,
                    NodeHuman.VALUE_OPERATOR.value: ,
                    NodeHuman.VALUE_CRAFTS.value:,
                    NodeHuman.VALUE_SKILLS.value:,

                    NodeTag.VALUE_ITEM.value: ,
                    NodeTag.VALUE_PROBLEM.value: ,
                    NodeTag.VALUE_SOLUTION.value: ,

                    NodeMachine.VALUE_MACHINE.value: ,
                    NodeMachine.VALUE_TYPE.value:,
                    NodeMachine.VALUE_MANUFACTURER.value:,
                    NodeMachine.VALUE_LOCASION.value:,

                    NodeIssue.VALUE_DESCRIPTION_PROBLEM.value: ,
                    NodeIssue.VALUE_DESCRIPTION_SOLUTION.value: ,
                    NodeIssue.VALUE_DESCRIPTION_CAUSE.value:,
                    NodeIssue.VALUE_DESCRIPTION_EFFECT.value:,
                    NodeIssue.VALUE_PART_PROCESS.value: ,
                    NodeIssue.PROPERTY_NECESSARY_PART.value: ,
                    NodeIssue.VALUE_DATE_MACHINE_DOWN.value:,
                    NodeIssue.VALUE_DATE_MACHINE_UP.value:,
                    NodeIssue.VALUE_DATE_MAINTENANCE_WORK_ORDER_ISSUE.value:,
                    NodeIssue.VALUE_DATE_MAINTENANCE_WORK_ORDER_CLOSE.value:,
                    NodeIssue.VALUE_DATE_TECHNICIAN_ARRIVE.value:,
                    NodeIssue.VALUE_DATE_PROBLEM_FOUND.value:,
                    NodeIssue.VALUE_DATE_PROBLEM_SOLVE.value:,
                    NodeIssue.VALUE_DATE_PART_ORDER.value:,
                    NodeIssue.VALUE_DATE_MAINTENANCE_TECHNICIAN_REPAIR_PROBLEM.value:,

                    }
    :return:
    """

    def create_MWO(row, localization, date_cleanizer = None):

        #####   TECHNICIAN #####
        def create_technicians(row, localization):
            skills = []
            try:
                for skill in row[localization[NodeHuman.VALUE_SKILLS.value]].split('/'):
                    skills.append(skill)
            except KeyError:
                pass

            crafts = []
            try:
                for craft in row[localization[NodeHuman.VALUE_CRAFTS.value]].split('/'):
                    crafts.append(craft)
            except KeyError:
                pass

            technicians = []
            try:
                for technician in row[localization[NodeHuman.VALUE_TECHNICIAN.value]].split('/'):
                    technicians.append(Technician(name=technician, skills=skills, crafts=crafts))
            except KeyError:
                pass

            return technicians

        #####   OPERATOR #####
        def create_operators(row, localization):
            operators = []
            try:
                for operator in row[localization[NodeHuman.VALUE_OPERATOR.value]].split('/'):
                    operators.append(Operator(name=operator))
            except KeyError:
                pass

            return operators

        #####   MACHINE #####
        def create_machine(row, localization):
            machine = None

            try:
                machine = Machine(name=row[localization[NodeMachine.VALUE_MACHINE.value]])

                try:
                    machine._set_manufacturer(row[localization[NodeMachine.VALUE_MANUFACTURER.value]])
                except KeyError:
                    pass

                try:
                    machine._set_machine_type(row[localization[NodeMachine.VALUE_TYPE.value]])
                except KeyError:
                    pass

                try:
                    machine._set_locasion(row[localization[NodeMachine.VALUE_LOCASION.value]])
                except KeyError:
                    pass

            except KeyError:
                pass

            return machine

        #####   TAG #####
        def create_items(row, localization):
            items = []

            try:
                for item in row[localization[NodeTag.VALUE_ITEM.value]].split('/'):
                    items.append(TagItem(keyword=item))
            except KeyError:
                pass

            return items

        def create_problems(row, localization):
            problems = []

            try:
                for problem in row[localization[NodeTag.VALUE_PROBLEM.value]].split('/'):
                    problems.append(TagAction(keyword=problem))
            except KeyError:
                pass

            return problems


        def create_solutions(row, localization):
            solutions = []

            try:
                for solution in row[localization[NodeTag.VALUE_SOLUTION.value]].split('/'):
                    solutions.append(TagAction(keyword=solution))
            except KeyError:
                pass

            return solutions

        #####   ISSUE #####
        def create_issue(row, localization, date_cleanizer = None):
            issue = None

            try:
                issue = Issue(problem=row[localization[NodeIssue.VALUE_DESCRIPTION_PROBLEM.value]],
                              solution=row[localization[NodeIssue.VALUE_DESCRIPTION_SOLUTION.value]])
                try:
                    issue._set_cause(row[localization[NodeIssue.VALUE_DESCRIPTION_CAUSE.value]])
                except KeyError:
                    pass
                try:
                    issue._set_effects(row[localization[NodeIssue.VALUE_DESCRIPTION_EFFECT.value]])
                except KeyError:
                    pass
                try:
                    issue._set_part_in_process(row[localization[NodeIssue.VALUE_PART_PROCESS.value]])
                except KeyError:
                    pass
                try:
                    issue._set_necessary_part(row[localization[NodeIssue.VALUE_NECESSARY_PART.value]])
                except KeyError:
                    pass
                try:
                    issue._set_machine_down(row[localization[NodeIssue.VALUE_MACHINE_DOWN.value]])
                except KeyError:
                    pass
                try:
                    if NodeIssue.VALUE_DATE_MACHINE_DOWN.value + "2" in localization \
                            and row[localization[NodeIssue.VALUE_DATE_MACHINE_DOWN.value + "2"]] is not "":
                        issue._set_date_machine_down(
                            date_cleanizer(
                                row[localization[NodeIssue.VALUE_DATE_MACHINE_DOWN.value]],
                                row[localization[NodeIssue.VALUE_DATE_MACHINE_DOWN.value + "2"]]
                            )
                        )
                    elif NodeIssue.VALUE_DATE_MACHINE_DOWN.value in localization.keys():
                        issue._set_date_machine_down(
                            date_cleanizer(
                                row[localization[NodeIssue.VALUE_DATE_MACHINE_DOWN.value]]
                            )
                        )
                except (KeyError, AttributeError):
                    pass
                try:
                    if NodeIssue.VALUE_DATE_MACHINE_UP.value + "2" in localization \
                            and row[localization[NodeIssue.VALUE_DATE_MACHINE_UP.value + "2"]] is not "":
                        issue._set_date_machine_up(
                            date_cleanizer(
                                row[localization[NodeIssue.VALUE_DATE_MACHINE_UP.value]],
                                row[localization[NodeIssue.VALUE_DATE_MACHINE_UP.value + "2"]]
                            )
                        )
                    elif NodeIssue.VALUE_DATE_MACHINE_UP.value in localization.keys():
                        issue._set_date_machine_up(
                            date_cleanizer(
                                row[localization[NodeIssue.VALUE_DATE_MACHINE_UP.value]]
                            )
                        )
                except (KeyError, AttributeError):
                    pass
                try:
                    if NodeIssue.VALUE_DATE_MAINTENANCE_WORK_ORDER_ISSUE.value + "2" in localization \
                            and row[localization[NodeIssue.VALUE_DATE_MAINTENANCE_WORK_ORDER_ISSUE.value + "2"]] is not "":
                        issue._set_date_maintenance_work_order_issue(
                            date_cleanizer(
                                row[localization[NodeIssue.VALUE_DATE_MAINTENANCE_WORK_ORDER_ISSUE.value]],
                                row[localization[NodeIssue.VALUE_DATE_MAINTENANCE_WORK_ORDER_ISSUE.value + "2"]])
                        )
                    elif NodeIssue.VALUE_DATE_MAINTENANCE_WORK_ORDER_ISSUE.value in localization.keys():
                        issue._set_date_maintenance_work_order_issue(
                            date_cleanizer(
                                row[localization[NodeIssue.VALUE_DATE_MAINTENANCE_WORK_ORDER_ISSUE.value]])
                        )
                except (KeyError, AttributeError):
                    pass
                try:
                    if NodeIssue.VALUE_DATE_MAINTENANCE_WORK_ORDER_CLOSE.value + "2" in localization \
                            and row[localization[NodeIssue.VALUE_DATE_MAINTENANCE_WORK_ORDER_CLOSE.value + "2"]] is not "":
                        issue._set_date_maintenance_work_order_close(
                            date_cleanizer(
                                row[localization[NodeIssue.VALUE_DATE_MAINTENANCE_WORK_ORDER_CLOSE.value]],
                                row[localization[NodeIssue.VALUE_DATE_MAINTENANCE_WORK_ORDER_CLOSE.value + "2"]])
                        )
                    elif NodeIssue.VALUE_DATE_MAINTENANCE_WORK_ORDER_CLOSE.value in localization.keys():
                        issue._set_date_maintenance_work_order_close(
                            date_cleanizer(
                                row[localization[NodeIssue.VALUE_DATE_MAINTENANCE_WORK_ORDER_CLOSE.value]])
                        )
                except (KeyError, AttributeError):
                    pass
                try:
                    if NodeIssue.VALUE_DATE_TECHNICIAN_ARRIVE.value + "2" in localization \
                            and row[localization[NodeIssue.VALUE_DATE_TECHNICIAN_ARRIVE.value + "2"]] is not "":
                        issue._set_date_maintenance_technician_arrives(
                            date_cleanizer(
                                row[localization[NodeIssue.VALUE_DATE_TECHNICIAN_ARRIVE.value]],
                                row[localization[NodeIssue.VALUE_DATE_TECHNICIAN_ARRIVE.value + "2"]])
                        )
                    elif NodeIssue.VALUE_DATE_TECHNICIAN_ARRIVE.value in localization.keys():
                        issue._set_date_maintenance_technician_arrives(
                            date_cleanizer(
                                row[localization[NodeIssue.VALUE_DATE_TECHNICIAN_ARRIVE.value]])
                        )
                except (KeyError, AttributeError):
                    pass
                try:
                    if NodeIssue.VALUE_DATE_PROBLEM_FOUND.value + "2" in localization \
                            and row[localization[NodeIssue.VALUE_DATE_PROBLEM_FOUND.value + "2"]] is not "":
                        issue._set_date_problem_found(
                            date_cleanizer(
                                row[localization[NodeIssue.VALUE_DATE_PROBLEM_FOUND.value]],
                                row[localization[NodeIssue.VALUE_DATE_PROBLEM_FOUND.value + "2"]])
                        )
                    elif NodeIssue.VALUE_DATE_PROBLEM_FOUND.value in localization.keys():
                        issue._set_date_problem_found(
                            date_cleanizer(
                                row[localization[NodeIssue.VALUE_DATE_PROBLEM_FOUND.value]])
                        )
                except (KeyError, AttributeError):
                    pass
                try:
                    if NodeIssue.VALUE_DATE_PROBLEM_SOLVE.value + "2" in localization \
                            and row[localization[NodeIssue.VALUE_DATE_PROBLEM_SOLVE.value + "2"]] is not "":
                        issue._set_date_problem_solved(
                            date_cleanizer(
                                row[localization[NodeIssue.VALUE_DATE_PROBLEM_SOLVE.value]],
                                row[localization[NodeIssue.VALUE_DATE_PROBLEM_SOLVE.value + "2"]])
                        )
                    elif NodeIssue.VALUE_DATE_PROBLEM_SOLVE.value in localization.keys():
                        issue._set_date_problem_solved(
                            date_cleanizer(
                                row[localization[NodeIssue.VALUE_DATE_PROBLEM_SOLVE.value]])
                        )
                except (KeyError, AttributeError):
                    pass
                try:
                    if NodeIssue.VALUE_DATE_PART_ORDER.value + "2" in localization \
                            and row[localization[NodeIssue.VALUE_DATE_PART_ORDER.value + "2"]] is not "":
                        issue._set_date_part_ordered(
                            date_cleanizer(
                                row[localization[NodeIssue.VALUE_DATE_PART_ORDER.value]],
                                row[localization[NodeIssue.VALUE_DATE_PART_ORDER.value + "2"]])
                        )
                    elif NodeIssue.VALUE_DATE_PART_ORDER.value in localization.keys():
                        issue._set_date_part_ordered(
                            date_cleanizer(
                                row[localization[NodeIssue.VALUE_DATE_PART_ORDER.value]])
                        )
                except (KeyError, AttributeError):
                    pass
                try:
                    if NodeIssue.VALUE_DATE_MAINTENANCE_TECHNICIAN_REPAIR_PROBLEM.value + "2" in localization \
                            and row[localization[NodeIssue.VALUE_DATE_MAINTENANCE_TECHNICIAN_REPAIR_PROBLEM.value + "2"]] is not "":
                        issue._set_date_maintenance_technician_begin_repair_problem(
                            date_cleanizer(
                                row[localization[NodeIssue.VALUE_DATE_MAINTENANCE_TECHNICIAN_REPAIR_PROBLEM.value]],
                                row[localization[NodeIssue.VALUE_DATE_MAINTENANCE_TECHNICIAN_REPAIR_PROBLEM.value + "2"]])
                        )
                    elif NodeIssue.VALUE_DATE_MAINTENANCE_TECHNICIAN_REPAIR_PROBLEM.value in localization.keys():
                        issue._set_date_maintenance_technician_begin_repair_problem(
                            date_cleanizer(
                                row[localization[NodeIssue.VALUE_DATE_MAINTENANCE_TECHNICIAN_REPAIR_PROBLEM.value]])
                        )
                except (KeyError, AttributeError):
                    pass
            except KeyError:
                pass
            return issue

        #####   CORE  #####
        technicians = create_technicians(row, localization)
        operators = create_operators(row, localization)
        machine = create_machine(row, localization)
        items = create_items(row, localization)
        problems = create_problems(row, localization)
        solutions = create_solutions(row, localization)
        issue = create_issue(row, localization, date_cleanizer)

        return MaintenanceWorkOrder(issue=issue,
                                    machine=machine,
                                    operators=operators,
                                    technicians=technicians,
                                    tag_items=items,
                                    tag_problems=problems,
                                    tag_solutions=solutions
                                    )

    with open(file_path, encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        csvfile.seek(0)
        # Only used for the tqdm
        num_lines=0
        for line in csvfile:                        # get the number total of row in the csv
            num_lines +=1
        csvfile.seek(0)                             # reset the reader at the first line

        for row in tqdm(reader, total=num_lines):
        #for row in reader:
            mwo = create_MWO(row, localization, date_cleanizer)
            query = mwo.cypher_mwo_graphdata("issue", "machine", "machine_type", "operators", "technicians", "items", "problems", "solutions")
            database.runQuery(query=query)



def graph_database_from_tag_extractor(database, token_dataframe= None):
    """
    token_dataframe :

        Description   |   Resolution    |    I  |   P   |   S   |   U   |   X   |   NA

    """

    for index, row in tqdm(token_dataframe.iterrows(), total=len(token_dataframe.index)):
        issue = Issue(problem = row["Description"], solution = row["Resolution"])
        items = []
        problems = []
        solutions = []
        unknowns = []
        others = []

        try:
            for i in row["I"].split(", "):
                items.append(TagItem(keyword=i))
        except AttributeError:
            pass
        try:
            for p in row["P"].split(", "):
                problems.append(TagAction(keyword=p, it_is="p"))
        except AttributeError:
            pass
        try:
            for s in row["S"].split(", "):
                solutions.append(TagAction(keyword=s, it_is="s"))
        except AttributeError:
            pass
        try:
            for u in row["U"].split(", "):
                unknowns.append(TagUnknown(keyword=u))
        except AttributeError:
            pass
        try:
            for x in row["X"].split(", "):
                others.append(Tag(keyword=x))
        except AttributeError:
            pass
        try:
            for x in row["NA"].split(", "):
                others.append(Tag(keyword=x))
        except AttributeError:
            pass

        mwo = MaintenanceWorkOrder(issue = issue, tag_items=items, tag_problems=problems, tag_solutions=solutions, tag_unknowns=unknowns, tag_others= others)

        query = mwo.cypher_mwo_tagdata("issue", "tag_item", "tag_action_problem", "tag_action_solution", "tag_unknown", "tag_other")
        query += "RETURN 1"

        database.runQuery(query=query)