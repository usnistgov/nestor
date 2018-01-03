from datetime import datetime

from Program.Database.Database_Properties import NodeIssue
from Program.Others.MyDate import isoStringToDate

"""
EVERY DATE HAS TO BE AN INSTANCE OF DATETIME
OR IT HAS TO BE A STRING WITH THE FOLLOWING FORMAT : YYYY-MM-DDThh:mm (it can be even more : YYYY-MM-DDThh:mm:ss:s:TZD)
Or it is not going to store it

"""


class Issue:
    """
    The issue represente the information of a Maintenance Work Order (MWO)
    ISSUE are extracted from a CSV files and store in a Neo4J database using the my methods by create CYPHER queries
    It needs at least a problem_description and a solution_description

    All the time parameters are calculated based on the date (cannot be instantiated)
    Times are not store in the database

    In the database, we create an ISSUE for every new MWO

    PARAMETERS:
        Description:
            problem     --  String what is the problem
            solution    --  String how was it solve
            cause       --  String what was the cause of it
            effects     --  String what was the effect
        Other:
            machine_down    --  Boolean is the machine still working
            part_in_process --  String what was the part created during the MWO
            necessary_part  --  String wich part do you need to solve the MWO
        Date:
            date_machine_down                                   --  DateTime when does the MACHINE start to fail
            date_machine_up                                     --  DateTime when does the MACHINE start to work
            date_maintenance_work_order_close                   --  DateTime when does the MWO is closed
            date_maintenance_work_order_issue                   --  DateTime when does the MWO is created
            date_maintenance_technician_arrives                 --  DateTime when does the TECHNICIAN arrives on the MACHINE
            date_problem_solved                                 --  DateTime when does the problem is solved by the TECHNICIAN
            date_problem_found                                  --  DateTime when does the problem is found by the TECHNICIAN
            date_part_ordered                                   --  DateTime when does the neccesary_part is ordered
            date_maintenance_technician_begin_repair_problem    --  DateTime when does the TECHNICIAN start to repaire the MACHINE
        Time:
            time_to_repair                  --  TimeDelta from date_machine_down to date_machine_up
            time_work_order_completion      --  TimeDelta from date_maintenance_work_order_close to date_maintenance_work_order_issue
            time_to_dispatch                --  TimeDelta from date_maintenance_technician_arrives to date_machine_down
            time_to_return_to_operation     --  TimeDelta from date_machine_up to date_maintenance_technician_arrives
            time_to_issue_work_order        --  TimeDelta from date_maintenance_work_order_issue to date_machine_down
            time_to_travel                  --  TimeDelta from date_maintenance_technician_arrives to date_maintenance_work_order_issue
            time_to_solve_problem           --  TimeDelta from date_problem_solved to date_maintenance_technician_arrives
            time_to_diagnose                --  TimeDelta from date_problem_found to date_maintenance_technician_arrives
            time_to_order                   --  TimeDelta from date_part_ordered to date_problem_found
            time_lead_for_part              --  TimeDelta from date_maintenance_technician_begin_repair_problem to date_part_ordered
            time_to_fix                     --  TimeDelta from date_problem_solved to date_maintenance_technician_begin_repair_problem
            time_to_turn_on                 --  TimeDelta from date_machine_up to date_problem_solved


    METHODS:
        create_all_time     --  Used to set all the time possible of an ISSUE
        toCypher            --  DEPRECIATE (use toCypherDescription and toCypherUpdate instead) Used to represent a Cypher query to Create a new ISSUE
        toCypherDescription --  Used to represent a CYPHER query to represent an ISSUE in the database using the problem and solution
        toCypherUpdate      --  Used to update the information of the node ISSUE in the database
                            If in the database a HUMAN already have my name, It updated it and add all other information possible
    """

    def __init__(self, problem, solution, cause=None, effects=None,
                 part_in_process=None, necessary_part=None, machine_down= None,

                 date_machine_up=None, date_machine_down=None,
                 date_maintenance_work_order_issue=None, date_maintenance_work_order_close=None,
                 date_maintenance_technician_arrives=None,
                 date_problem_found=None, date_problem_solved=None,
                 date_part_ordered=None, date_maintenance_technician_begin_repair_problem=None,
                ):

        self._set_problem(problem)
        self._set_solution(solution)
        self._set_cause(cause)
        self._set_effects(effects)
        self._set_machine_down(machine_down)


        self._set_part_in_process(part_in_process)
        self._set_necessary_part(necessary_part)

        self._set_date_machine_down(date_machine_down)
        self._set_date_machine_up(date_machine_up)

        self._set_date_maintenance_work_order_close(date_maintenance_work_order_close)
        self._set_date_maintenance_work_order_issue(date_maintenance_work_order_issue)

        self._set_date_maintenance_technician_arrives(date_maintenance_technician_arrives)

        self._set_date_problem_solved(date_problem_solved)
        self._set_date_problem_found(date_problem_found)

        self._set_date_part_ordered(date_part_ordered)
        self._set_date_maintenance_technician_begin_repair_problem(date_maintenance_technician_begin_repair_problem)

        self.create_all_time()

    def _get_problem(self):
        return self.problem

    def _set_problem(self, problem):
        if problem is "":
            problem = "unknown"
        self.problem = problem

    def _get_solution(self):
        return self.solution

    def _set_solution(self, solution):
        if solution is "":
            solution = "unknown"
        self.solution = solution

    def _get_cause(self):
        return self.cause

    def _set_cause(self, cause):
        if cause is "":
            cause = None
        self.cause = cause

    def _get_effects(self):
        return self.effects

    def _set_effects(self, effects):
        if effects is "":
            effects = None
        self.effects = effects

    def _get_part_in_process(self):
        return self.part_in_process

    def _set_part_in_process(self, part_in_process):
        if part_in_process is "":
            part_in_process = None
        self.part_in_process = part_in_process

    def _get_necessary_part(self):
        return self.necessary_part

    def _set_necessary_part(self, necessary_part):
        if necessary_part is "":
            necessary_part = None
        self.necessary_part = necessary_part

    def _get_machine_down(self):
        return self.machine_down

    def _set_machine_down(self, machine_down):
        #TODO when THURSTON cleaned everything, change it

        if machine_down == "y" or machine_down == "yes" or machine_down == "true" or machine_down == "t" or machine_down == "1":
            self.machine_down = True
        elif machine_down == "n" or machine_down == "no" or machine_down == "false" or machine_down == "f" or machine_down == "0":
            self.machine_down = False
        else:
            self.machine_down = None


        ############################  DATE ############################

    def _get_date_machine_down(self):
        return self.date_machine_down

    def _set_date_machine_down(self, date_machine_down):
        if isinstance(date_machine_down, datetime):
            self.date_machine_down = date_machine_down
        elif date_machine_down is not None:
            self.date_machine_down = isoStringToDate(date_machine_down)
        else:
            self.date_machine_down = None

    def _get_date_machine_up(self):
        return self.date_machine_up

    def _set_date_machine_up(self, date_machine_up):
        if isinstance(date_machine_up, datetime):
            self.date_machine_up = date_machine_up
        elif date_machine_up is not None:
            self.date_machine_up = isoStringToDate(date_machine_up)
        else:
            self.date_machine_up = None
