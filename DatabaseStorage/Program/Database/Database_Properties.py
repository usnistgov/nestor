"""
This file is used to represent the information (LABEL and PROPERTIES) of nodes and edges in the database

And also the value needed as input ny the user to define where is the value in the CSV file

Every class are an enumerate
"""

from enum import Enum

class NodeHuman(Enum):
    """
    Label, Properties and Value information from the node HUMAN
    """
    LABEL_HUMAN = ":HUMAN"
    LABEL_OPERATOR = ":OPERATOR"
    LABEL_TECHNICIAN = ":TECHNICIAN"

    PROPERTY_NAME = "name"
    PROPERTY_SKILLS = "skills"
    PROPERTY_CRAFTS = "crafts"

    VALUE_TECHNICIAN = "technician"
    VALUE_OPERATOR = "operator"
    VALUE_SKILLS = "skills"
    VALUE_CRAFTS = "crafts"

class NodeMachine(Enum):
    """
    Label, Properties and Value information from the node MACHINE
    """
    LABEL_MACHINE = ":MACHINE"
    LABEL_MACHINE_TYPE = ":MACHINE_TYPE"

    PROPERTY_NAME = "name"
    PROPERTY_TYPE = "type"
    PROPERTY_MANUFACTURER = "manufacturer"
    PROPERTY_LOCASION = "locasion"

    VALUE_MACHINE = "machine"
    VALUE_TYPE = "type"
    VALUE_MANUFACTURER = "manufacturer"
    VALUE_LOCASION = "locasion"

