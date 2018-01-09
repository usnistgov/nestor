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

def GraphDatabaseCsv(database, file_path, localization, date_cleanizer = None):
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

    def createMWO(row, localization, date_cleanizer = None):

        #####   TECHNICIAN #####
        def createTechnicians(row, localization):
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
                    technicians.append(Human(name=technician, skills=skills, crafts=crafts))
            except KeyError:
                pass

            return technicians

        #####   OPERATOR #####
        def createOperators(row, localization):
            operators = []
            try:
                for operator in row[localization[NodeHuman.VALUE_OPERATOR.value]].split('/'):
                    operators.append(Human(name=operator))
            except KeyError:
                pass

            return operators

        #####   MACHINE #####
        def createMachine(row, localization):
            machine = None

            try:
                machine = Machine(name=row[localization[NodeMachine.VALUE_MACHINE.value]])

                try:
                    machine._set_manufacturer(row[localization[NodeMachine.VALUE_MANUFACTURER.value]])
                except KeyError:
                    pass

                try:
                    machine._set_type(row[localization[NodeMachine.VALUE_TYPE.value]])
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
        def createTags(row, localization, collumn):
            tags = []

            try:
                for item in row[localization[collumn]].split('/'):
                    tags.append(Tag(keyword=item))
            except KeyError:
                pass

            return tags

        #####   ISSUE #####
        def createIssue(row, localization, date_cleanizer = None):
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
        technicians = createTechnicians(row, localization)
        operators = createOperators(row, localization)
        machine = createMachine(row, localization)
        items = createTags(row, localization, NodeTag.VALUE_ITEM.value)
        problems = createTags(row, localization, NodeTag.VALUE_PROBLEM.value)
        solutions = createTags(row, localization, NodeTag.VALUE_SOLUTION.value)
        issue = createIssue(row, localization, date_cleanizer)

        return MaintenanceWorkOrder(issue=issue,
                                    machine=machine,
                                    operators=operators,
                                    technicians=technicians,
                                    itemtags=items,
                                    problemtags=problems,
                                    solutiontags=solutions
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
            mwo = createMWO(row, localization, date_cleanizer)
            query = mwo.create_database("issue", "machine", "machinetype", "operator", "technician", "item", "problem", "solution")
            database.runQuery(query=query)




def GraphDatabaseFromGreyStoneCsv(database):
    """
    Store the data from Greystone CSV
    :param database: the Neo4j database
    """
    file = "Data_CSV/GreyStone_Data.csv"
    file = os.path.abspath()
    localization = {NodeHuman.VALUE_TECHNICIAN.value: 15,
                    NodeHuman.VALUE_OPERATOR.value: 13,

                    NodeTag.VALUE_ITEM.value: 2,
                    NodeTag.VALUE_PROBLEM.value: 3,
                    NodeTag.VALUE_SOLUTION.value: 4,

                    NodeMachine.VALUE_MACHINE.value: 7,
                    NodeIssue.VALUE_MACHINE_DOWN.value: 8,

                    NodeIssue.VALUE_DESCRIPTION_PROBLEM.value: 0,
                    NodeIssue.VALUE_DESCRIPTION_SOLUTION.value: 1,
                    NodeIssue.VALUE_PART_PROCESS.value: 16,
                    }

    GraphDatabaseCsv(database, file, localization)

def GraphDatabaseFromAutoCsv(database):
    """
    Store the data from Auto CSV
    :param database: the Neo4j database
    """
    file = "Data_CSV/Auto_Data.csv"
    localization = {NodeHuman.VALUE_TECHNICIAN.value: 4,
                    NodeHuman.VALUE_OPERATOR.value: 11,
                    NodeHuman.VALUE_CRAFTS.value: 16,
                    NodeHuman.VALUE_SKILLS.value: 17,

                    NodeMachine.VALUE_MACHINE.value: 8,

                    NodeIssue.VALUE_DESCRIPTION_PROBLEM.value: 5,
                    NodeIssue.VALUE_DESCRIPTION_SOLUTION.value: 7,
                    }

    GraphDatabaseCsv(database, file, localization)


def GraphDatabaseFromHvacCsv(database):
    """
    Store the data from Hvac CSV
    :param database: the Neo4j database
    """
    file = "Data_CSV/Hvac_Data.csv"
    localization = {NodeHuman.VALUE_TECHNICIAN.value: 10,
                    NodeHuman.VALUE_OPERATOR.value: 43,

                    NodeMachine.VALUE_MACHINE.value: 7,

                    NodeIssue.VALUE_DESCRIPTION_PROBLEM.value: 5,
                    NodeIssue.VALUE_DESCRIPTION_SOLUTION.value: 247,
                    }

    GraphDatabaseCsv(database, file, localization)

def GraphDatabaseFromPsuCsv(database):
    """
    Store the data from Psu CSV
    :param database: the Neo4j database
    """
    file = "Data_CSV/Psu_Data.csv"
    localization = {NodeHuman.VALUE_TECHNICIAN.value: 18,

                    NodeMachine.VALUE_MACHINE.value: 3,
                    NodeMachine.VALUE_TYPE.value:6,
                    NodeMachine.VALUE_MANUFACTURER.value:5,
                    NodeMachine.VALUE_LOCASION.value:4,


                    NodeIssue.VALUE_DESCRIPTION_PROBLEM.value: 11,
                    NodeIssue.VALUE_DESCRIPTION_SOLUTION.value: 19,
                    NodeIssue.VALUE_DESCRIPTION_CAUSE.value:12,
                    NodeIssue.VALUE_MACHINE_DOWN.value: 13,
                    }

    GraphDatabaseCsv(database, file, localization)

def GraphDatabaseFromTestCsv(database):
    """
    Store the data from Test CSV
    a fake csv files that contains all data in the right format
    :param database: the Neo4j database
    """
    file = "Data_CSV/test.csv"
    localization = {NodeHuman.VALUE_TECHNICIAN.value: 0,
                    NodeHuman.VALUE_OPERATOR.value: 1,
                    NodeHuman.VALUE_CRAFTS.value:2,
                    NodeHuman.VALUE_SKILLS.value:3,

                    NodeTag.VALUE_ITEM.value: 4,
                    NodeTag.VALUE_PROBLEM.value: 5,
                    NodeTag.VALUE_SOLUTION.value: 6,

                    NodeMachine.VALUE_MACHINE.value:7 ,
                    NodeMachine.VALUE_TYPE.value:8,
                    NodeMachine.VALUE_MANUFACTURER.value:9,
                    NodeMachine.VALUE_LOCASION.value:10,

                    NodeIssue.VALUE_DESCRIPTION_PROBLEM.value: 11,
                    NodeIssue.VALUE_DESCRIPTION_SOLUTION.value: 12,
                    NodeIssue.VALUE_DESCRIPTION_CAUSE.value:13,
                    NodeIssue.VALUE_DESCRIPTION_EFFECT.value:14,
                    NodeIssue.VALUE_MACHINE_DOWN.value:15,
                    NodeIssue.VALUE_PART_PROCESS.value: 16,
                    NodeIssue.PROPERTY_NECESSARY_PART.value: 17,
                    NodeIssue.VALUE_DATE_MACHINE_DOWN.value:18,
                    NodeIssue.VALUE_DATE_MACHINE_UP.value:19,
                    NodeIssue.VALUE_DATE_MAINTENANCE_WORK_ORDER_ISSUE.value:20,
                    NodeIssue.VALUE_DATE_MAINTENANCE_WORK_ORDER_CLOSE.value:21,
                    NodeIssue.VALUE_DATE_TECHNICIAN_ARRIVE.value:22,
                    NodeIssue.VALUE_DATE_PROBLEM_FOUND.value:23,
                    NodeIssue.VALUE_DATE_PROBLEM_SOLVE.value:24,
                    NodeIssue.VALUE_DATE_PART_ORDER.value:25,
                    NodeIssue.VALUE_DATE_MAINTENANCE_TECHNICIAN_REPAIR_PROBLEM.value:26,
                    }

    GraphDatabaseCsv(database, file, localization)