#

    def _get_date_maintenance_work_order_close(self):
        return self.date_maintenance_work_order_close

    def _set_date_maintenance_work_order_close(self, date_maintenance_work_order_close):
        if isinstance(date_maintenance_work_order_close, datetime):
            self.date_maintenance_work_order_close = date_maintenance_work_order_close
        elif date_maintenance_work_order_close is not None:
            self.date_maintenance_work_order_close = isoStringToDate(date_maintenance_work_order_close)
        else:
            self.date_maintenance_work_order_close = None

    def _get_date_maintenance_work_order_issue(self):
        return self.date_maintenance_work_order_issue

    def _set_date_maintenance_work_order_issue(self, date_maintenance_work_order_issue):
        if isinstance(date_maintenance_work_order_issue, datetime):
            self.date_maintenance_work_order_issue = date_maintenance_work_order_issue
        elif date_maintenance_work_order_issue is not None:
            self.date_maintenance_work_order_issue = isoStringToDate(date_maintenance_work_order_issue)
        else:
            self.date_maintenance_work_order_issue = None
#

    def _get_date_maintenance_technician_arrives(self,):
        return self.date_maintenance_technician_arrives

    def _set_date_maintenance_technician_arrives(self, date_maintenance_technician_arrives):
        if isinstance(date_maintenance_technician_arrives, datetime):
            self.date_maintenance_technician_arrives = date_maintenance_technician_arrives
        elif date_maintenance_technician_arrives is not None:
            self.date_maintenance_technician_arrives = isoStringToDate(date_maintenance_technician_arrives)
        else:
            self.date_maintenance_technician_arrives = None