class NodeIssue(Enum):
    """
    Label, Properties and Value information from the node ISSUE
    """
    LABEL_ISSUE = ":ISSUE"

    PROPERTY_DESCRIPTION_PROBLEM = "description_of_problem"
    PROPERTY_DESCRIPTION_SOLUTION = "description_of_solution"
    PROPERTY_DESCRIPTION_CAUSE = "description_of_cause"
    PROPERTY_DESCRIPTION_EFFECT = "description_of_effect"
    PROPERTY_MACHINE_DOWN = "machine_down"
    PROPERTY_NECESSARY_PART = "necessary_part"
    PROPERTY_PART_PROCESS = "part_in_process"

    PROPERTY_DATE_MACHINE_DOWN = "date_machine_down"
    PROPERTY_DATE_MACHINE_UP = "date_machine_up"
    PROPERTY_DATE_MAINTENANCE_WORK_ORDER_ISSUE = "date_maintenance_work_order_issue"
    PROPERTY_DATE_MAINTENANCE_WORK_ORDER_CLOSE = "date_maintenance_work_order_close"
    PROPERTY_DATE_TECHNICIAN_ARRIVE = "date_technician_arrive"
    PROPERTY_DATE_PROBLEM_FOUND = "date_problem_found"
    PROPERTY_DATE_PROBLEM_SOLVE = "date_problem_solve"
    PROPERTY_DATE_PART_ORDER = "date_part_order"
    PROPERTY_DATE_MAINTENANCE_TECHNICIAN_REPAIR_PROBLEM = "date_maintenance_technician_repair_problem"
    PROPERTY_TIME_REPAIR = "time_to_repair"
    PROPERTY_TIME_WORK_ORDER_COMPLETION = "time_work_order_completion"
    PROPERTY_TIME_DISPATCH = "time_to_dispatch"
    PROPERTY_TIME_RETURN_OPERATION = "time_to_return_to_operation"
    PROPERTY_TIME_ISSUE_WORK_ORDER = "time_to_issue_work_order"
    PROPERTY_TIME_TRAVEL = "time_to_travel"
    PROPERTY_TIME_SOLVE_PROBLEM = "time_to_solve_problem"
    PROPERTY_TIME_DIAGNOSE = "time_to_diagnose"
    PROPERTY_TIME_ORDER = "time_to_order"
    PROPERTY_TIME_LEAD_PART = "lead_time_for_part"
    PROPERTY_TIME_FIX = "time_to_fix"
    PROPERTY_TIME_TURN_ON = "time_to_turn_on"


    VALUE_DESCRIPTION_PROBLEM = "description_of_problem"
    VALUE_DESCRIPTION_SOLUTION = "description_of_solution"
    VALUE_DESCRIPTION_CAUSE = "description_of_cause"
    VALUE_DESCRIPTION_EFFECT = "description_of_effect"
    VALUE_NECESSARY_PART = "necessary_part"
    VALUE_PART_PROCESS = "part_in_process"
    VALUE_MACHINE_DOWN = "machine_down"

    VALUE_DATE_MACHINE_DOWN = "date_machine_down"
    VALUE_DATE_MACHINE_UP = "date_machine_up"
    VALUE_DATE_MAINTENANCE_WORK_ORDER_ISSUE = "date_maintenance_work_order_issue"
    VALUE_DATE_MAINTENANCE_WORK_ORDER_CLOSE = "date_maintenance_work_order_close"
    VALUE_DATE_TECHNICIAN_ARRIVE = "date_technician_arrive"
    VALUE_DATE_PROBLEM_FOUND = "date_problem_found"
    VALUE_DATE_PROBLEM_SOLVE = "date_problem_solve"
    VALUE_DATE_PART_ORDER = "date_part_order"
    VALUE_DATE_MAINTENANCE_TECHNICIAN_REPAIR_PROBLEM = "date_maintenance_technician_repair_problem"
    VALUE_TIME_REPAIR = "time_to_repair"
    VALUE_TIME_WORK_ORDER_COMPLETION = "time_work_order_completion"
    VALUE_TIME_DISPATCH = "time_to_dispatch"
    VALUE_TIME_RETURN_OPERATION = "time_to_return_to_operation"
    VALUE_TIME_ISSUE_WORK_ORDER = "time_to_issue_work_order"
    VALUE_TIME_TRAVEL = "time_to_travel"
    VALUE_TIME_SOLVE_PROBLEM = "time_to_solve_problem"
    VALUE_TIME_DIAGNOSE = "time_to_diagnose"
    VALUE_TIME_ORDER = "time_to_order"
    VALUE_TIME_LEAD_PART = "lead_time_for_part"
    VALUE_TIME_FIX = "time_to_fix"
    VALUE_TIME_TURN_ON = "time_to_turn_on"



class NodeTag(Enum):
    """
    Label, Properties and Value information from the node TAG
    """
    LABEL_TAG = ":TAG"
    LABEL_ITEM = ":ITEM"
    LABEL_ACTION = ":ACTION"
    LABEL_ACTION_ITEM = ":ACTION_ITEM"
    LABEL_UNKNOWN = ":UNKNOWN"

    PROPERTY_KEYWORD = "keyword"
    PROPERTY_SYNONYMS = "synonyms"
    PROPERTY_PARENTS = "parents"
    PROPERTY_LINKS = "links"

    VALUE_ITEM = "tag_item"
    VALUE_PROBLEM = "tag_problem"
    VALUE_SOLUTION = "tag_solution"
    VALUE_ACTION_ITEM = "tag_action_item"

    VALUE_KEYWORD = "keyword"
    VALUE_SYNONYMS = "synonyms"
    VALUE_PARENTS = "parents"
    VALUE_LINKS = "links"

class LabelEdges(Enum):
    """
    Label, Properties and Value information from the EDGES
    """
    LABEL_PROBLEM = ":PROBLEM"
    LABEL_SOLUTION = ":SOLUTION"
    LABEL_CONTAINS = ":CONTAINS"

    LABEL_REQUESTED = ":REQUESTED_BY"
    LABEL_SOLVE = ":SOLVE_BY"

    LABEL_COVERED = ":COVERED"
    LABEL_ISA = ":IS_A"

