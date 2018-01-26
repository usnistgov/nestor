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

    def __init__(self, problem=None, solution=None, cause=None, effects=None,
                 part_in_process=None, necessary_part=None, machine_down=None,

                 date_machine_up=None, date_machine_down=None,
                 date_maintenance_work_order_issue=None, date_maintenance_work_order_close=None,
                 date_maintenance_technician_arrives=None,
                 date_problem_found=None, date_problem_solved=None,
                 date_part_ordered=None, date_maintenance_technician_begin_repair_problem=None,
                 ):
        self.label_issue = NodeIssue.LABEL_ISSUE.value
        self.property_problem = NodeIssue.PROPERTY_DESCRIPTION_PROBLEM.value
        self.property_solution = NodeIssue.PROPERTY_DESCRIPTION_SOLUTION.value
        self.property_cause = NodeIssue.PROPERTY_DESCRIPTION_CAUSE.value
        self.property_effects = NodeIssue.PROPERTY_DESCRIPTION_EFFECT.value
        self.property_machine_down = NodeIssue.PROPERTY_MACHINE_DOWN.value

        self.property_part_in_process = NodeIssue.PROPERTY_PART_PROCESS.value
        self.property_necessary_part = NodeIssue.PROPERTY_NECESSARY_PART.value

        self.property_date_machine_down = NodeIssue.PROPERTY_DATE_MACHINE_DOWN.value
        self.property_date_machine_up = NodeIssue.PROPERTY_DATE_MACHINE_UP.value
        self.property_date_mwo_issue = NodeIssue.PROPERTY_DATE_MAINTENANCE_WORK_ORDER_ISSUE.value
        self.property_date_mwo_close = NodeIssue.PROPERTY_DATE_MAINTENANCE_WORK_ORDER_CLOSE.value
        self.property_date_mt_arrives = NodeIssue.PROPERTY_DATE_TECHNICIAN_ARRIVE.value
        self.property_date_problem_found = NodeIssue.PROPERTY_DATE_PROBLEM_FOUND.value
        self.property_date_problem_solved = NodeIssue.PROPERTY_DATE_PROBLEM_SOLVE.value
        self.property_date_part_ordered = NodeIssue.PROPERTY_DATE_PART_ORDER.value
        self.property_date_mt_begin_repaire_problem = NodeIssue.PROPERTY_DATE_MAINTENANCE_TECHNICIAN_REPAIR_PROBLEM.value

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
        if problem is "" or problem is None:
            self.problem = None
        else:
            self.problem = problem

    def _get_solution(self):
        return self.solution

    def _set_solution(self, solution):
        if solution is "" or solution is None:
            self.solution = None
        else:
            self.solution = solution

    def _get_cause(self):
        return self.cause

    def _set_cause(self, cause):
        if cause is "" or cause is None:
            self.cause = None
        else:
            self.cause = cause

    def _get_effects(self):
        return self.effects

    def _set_effects(self, effects):
        if effects is "" is None:
            self.effects = None
        else:
            self.effects = effects

    def _get_part_in_process(self):
        return self.part_in_process

    def _set_part_in_process(self, part_in_process):
        if part_in_process is "" or part_in_process is None:
            self.part_in_process = None
        else:
            try:
                self.part_in_process = part_in_process.lower()
            except AttributeError:
                self.part_in_process = [p.lower() for p in part_in_process]

    def _get_necessary_part(self):
        return self.necessary_part

    def _set_necessary_part(self, necessary_part):
        if necessary_part is "" or necessary_part is None:
            self.necessary_part = None
        else:
            try:
                self.necessary_part = necessary_part.lower()
            except AttributeError:
                self.necessary_part = [n.lower() for n in necessary_part]

    def _get_machine_down(self):
        return self.machine_down

    def _set_machine_down(self, machine_down):
        if machine_down == "y" or machine_down == "yes" or machine_down == "true" or machine_down == "t" or machine_down == "1":
            self.machine_down = True
        elif machine_down == "n" or machine_down == "no" or machine_down == "false" or machine_down == "f" or machine_down == "0":
            self.machine_down = False
        elif machine_down == "_":
            self.machine_down = "_"
        else:
            self.machine_down = None

            ############################  DATE ############################
        # TODO Dates make problem, because there is too much difference between the csv

    def _get_date_machine_down(self):
        return self.date_machine_down

    def _set_date_machine_down(self, date_machine_down):
        if date_machine_down is not None:
            if isinstance(date_machine_down, datetime):
                self.date_machine_down = date_machine_down
            elif date_machine_down == "_":
                self.date_machine_down = "_"
            else:
                self.date_machine_down = isoStringToDate(date_machine_down)
        else:
            self.date_machine_down = None

    def _get_date_machine_up(self):
        return self.date_machine_up

    def _set_date_machine_up(self, date_machine_up):
        if date_machine_up is not None:
            if isinstance(date_machine_up, datetime):
                self.date_machine_up = date_machine_up
            elif date_machine_up == "_":
                self.date_machine_up = "_"
            else:
                self.date_machine_up = isoStringToDate(date_machine_up)
        else:
            self.date_machine_up = None
        #

    def _get_date_maintenance_work_order_close(self):
        return self.date_maintenance_work_order_close

    def _set_date_maintenance_work_order_close(self, date_maintenance_work_order_close):
        if date_maintenance_work_order_close is not None:
            if isinstance(date_maintenance_work_order_close, datetime):
                self.date_maintenance_work_order_close = date_maintenance_work_order_close
            elif date_maintenance_work_order_close == "_":
                self.date_maintenance_work_order_close = "_"
            else:
                self.date_maintenance_work_order_close = isoStringToDate(date_maintenance_work_order_close)
        else:
            self.date_maintenance_work_order_close = None

    def _get_date_maintenance_work_order_issue(self):
        return self.date_maintenance_work_order_issue

    def _set_date_maintenance_work_order_issue(self, date_maintenance_work_order_issue):
        if date_maintenance_work_order_issue is not None:
            if isinstance(date_maintenance_work_order_issue, datetime):
                self.date_maintenance_work_order_issue = date_maintenance_work_order_issue
            elif date_maintenance_work_order_issue == "_":
                self.date_maintenance_work_order_issue = "_"
            else:
                self.date_maintenance_work_order_issue = isoStringToDate(date_maintenance_work_order_issue)
        else:
            self.date_maintenance_work_order_issue = None
        #

    def _get_date_maintenance_technician_arrives(self, ):
        return self.date_maintenance_technician_arrives

    def _set_date_maintenance_technician_arrives(self, date_maintenance_technician_arrives):
        if date_maintenance_technician_arrives is not None:
            if isinstance(date_maintenance_technician_arrives, datetime):
                self.date_maintenance_technician_arrives = date_maintenance_technician_arrives
            elif date_maintenance_technician_arrives == "_":
                self.date_maintenance_technician_arrives = "_"
            else:
                self.date_maintenance_technician_arrives = isoStringToDate(date_maintenance_technician_arrives)
        else:
            self.date_maintenance_technician_arrives = None
        #

    def _get_date_problem_solved(self):
        return self.date_problem_solved

    def _set_date_problem_solved(self, date_problem_solved):
        if date_problem_solved is not None:
            if isinstance(date_problem_solved, datetime):
                self.date_problem_solved = date_problem_solved
            elif date_problem_solved == "_":
                self.date_problem_solved = "_"
            else:
                self.date_problem_solved = isoStringToDate(date_problem_solved)
        else:
            self.date_problem_solved = None

    def _get_date_problem_found(self):
        return self.date_problem_found

    def _set_date_problem_found(self, date_problem_found):
        if date_problem_found is not None:
            if isinstance(date_problem_found, datetime):
                self.date_problem_found = date_problem_found
            elif date_problem_found == "_":
                self.date_problem_found = "_"
            else:
                self.date_problem_found = isoStringToDate(date_problem_found)
        else:
            self.date_problem_found = None
        #

    def _get_date_part_ordered(self):
        return self.date_part_ordered

    def _set_date_part_ordered(self, date_part_ordered):
        if date_part_ordered is not None:
            if isinstance(date_part_ordered, datetime):
                self.date_part_ordered = date_part_ordered
            elif date_part_ordered == "_":
                self.date_part_ordered = "_"
            else:
                self.date_part_ordered = isoStringToDate(date_part_ordered)
        else:
            self.date_part_ordered = None

    def _get_date_maintenance_technician_begin_repair_problem(self):
        return self.date_maintenance_technician_begin_repair_problem

    def _set_date_maintenance_technician_begin_repair_problem(self, date_maintenance_technician_begin_repair_problem):
        if date_maintenance_technician_begin_repair_problem is not None:
            if isinstance(date_maintenance_technician_begin_repair_problem, datetime):
                self.date_maintenance_technician_begin_repair_problem = date_maintenance_technician_begin_repair_problem
            elif date_maintenance_technician_begin_repair_problem == "_":
                self.date_maintenance_technician_begin_repair_problem = "_"
            else:
                self.date_maintenance_technician_begin_repair_problem = isoStringToDate(
                    date_maintenance_technician_begin_repair_problem)
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
        return f"OBJECT: {type(self)}\n\t" \
               f"problem: {self.problem} \n\tsolution: {self.solution} \n\t" \
               f"cause: {self.cause} \n\teffects: {self.effects} \n\t" \
               f"part_in_process: {self.part_in_process} \n\t|| necessary_part: {self.necessary_part} \n\t" \
               f"machine_down: {self.down} \n\t" \
               f"date_machine_up: {self.date_machine_up} \n\t|| date_machine_down: {self.date_machine_down} \n\t" \
               f"date_maintenance_work_order_issue: {self.date_maintenance_work_order_issue} \n\t" \
               f"date_maintenance_work_order_close: {self.date_maintenance_work_order_close} \n\t" \
               f"date_maintenance_technician_arrives: {self.date_maintenance_technician_arrives} \n\t" \
               f"date_problem_found: {self.date_problem_found} \n\tdate_problem_solved: {self.date_problem_solved} \n\t" \
               f"date_part_ordered: {self.date_part_ordered} \n\t" \
               f"date_maintenance_technician_begin_repair_problem: {self.date_maintenance_technician_begin_repair_problem} \n\t" \
               f"time_to_repair: {self.time_to_repair} \n\ttime_work_order_completion: {self.time_work_order_completion} \n\t" \
               f"time_to_dispatch: {self.time_to_dispatch} \n\ttime_to_return_to_operation: {self.time_to_return_to_operation} \n\t" \
               f"time_to_issue_work_order: {self.time_to_issue_work_order} \n\ttime_to_travel: {self.time_to_travel} \n\t" \
               f"time_to_solve_problem: {self.time_to_solve_problem} \n\ttime_to_diagnose: {self.time_to_diagnose} \n\t" \
               f"time_to_order: {self.time_to_order} \n\ttime_lead_for_part: {self.time_lead_for_part} \n\t" \
               f"time_to_fix: {self.time_to_fix} \n\ttime_to_turn_on: {self.time_to_turn_on} \n\t"


    def cypher_issue_all(self, variable="issue"):
        query = f'({variable} {self.label_issue}'
        if self.problem or self.solution or self.cause or self.effects or self.part_in_process or self.necessary_part\
                or self.machine_down or self.date_machine_up or self.date_machine_down \
                or self.date_maintenance_work_order_issue or self.date_maintenance_work_order_close\
                or self.date_maintenance_technician_arrives or self.date_problem_found or self.date_problem_solved\
                or self.date_part_ordered or self.date_maintenance_technician_begin_repair_problem is not None :
            query += "{"
            if self.problem is not None:
                query += f'{self.property_problem}:"{self.problem}",'
            if self.solution is not None:
                query += f'{self.property_solution}:"{self.solution}",'
            if self.cause is not None:
                query += f'{self.property_cause}:"{self.cause}",'
            if self.effects is not None:
                query += f'{self.property_effects}:"{self.effects}",'
            if self.part_in_process is not None:
                query += f'{self.property_part_in_process}:"{self.part_in_process}",'
            if self.necessary_part is not None:
                query += f'{self.property_necessary_part}:"{self.necessary_part}",'
            if self.machine_down is not None:
                query += f'{self.property_machine_down}:"{self.machine_down}",'
            if self.date_machine_up is not None:
                query += f'{self.property_date_machine_up}:"{self.date_machine_up}",'
            if self.date_machine_down is not None and self.date_machine_down != "_":
                query += f'{self.property_date_machine_down}:"{self.date_machine_down }",'
            if self.date_maintenance_work_order_issue is not None:
                query += f'{self.property_date_mwo_issue}:"{self.date_maintenance_work_order_issue}",'
            if self.date_maintenance_work_order_close is not None:
                query += f'{self.property_date_mwo_close}:"{self.date_maintenance_work_order_close}",'
            if self.date_maintenance_technician_arrives is not None:
                query += f'{self.property_date_mt_arrives}:"{self.date_maintenance_technician_arrives}",'
            if self.date_problem_found is not None:
                query += f'{self.property_date_problem_found}:"{self.date_problem_found}",'
            if self.date_problem_solved is not None:
                query += f'{self.property_date_problem_solved}:"{self.date_problem_solved}",'
            if self.date_part_ordered is not None:
                query += f'{self.property_date_part_ordered}:"{self.date_part_ordered}",'
            if self.date_maintenance_technician_begin_repair_problem is not None:
                query += f'{self.property_date_mt_begin_repaire_problem}:"{self.date_maintenance_technician_begin_repair_problem}",'
            query = query[:-1] + "}"
        return query + ")"

    def cypher_create_issue_node(self, variable="issue"):
        if self.problem and self.solution is None:
            return ""
        query = f'CREATE {self.cypher_issue_all(variable)}'
        return query

    def cypher_kpi(self, variable ="issue"):

        match = f'MATCH (issue {NodeIssue.LABEL_ISSUE.value})'
        where, res = self.cypher_where_properties(variable= variable)

        return match, " OR ".join(where), res

    def cypher_where_properties(self, variable = "issue"):
        where = []
        res = []
        if self.problem is not None :
            if self.problem != "_":
                for p in self.problem:
                    where.append(f'{variable}.{self.property_problem} = "{p}"')
            else:
                res.append(f'{variable}.{self.property_problem}')
        if self.solution is not None :
            if self.solution != "_":
                for s in self.solution:
                    where.append(f'{variable}.{self.property_solution} = "{s}"')
            else:
                res.append(f'{variable}.{self.property_solution}')
        if self.cause is not None :
            if self.cause != "_":
                for c in self.cause:
                    where.append(f'{variable}.{self.property_cause} = "{c}"')
            else:
                res.append(f'{variable}.{self.property_cause}')
        if self.effects is not None:
            if self.effects != "_":
                for e in self.effects:
                    where.append(f'{variable}.{self.property_effects} = "{e}"')
            else:
                res.append(f'{variable}.{self.property_effects}')
        if self.part_in_process is not None:
            if self.part_in_process != "_":
                for p in self.effects:
                    where.append(f'{variable}.{self.property_part_in_process} = "{p}"')
            else:
                res.append(f'{variable}.{self.property_part_in_process}')
        if self.necessary_part is not None:
            if self.necessary_part != "_":
                for n in self.effects:
                    where.append(f'{variable}.{self.property_necessary_part} = "{n}"')
            else:
                res.append(f'{variable}.{self.property_necessary_part}')
        if self.machine_down is not None:
            if self.machine_down != "_":
                where.append(f'{variable}.{self.property_machine_down} = {self.machine_down}')
            else:
                res.append(f'{variable}.{self.property_machine_down}')

        if self.date_machine_down is not None:
            if self.date_machine_down != "_":
                for d in self.date_machine_down:
                    where.append(f'{variable}.{self.date_machine_down} = "{d}"')
            else:
                res.append(f'{variable}.{self.property_date_machine_down}')
        if self.date_machine_up is not None:
            if self.date_machine_up != "_":
                for d in self.date_machine_up:
                    where.append(f'{variable}.{self.date_machine_up} = "{d}"')
            else:
                res.append(f'{variable}.{self.property_date_machine_up}')
        if self.date_maintenance_work_order_close is not None:
            if self.date_maintenance_work_order_close != "_":
                for d in self.date_maintenance_work_order_close:
                    where.append(f'{variable}.{self.property_date_mwo_close} = "{d}"')
            else:
                res.append(f'{variable}.{self.property_date_mwo_close}')
        if self.date_maintenance_work_order_issue is not None:
            if self.date_maintenance_work_order_issue != "_":
                for d in self.date_maintenance_work_order_issue:
                    where.append(f'{variable}.{self.property_date_mwo_issue} = "{d}"')
            else:
                res.append(f'{variable}.{self.property_date_mwo_issue}')
        if self.date_maintenance_technician_arrives is not None:
            if self.date_maintenance_technician_arrives != "_":
                for d in self.date_maintenance_technician_arrives:
                    where.append(f'{variable}.{self.property_date_mt_arrives} = "{d}"')
            else:
                res.append(f'{variable}.{self.property_date_mt_arrives}')
        if self.date_problem_solved is not None:
            if self.date_problem_solved != "_":
                for d in self.date_problem_solved:
                    where.append(f'{variable}.{self.date_problem_solved} = "{d}"')
            else:
                res.append(f'{variable}.{self.property_date_problem_solved}')
        if self.date_problem_found is not None:
            if self.date_problem_found != "_":
                for d in self.date_problem_found:
                    where.append(f'{variable}.{self.date_problem_found} = "{d}"')
            else:
                res.append(f'{variable}.{self.property_date_problem_found}')
        if self.date_part_ordered is not None:
            if self.date_part_ordered != "_":
                for d in self.date_part_ordered:
                    where.append(f'{variable}.{self.date_part_ordered} = "{d}"')
            else:
                res.append(f'{variable}.{self.property_date_part_ordered}')
        if self.date_maintenance_technician_begin_repair_problem is not None:
            if self.date_maintenance_technician_begin_repair_problem != "_":
                for d in self.date_maintenance_technician_begin_repair_problem:
                    where.append(f'{variable}.{self.property_date_mt_begin_repaire_problem} = "{d}"')
            else:
                res.append(f'{variable}.{self.property_date_mt_begin_repaire_problem}')

        return where, res