#

    def _get_date_problem_solved(self):
        return self.date_problem_solved

    def _set_date_problem_solved(self, date_problem_solved):
        if isinstance(date_problem_solved, datetime):
            self.date_problem_solved = date_problem_solved
        elif date_problem_solved is not None:
            self.date_problem_solved = isoStringToDate(date_problem_solved)
        else:
            self.date_problem_solved = None

    def _get_date_problem_found(self):
        return self.date_problem_found

    def _set_date_problem_found(self, date_problem_found):
        if isinstance(date_problem_found, datetime):
            self.date_problem_found = date_problem_found
        elif date_problem_found is not None:
            self.date_problem_found = isoStringToDate(date_problem_found)
        else:
            self.date_problem_found = None
#

    def _get_date_part_ordered(self):
        return self.date_part_ordered

    def _set_date_part_ordered(self,date_part_ordered):
        if isinstance(date_part_ordered, datetime):
            self.date_part_ordered = date_part_ordered
        elif date_part_ordered is not None:
            self.date_part_ordered = isoStringToDate(date_part_ordered)
        else:
            self.date_part_ordered = None

    def _get_date_maintenance_technician_begin_repair_problem(self):
        return self.date_maintenance_technician_begin_repair_problem

    def _set_date_maintenance_technician_begin_repair_problem(self, date_maintenance_technician_begin_repair_problem):
        if isinstance(date_maintenance_technician_begin_repair_problem, datetime):
            self.date_maintenance_technician_begin_repair_problem = date_maintenance_technician_begin_repair_problem
        elif date_maintenance_technician_begin_repair_problem is not None:
            self.date_maintenance_technician_begin_repair_problem = isoStringToDate(date_maintenance_technician_begin_repair_problem)
        else:
            self.date_maintenance_technician_begin_repair_problem = None

############################  TIME ############################

    def _get_time_to_repair(self):
        return self.time_to_repair

    def _set_time_to_repair(self):
        try:
            self.time_to_repair = self.date_machine_up - self.date_machine_down
        except TypeError:
            self.time_to_repair = None

    def _get_time_work_order_completion(self):
        return self.time_work_order_completion

    def _set_time_work_order_completion(self):
        try:
            self.time_work_order_completion = self.date_maintenance_work_order_close - self.date_maintenance_work_order_issue
        except TypeError:
            self.time_work_order_completion = None

    def _get_time_to_dispatch(self):
        return self.time_to_dispatch

    def _set_time_to_dispatch(self):
        try:
            self.time_to_dispatch = self.date_maintenance_technician_arrives - self.date_machine_down
        except TypeError:
            self.time_to_dispatch = None

    def _get_time_to_return_to_operation(self):
        return self.time_to_return_to_operation

    def _set_time_to_return_to_operation(self):
        try:
            self.time_to_return_to_operation = self.date_machine_up - self.date_maintenance_technician_arrives
        except TypeError:
            self.time_to_return_to_operation = None

    def _get_time_to_issue_work_order(self):
        return self.time_to_issue_work_order

    def _set_time_to_issue_work_order(self):
        try:
            self.time_to_issue_work_order = self.date_maintenance_work_order_issue - self.date_machine_down
        except TypeError:
            self.time_to_issue_work_order = None

    def _get_time_to_travel(self):
        return self.time_to_travel

    def _set_time_to_travel(self):
        try:
            self.time_to_travel = self.date_maintenance_technician_arrives - self.date_maintenance_work_order_issue
        except TypeError:
            self.time_to_travel = None

    def _get_time_to_solve_problem(self):
        return self.time_to_solve_problem

    def _set_time_to_solve_problem(self):
        try:
            self.time_to_solve_problem = self.date_problem_solved - self.date_maintenance_technician_arrives
        except TypeError:
            self.time_to_solve_problem = None

    def _get_time_to_diagnose(self):
        return self.time_to_diagnose

    def _set_time_to_diagnose(self):
        try:
            self.time_to_diagnose = self.date_problem_found - self.date_maintenance_technician_arrives
        except TypeError:
            self.time_to_diagnose = None

    def _get_time_to_order(self):
        return self.time_to_order

    def _set_time_to_order(self):
        try:
            self.time_to_order = self.date_part_ordered - self.date_problem_found
        except TypeError:
            self.time_to_order = None

    def _get_time_lead_for_part(self):
        return self.time_lead_for_part

    def _set_time_lead_for_part(self):
        try:
            self.time_lead_for_part = self.date_maintenance_technician_begin_repair_problem - self.date_part_ordered
        except TypeError:
            self.time_lead_for_part = None

    def _get_time_to_fix(self):
        return self.time_to_fix

    def _set_time_to_fix(self):
        try:
            self.time_to_fix = self.date_problem_solved - self.date_maintenance_technician_begin_repair_problem
        except TypeError:
            self.time_to_fix = None

    def _get_time_to_turn_on(self):
        return self.time_to_turn_on

    def _set_time_to_turn_on(self):
        try:
            self.time_to_turn_on = self.date_machine_up - self.date_problem_solved
        except TypeError:
            self.time_to_turn_on = None

#

    def create_all_time(self):
        """
        Set all the time based on all the date in the object
        """
        self._set_time_to_repair()
        self._set_time_work_order_completion()
        self._set_time_to_dispatch()
        self._set_time_to_return_to_operation()
        self._set_time_to_issue_work_order()
        self._set_time_to_travel()
        self._set_time_to_solve_problem()
        self._set_time_to_diagnose()
        self._set_time_to_order()
        self._set_time_lead_for_part()
        self._set_time_to_fix()
        self._set_time_to_turn_on()


    def __str__(self):
        return "OBJECT: %s --> problem: %s \n|| solution: %s \n" \
               "|| cause: %s \n|| effects: %s \n" \
               "|| part_in_process: %s \n|| necessary_part: %s \n" \
               "|| machine_down: %s \n"\
               "|| date_machine_up: %s \n|| date_machine_down: %s \n" \
               "|| date_maintenance_work_order_issue: %s \n|| date_maintenance_work_order_close: %s \n" \
               "|| date_maintenance_technician_arrives: %s \n" \
               "|| date_problem_found: %s \n|| date_problem_solved: %s \n" \
               "|| date_part_ordered: %s \n|| date_maintenance_technician_begin_repair_problem: %s \n" \
               "|| time_to_repair: %s \n|| time_work_order_completion: %s \n" \
               "|| time_to_dispatch: %s \n|| time_to_return_to_operation: %s \n" \
               "|| time_to_issue_work_order: %s \n|| time_to_travel: %s \n" \
               "|| time_to_solve_problem: %s \n|| time_to_diagnose: %s \n" \
               "|| time_to_order: %s \n|| time_lead_for_part: %s \n" \
               "|| time_to_fix: %s \n|| time_to_turn_on: %s \n"%\
               (type(self), self.problem, self.solution,
                self.cause, self.effects,
                self.part_in_process, self.necessary_part,
                self.down,
                self.date_machine_up, self.date_machine_down,
                self.date_maintenance_work_order_issue, self.date_maintenance_work_order_close,
                self.date_maintenance_technician_arrives,
                self.date_problem_found, self.date_problem_solved,
                self.date_part_ordered, self.date_maintenance_technician_begin_repair_problem,
                self.time_to_repair, self.time_work_order_completion, self.time_to_dispatch,
                self.time_to_return_to_operation, self.time_to_issue_work_order, self.time_to_travel,
                self.time_to_solve_problem, self.time_to_diagnose, self.time_to_order, self.time_lead_for_part,
                self.time_to_fix, self.time_to_turn_on)

    def toCypher(self, variable):
        """
        DEPRECIATE (use toCypherDescription and toCypherUpdate instead)
        Used to create a Cypher query node corresponding to an ISSUE

        The problem is that it create a new ISSUE even if one already has the same problem and solution in tha database
        but if the new one has more parameters

        :param variable: a string to define the variable of the node in CYPHER. It is used to reuse the given node ISSUE
        :return: a String representing a Cypher query corresponding to a full ISSUE

        """
        if self.problem is None or self.solution is None:
            return ""

        query = '(%s %s {%s: "%s"' %\
                (variable, NodeIssue.LABEL_ISSUE.value, NodeIssue.PROPERTY_DESCRIPTION_PROBLEM.value, self.problem)
        query += ', %s: "%s"'%\
                (NodeIssue.PROPERTY_DESCRIPTION_SOLUTION.value, self.solution)
        if self.cause is not None:
            query += ', %s: "%s"' % \
                (NodeIssue.PROPERTY_DESCRIPTION_CAUSE.value, self.cause)
        if self.effects is not None:
            query += ', %s: "%s"' % \
                (NodeIssue.PROPERTY_DESCRIPTION_EFFECT.value, self.effects)
        if self.part_in_process is not None:
            query += ', %s: "%s"' % \
                (NodeIssue.PROPERTY_PART_PROCESS.value, self.part_in_process)
        if self.necessary_part is not None:
            query += ', %s: "%s"' % \
                (NodeIssue.PROPERTY_NECESSARY_PART.value, self.necessary_part)
        if self.machine_down is not None:
            query+= ', %s: %s'%\
                (NodeIssue.PROPERTY_MACHINE_DOWN.value, self.machine_down)
        if self.date_machine_down is not None:
            query += ', %s: "%s"' % \
                (NodeIssue.PROPERTY_DATE_MACHINE_DOWN.value, self.date_machine_down.isoformat())
        if self.date_machine_up is not None:
            query += ', %s: "%s"' % \
                (NodeIssue.PROPERTY_DATE_MACHINE_UP.value, self.date_machine_up.isoformat())
        if self.date_maintenance_work_order_issue is not None:
            query += ', %s: "%s"' % \
                (NodeIssue.PROPERTY_DATE_MAINTENANCE_WORK_ORDER_ISSUE.value, self.date_maintenance_work_order_issue.isoformat())
        if self.date_maintenance_work_order_close is not None:
            query += ', %s: "%s"' % \
                (NodeIssue.PROPERTY_DATE_MAINTENANCE_WORK_ORDER_CLOSE.value, self.date_maintenance_work_order_close.isoformat())
        if self.date_maintenance_technician_arrives is not None:
            query += ', %s: "%s"' % \
                (NodeIssue.PROPERTY_DATE_TECHNICIAN_ARRIVE.value, self.date_maintenance_technician_arrives.isoformat())
        if self.date_problem_found is not None:
            query += ', %s: "%s"' % \
                (NodeIssue.PROPERTY_DATE_PROBLEM_FOUND.value, self.date_problem_found.isoformat())
        if self.date_problem_solved is not None:
            query += ', %s: "%s"' % \
                (NodeIssue.PROPERTY_DATE_PROBLEM_SOLVE.value, self.date_problem_solved.isoformat())
        if self.date_part_ordered is not None:
            query += ', %s: "%s"' % \
                (NodeIssue.PROPERTY_DATE_PART_ORDER.value, self.date_part_ordered.isoformat())
        if self.date_maintenance_technician_begin_repair_problem is not None:
            query += ', %s: "%s"' % \
                (NodeIssue.PROPERTY_DATE_MAINTENANCE_TECHNICIAN_REPAIR_PROBLEM.value, self.date_maintenance_technician_begin_repair_problem.isoformat())
        query += "})"
        return query

    def toCypherDescription(self, variable):
        """
        Used to create a CYPHER query corresponding to a ISSUE only using the problem and solution

        :param variable: a string to define the variable of the node in CYPHER. It is used to reuse name the given node ISSUE
        :return: a String representing a Cypher query to corresponding to a ISSUE with only the problem and solution
        """
        if self.problem is None and self.solution is None:
            return ""
        query = '(%s %s {%s: "%s"' % \
                (variable, NodeIssue.LABEL_ISSUE.value, NodeIssue.PROPERTY_DESCRIPTION_PROBLEM.value, self.problem)
        query += ', %s: "%s"})' % \
                 (NodeIssue.PROPERTY_DESCRIPTION_SOLUTION.value, self.solution)
        return query

    def toCypherUpdate(self, variable):
        """
        Used to complete the description of the node ISSUS using all the other description

        :param variable: a string to define the variable of the node in CYPHER.
                        The variable has to link with a node ISSUE from your database (use toCypherDescription to find it)
        :return: a CYPHER query to specify a given ISSUE node by adding the other descriptions in the database
        """

        if self.cause is None and self.effects is None and self.part_in_process is None and self.necessary_part is None and self.machine_down is None and self.date_machine_down is None\
                and self.date_machine_up is None and self.date_maintenance_work_order_issue is None and self.date_maintenance_work_order_close is None and self.date_maintenance_technician_arrives is None\
                and self.date_problem_found is None and self.date_problem_solved is None and self.date_part_ordered is None and self.date_maintenance_technician_begin_repair_problem is None:
            return ""
        query = "SET "
        if self.cause is not None:
            query += '%s.%s="%s",' % \
                (variable, NodeIssue.PROPERTY_DESCRIPTION_CAUSE.value, self.cause)
        if self.effects is not None:
            query += '%s.%s="%s",' % \
                (variable, NodeIssue.PROPERTY_DESCRIPTION_EFFECT.value, self.effects)
        if self.part_in_process is not None:
            query += '%s.%s="%s",' % \
                (variable, NodeIssue.PROPERTY_PART_PROCESS.value, self.part_in_process)
        if self.necessary_part is not None:
            query += '%s.%s="%s",' % \
                (variable, NodeIssue.PROPERTY_NECESSARY_PART.value, self.necessary_part)
        if self.machine_down is not None:
            query += '%s.%s=%s,' % \
                (variable, NodeIssue.PROPERTY_MACHINE_DOWN.value, self.machine_down)
        if self.date_machine_down is not None:
            query += '%s.%s="%s",' % \
                (variable, NodeIssue.PROPERTY_DATE_MACHINE_DOWN.value, self.date_machine_down.isoformat())
        if self.date_machine_up is not None:
            query += '%s.%s="%s",' % \
                (variable, NodeIssue.PROPERTY_DATE_MACHINE_UP.value, self.date_machine_up.isoformat())
        if self.date_maintenance_work_order_issue is not None:
            query += '%s.%s="%s",' % \
                (variable, NodeIssue.PROPERTY_DATE_MAINTENANCE_WORK_ORDER_ISSUE.value, self.date_maintenance_work_order_issue.isoformat())
        if self.date_maintenance_work_order_close is not None:
            query += '%s.%s="%s",' % \
                (variable, NodeIssue.PROPERTY_DATE_MAINTENANCE_WORK_ORDER_CLOSE.value, self.date_maintenance_work_order_close.isoformat())
        if self.date_maintenance_technician_arrives is not None:
            query += '%s.%s="%s",' % \
                (variable, NodeIssue.PROPERTY_DATE_TECHNICIAN_ARRIVE.value, self.date_maintenance_technician_arrives.isoformat())
        if self.date_problem_found is not None:
            query += '%s.%s="%s",' % \
                (variable, NodeIssue.PROPERTY_DATE_PROBLEM_FOUND.value, self.date_problem_found.isoformat())
        if self.date_problem_solved is not None:
            query += '%s.%s="%s",' % \
                (variable, NodeIssue.PROPERTY_DATE_PROBLEM_SOLVE.value, self.date_problem_solved.isoformat())
        if self.date_part_ordered is not None:
            query += '%s.%s="%s",' % \
                (variable, NodeIssue.PROPERTY_DATE_PART_ORDER.value, self.date_part_ordered.isoformat())
        if self.date_maintenance_technician_begin_repair_problem is not None:
            query += '%s.%s="%s",' % \
                (variable, NodeIssue.PROPERTY_DATE_MAINTENANCE_TECHNICIAN_REPAIR_PROBLEM.value, self.date_maintenance_technician_begin_repair_problem.isoformat())

        return query[:-1]

"""
    def fromCypher(self, result):
        self._set_problem(result[NodeIssue.PROPERTY_DESCRIPTION_PROBLEM.value])
        self._set_solution(result[NodeIssue.PROPERTY_DESCRIPTION_SOLUTION.value])
        self._set_cause(result[NodeIssue.PROPERTY_DESCRIPTION_CAUSE.value])
        self._set_effects(result[NodeIssue.PROPERTY_DESCRIPTION_EFFECT.value])
        self._set_machine_down(result[NodeIssue.PROPERTY_MACHINE_DOWN.value])

        self._set_part_in_process(result[NodeIssue.PROPERTY_PART_PROCESS.value])
        self._set_necessary_part(result[NodeIssue.PROPERTY_NECESSARY_PART.value])

        self._set_date_machine_down(result[NodeIssue.PROPERTY_DATE_MACHINE_DOWN.value])
        self._set_date_machine_up(result[NodeIssue.PROPERTY_DATE_MACHINE_UP.value])

        self._set_date_maintenance_work_order_close(result[NodeIssue.PROPERTY_DATE_MAINTENANCE_WORK_ORDER_CLOSE.value])
        self._set_date_maintenance_work_order_issue(result[NodeIssue.PROPERTY_DATE_MAINTENANCE_WORK_ORDER_ISSUE.value])

        self._set_date_maintenance_technician_arrives(result[NodeIssue.PROPERTY_DATE_TECHNICIAN_ARRIVE.value])

        self._set_date_problem_solved(result[NodeIssue.PROPERTY_DATE_PROBLEM_SOLVE.value])
        self._set_date_problem_found(result[NodeIssue.PROPERTY_DATE_PROBLEM_FOUND.value])

        self._set_date_part_ordered(result[NodeIssue.PROPERTY_DATE_PART_ORDER.value])
        self._set_date_maintenance_technician_begin_repair_problem(result[NodeIssue.PROPERTY_DATE_MAINTENANCE_TECHNICIAN_REPAIR_PROBLEM.value])

        self.create_all_time()
"""