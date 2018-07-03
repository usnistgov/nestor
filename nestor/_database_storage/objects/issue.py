"""
File: issue.py
Name: Sascha MOCCOZET
Organisation:
    Departament of Commerce USA
    National Institute of Standards and Technology - NIST
    Engineering Laboratory - EL
    Systems Integration Division - SID
    Information Modeling and Testing Group - IMTG
    <Insert Project Name>
Description:
    This file contains the object ISSUE

    This object is a container that represent our world (maintenance work order data) but,
    in the database the node label and the properties key can be easily changed in the YAML file DatabaseSchema.YAML
    In the database, only the name of the properties can changed but not the type of data or the number of properties
    (you can have less but not more)

    The idea of the ISSUE is to store all the data that are specific for a given problem
    and are often different for every maintenance work order

"""

from datetime import datetime

from nestor._database_storage.helper import isoStringToDate


class Issue:
    """An ISSUE define every information that refer to the node ISSUE in our database.
    It setup the properties and query to match with every ISSUE in the database
    
    It is instantiate using:
        - problemn: a String or array of string
        - solution: a String or array of string
        - cause: a String or array of string
        - effects: a String or array of string
        - part_in_process: a String or array of string
        - necessary_part: a String or array of string
        - machine_down: a boolean or array of boolean
    
        - date_machine_up: a DateTime or array of DateTime
        - date_machine_down: a DateTime or array of DateTime
        - date_workorder_start: a DateTime or array of DateTime
        - date_workorder_completion: a DateTime or array of DateTime
        - date_maintenance_technician_arrive: a DateTime or array of DateTime
        - date_problem_found: a DateTime or array of DateTime
        - date_problem_solved: a DateTime or array of DateTime
        - date_part_ordered: a DateTime or array of DateTime
        - date_part_received:  a DateTime or array of DateTime
    
        Date needs to be a DateTime type OR a string that respect the ISO format and contains at least
        YYYY-MM-DD up to YYYY-MM-DDTHH:MM seconds and aboce as well as Time Zone Definer are not taking in acount
        See hleper.py - isoStringToDate() function
    
        - databaseInfo: the dictionary that describe the database information (name of properties, and Label)
    
    it also contains some time properties calculated based on the date:
        - time_to_repair : date_machine_down --> date_machine_up
        - time_work_order_completion : date_workorder_start --> date_workorder_completion
        - time_to_dispatch : date_machine_down --> date_maintenance_technician_arrive
        - time_to_return_to_operation : date_maintenance_technician_arrive --> date_machine_up
        - time_to_issue_work_order : date_machine_down --> date_workorder_start
        - time_to_travel : date_workorder_start --> date_maintenance_technician_arrive
        - time_to_solve_problem : date_maintenance_technician_arrive --> date_problem_solve
        - time_to_diagnose : date_maintenance_technician_arrive --> date_problem_found
        - time_to_order : date_problem_found --> date_part_ordered
        - time_lead_for_part : date_part_ordered --> date_part_received
        - time_to_fix : date_part_received --> date_problem_solve
        - time_to_turn_on : date_problem_solve --> date_machine_up
    
    The time information are not store in the database because we can calculate them very fast,
    but it is totaly possible to store it to recude the computation time but increase the size of the database
    
    It contains getter and setter for every properties, it is highly recommend to use the setter
     because it represent the data as a standard way - the way it is store in the database
    It contains a string representation
    It contains a boolean representation

    Parameters
    ----------

    Returns
    -------

    """

    def __init__(self, problem=None, solution=None, cause=None, effects=None,
                 part_in_process=None, necessary_part=None, machine_down=None,

                 date_machine_up=None, date_machine_down=None,
                 date_workorder_start=None, date_workorder_completion=None,
                 date_maintenance_technician_arrive=None,
                 date_problem_found=None, date_problem_solved=None,
                 date_part_ordered=None, date_part_received=None,
                 databaseInfo=None):
        self.databaseInfoIssue = databaseInfo['issue']

        self._set_problem(problem)
        self._set_solution(solution)
        self._set_cause(cause)
        self._set_effects(effects)
        self._set_machine_down(machine_down)

        self._set_part_in_process(part_in_process)
        self._set_necessary_part(necessary_part)

        self._set_date_machine_down(date_machine_down)
        self._set_date_machine_up(date_machine_up)

        self._set_date_workorder_completion(date_workorder_completion)
        self._set_date_workorder_start(date_workorder_start)

        self._set_date_maintenance_technician_arrive(date_maintenance_technician_arrive)

        self._set_date_problem_solve(date_problem_solved)
        self._set_date_problem_found(date_problem_found)

        self._set_date_part_ordered(date_part_ordered)
        self._set_date_part_received(date_part_received)

    def _get_problem(self):
        return self.problem

    def _set_problem(self, problem):
        if isinstance(problem, str):
            self.problem = problem.replace('"', '\\"').lstrip()
        elif isinstance(problem, list):
            self.problem = [p.replace('"','\\"').lstrip() for p in problem]
        else:
            self.problem = None

    def _get_solution(self):
        return self.solution

    def _set_solution(self, solution):
        if isinstance(solution, str) :
            self.solution = solution.replace('"', '\\"').lstrip()
        elif isinstance(solution, list):
            self.solution = [s.replace('"', '\\"').lstrip() for s in solution]
        else:
            self.solution=None

    def _get_cause(self):
        return self.cause

    def _set_cause(self, cause):
        if isinstance(cause, str):
            self.cause = cause.replace('"', '\\"').lstrip()
        elif isinstance(cause, list):
            self.cause = [c.replace('"','\\"').lstrip() for c in cause]
        else:
            self.cause = None


    def _get_effects(self):
        return self.effects

    def _set_effects(self, effects):
        if isinstance(effects, str):
            self.effects = effects.replace('"', '\\"').lstrip()
        elif isinstance(effects, list):
            self.effects = [e.replace('"', '\\"').lstrip() for e in effects]
        else:
            self.effects = None

    def _get_part_in_process(self):
        return self.part_in_process

    def _set_part_in_process(self, part_in_process):
        if isinstance(part_in_process, str):
            self.part_in_process = part_in_process.lower().replace('"','\\"').lstrip()
        elif isinstance(part_in_process, list):
            self.part_in_process = [p.lower().replace('"','\\"').lstrip() for p in part_in_process]
        else:
            self.part_in_process = None

    def _get_necessary_part(self):
        return self.necessary_part

    def _set_necessary_part(self, necessary_part):

        if isinstance(necessary_part, str):
            self.necessary_part = necessary_part.lower().replace('"','\\"').lstrip()
        elif isinstance(necessary_part, list):
            self.necessary_part = [n.lower().replace('"','\\"').lstrip() for n in necessary_part]
        else:
            self.necessary_part = None

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
        if isinstance(date_machine_down, datetime):
            self.date_machine_down = date_machine_down
        elif isinstance(date_machine_down, str):
            self.date_machine_down = isoStringToDate(date_machine_down)
        elif isinstance(date_machine_down, list):
            self.date_machine_down = date_machine_down
        else:
            self.date_machine_down = None

    def _get_date_machine_up(self):
        return self.date_machine_up

    def _set_date_machine_up(self, date_machine_up):
        if isinstance(date_machine_up, datetime):
            self.date_machine_up = date_machine_up
        elif isinstance(date_machine_up, str):
            self.date_machine_up = isoStringToDate(date_machine_up)
        elif isinstance(date_machine_up,list):
            self.date_machine_up = date_machine_up
        else:
            self.date_machine_up = None

    def _get_date_workorder_completion(self):
        return self.date_workorder_completion

    def _set_date_workorder_completion(self, date_workorder_completion):
        if isinstance(date_workorder_completion, datetime):
            self.date_workorder_completion = date_workorder_completion
        elif isinstance(date_workorder_completion, str):
            self.date_workorder_completion = isoStringToDate(date_workorder_completion)
        elif isinstance(date_workorder_completion, list):
            self.date_workorder_completion = date_workorder_completion
        else:
            self.date_workorder_completion = None

    def _get_date_workorder_start(self):
        return self.date_workorder_start

    def _set_date_workorder_start(self, date_workorder_start):
        if isinstance(date_workorder_start, datetime):
            self.date_workorder_start = date_workorder_start
        elif isinstance(date_workorder_start, str):
            self.date_workorder_start = isoStringToDate(date_workorder_start)
        elif isinstance(date_workorder_start, list):
            self.date_workorder_start = date_workorder_start
        else:
            self.date_workorder_start = None

    def _get_date_maintenance_technician_arrive(self, ):
        return self.date_maintenance_technician_arrive

    def _set_date_maintenance_technician_arrive(self, date_maintenance_technician_arrive):
        if isinstance(date_maintenance_technician_arrive, datetime):
            self.date_maintenance_technician_arrive = date_maintenance_technician_arrive
        elif isinstance(date_maintenance_technician_arrive, str):
            self.date_maintenance_technician_arrive = isoStringToDate(date_maintenance_technician_arrive)
        elif isinstance(date_maintenance_technician_arrive, list):
            self.date_maintenance_technician_arrive = date_maintenance_technician_arrive
        else:
            self.date_maintenance_technician_arrive = None

    def _get_date_problem_solve(self):
        return self.date_problem_solve

    def _set_date_problem_solve(self, date_problem_solve):
        if isinstance(date_problem_solve, datetime):
            self.date_problem_solve = date_problem_solve
        elif isinstance(date_problem_solve, str):
            self.date_problem_solve = isoStringToDate(date_problem_solve)
        elif isinstance(date_problem_solve, list):
            self.date_problem_solve = date_problem_solve
        else:
            self.date_problem_solve = None

    def _get_date_problem_found(self):
        return self.date_problem_found

    def _set_date_problem_found(self, date_problem_found):
        if isinstance(date_problem_found, datetime):
            self.date_problem_found = date_problem_found
        elif isinstance(date_problem_found, str):
            self.date_problem_found = isoStringToDate(date_problem_found)
        elif isinstance(date_problem_found, list):
            self.date_problem_found = date_problem_found
        else:
            self.date_problem_found = None

    def _get_date_part_ordered(self):
        return self.date_part_ordered

    def _set_date_part_ordered(self, date_part_ordered):
        if isinstance(date_part_ordered, datetime):
            self.date_part_ordered = date_part_ordered
        elif isinstance(date_part_ordered, str):
            self.date_part_ordered = isoStringToDate(date_part_ordered)
        elif isinstance(date_part_ordered, list):
            self.date_part_ordered = date_part_ordered
        else:
            self.date_part_ordered = None

    def _get_date_part_received(self):
        return self.date_part_received

    def _set_date_part_received(self, date_part_received):
        if isinstance(date_part_received, datetime):
            self.date_part_received = date_part_received
        elif isinstance(date_part_received, str):
            self.date_part_received = isoStringToDate(date_part_received)
        elif isinstance(date_part_received, list):
            self.date_part_received = date_part_received
        else:
            self.date_part_received = None

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
            self.time_work_order_completion = self.date_workorder_completion - self.date_workorder_start
        except TypeError:
            self.time_work_order_completion = None

    def _get_time_to_dispatch(self):
        return self.time_to_dispatch

    def _set_time_to_dispatch(self):
        try:
            self.time_to_dispatch = self.date_maintenance_technician_arrive - self.date_machine_down
        except TypeError:
            self.time_to_dispatch = None

    def _get_time_to_return_to_operation(self):
        return self.time_to_return_to_operation

    def _set_time_to_return_to_operation(self):
        try:
            self.time_to_return_to_operation = self.date_machine_up - self.date_maintenance_technician_arrive
        except TypeError:
            self.time_to_return_to_operation = None

    def _get_time_to_issue_work_order(self):
        return self.time_to_issue_work_order

    def _set_time_to_issue_work_order(self):
        try:
            self.time_to_issue_work_order = self.date_workorder_start - self.date_machine_down
        except TypeError:
            self.time_to_issue_work_order = None

    def _get_time_to_travel(self):
        return self.time_to_travel

    def _set_time_to_travel(self):
        try:
            self.time_to_travel = self.date_maintenance_technician_arrive - self.date_workorder_start
        except TypeError:
            self.time_to_travel = None

    def _get_time_to_solve_problem(self):
        return self.time_to_solve_problem

    def _set_time_to_solve_problem(self):
        try:
            self.time_to_solve_problem = self.date_problem_solve - self.date_maintenance_technician_arrive
        except TypeError:
            self.time_to_solve_problem = None

    def _get_time_to_diagnose(self):
        return self.time_to_diagnose

    def _set_time_to_diagnose(self):
        try:
            self.time_to_diagnose = self.date_problem_found - self.date_maintenance_technician_arrive
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
            self.time_lead_for_part = self.date_part_received - self.date_part_ordered
        except TypeError:
            self.time_lead_for_part = None

    def _get_time_to_fix(self):
        return self.time_to_fix

    def _set_time_to_fix(self):
        try:
            self.time_to_fix = self.date_problem_solve - self.date_part_received
        except TypeError:
            self.time_to_fix = None

    def _get_time_to_turn_on(self):
        return self.time_to_turn_on

    def _set_time_to_turn_on(self):
        try:
            self.time_to_turn_on = self.date_machine_up - self.date_problem_solve
        except TypeError:
            self.time_to_turn_on = None


    def create_all_time(self):
        """Set all the time based on all the date in the object"""
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

    def __bool__(self):
        return not (
            (self.problem is None) and
            (self.solution is None) and
            (self.effects is None) and
            (self.cause is None) and
            (self.part_in_process is None) and
            (self.necessary_part is None) and
            (self.machine_down is None) and
            (self.date_machine_down is None) and
            (self.date_machine_up is None) and
            (self.date_workorder_completion is None) and
            (self.date_workorder_start is None) and
            (self.date_maintenance_technician_arrive is None) and
            (self.date_problem_found is None) and
            (self.date_problem_solve is None) and
            (self.date_part_ordered is None) and
            (self.date_part_received is None)
        )

    def __str__(self):
        self.create_all_time()
        return f"OBJECT: {type(self)}\n\t" \
               f"problem: {self.problem} \n\tsolution: {self.solution} \n\t" \
               f"cause: {self.cause} \n\teffects: {self.effects} \n\t" \
               f"part_in_process: {self.part_in_process} \n\t|| necessary_part: {self.necessary_part} \n\t" \
               f"machine_down: {self.machine_down} \n\t" \
               f"date_machine_up: {self.date_machine_up} \n\t|| date_machine_down: {self.date_machine_down} \n\t" \
               f"date_workorder_start: {self.date_workorder_start} \n\t" \
               f"date_workorder_completion: {self.date_workorder_completion} \n\t" \
               f"date_maintenance_technician_arrives: {self.date_maintenance_technician_arrive} \n\t" \
               f"date_problem_found: {self.date_problem_found} \n\tdate_problem_solved: {self.date_problem_solve} \n\t" \
               f"date_part_ordered: {self.date_part_ordered} \n\t" \
               f"date_part_received: {self.date_part_received} \n\t" \
               f"time_to_repair: {self.time_to_repair} \n\ttime_work_order_completion: {self.time_work_order_completion} \n\t" \
               f"time_to_dispatch: {self.time_to_dispatch} \n\ttime_to_return_to_operation: {self.time_to_return_to_operation} \n\t" \
               f"time_to_issue_work_order: {self.time_to_issue_work_order} \n\ttime_to_travel: {self.time_to_travel} \n\t" \
               f"time_to_solve_problem: {self.time_to_solve_problem} \n\ttime_to_diagnose: {self.time_to_diagnose} \n\t" \
               f"time_to_order: {self.time_to_order} \n\ttime_lead_for_part: {self.time_lead_for_part} \n\t" \
               f"time_to_fix: {self.time_to_fix} \n\ttime_to_turn_on: {self.time_to_turn_on} \n\t"


    def cypher_issue_label(self, variable_issue="issue"):
        """Create a Cypher query with the given variable and all label for the node ISSUE

        Parameters
        ----------
        variable_issue :
            default "issue" to refer to a special node

        Returns
        -------
        type
            a string - Cypher Query : issue:ISSUE

        """
        return f'{variable_issue}{self.databaseInfoIssue["label"]["issue"]}'

    def cypher_issue_all(self, variable_issue="issue"):
        """Create a Cypher query to return the specific node ISSUE define by all the possible properties
        (DESCRIPTION_OF_PROBLEM, DESCRIPTION_OF_SOLUTION, DESCRIPTION_OF_CAUSE, DESCRIPTION_OF_EFFECTS,
        MACHINE_DOWN, NECESSARY_PART, PART_IN_PROCESS, DATE_MACHINE_DOWN, DATE_MAINTENANCEWORKOREDER_START,
        DATE_MAINTENANCE_TECHNICIAN_ARRIVE, DATE_PROBLEM_FOUND, DATE_PROBLEM_SOLVE, DATE_PART_RECEIVED,
        DATE_PART_ORDERED, DATE_MACHINE_UP,, DATE_MAINTENANCEWORKORDER_COMPLETION)
        
        The time information are not store in the database because we can calculate them very fast,
        but it is totaly possible to store it to recude the computation time but increase the size of the database

        Parameters
        ----------
        variable_issue :
            default "issue" to refer to a specific ISSUE

        Returns
        -------
        type
            a string - Cypher Query : (issue:ISSUE{description_of_problem:"x", description_of_solution:"x", ...})

        """

        query = f'({self.cypher_issue_label(variable_issue)}'
        if self.problem or self.solution or self.cause or self.effects or self.part_in_process or self.necessary_part \
                or self.machine_down or self.date_machine_up or self.date_machine_down \
                or self.date_workorder_start or self.date_workorder_completion \
                or self.date_maintenance_technician_arrive or self.date_problem_found or self.date_problem_solve \
                or self.date_part_ordered or self.date_part_received is not None:
            query += "{"
            if self.problem:
                query += f'{self.databaseInfoIssue["properties"]["description_problem"]}:"{self.problem}",'
            if self.solution:
                query += f'{self.databaseInfoIssue["properties"]["description_solution"]}:"{self.solution}",'
            if self.cause:
                query += f'{self.databaseInfoIssue["properties"]["description_cause"]}:"{self.cause}",'
            if self.effects:
                query += f'{self.databaseInfoIssue["properties"]["description_effect"]}:"{self.effects}",'
            if self.part_in_process:
                query += f'{self.databaseInfoIssue["properties"]["part_in_process"]}:"{self.part_in_process}",'
            if self.necessary_part:
                query += f'{self.databaseInfoIssue["properties"]["necessary_part"]}:"{self.necessary_part}",'
            if self.machine_down:
                query += f'{self.databaseInfoIssue["properties"]["machine_down"]}:"{self.machine_down}",'
            if self.date_machine_up:
                query += f'{self.databaseInfoIssue["properties"]["date_machine_up"]}:"{self.date_machine_up}",'
            if self.date_machine_down:
                query += f'{self.databaseInfoIssue["properties"]["date_machine_down"]}:"{self.date_machine_down }",'
            if self.date_workorder_start:
                query += f'{self.databaseInfoIssue["properties"]["date_workorder_start"]}:"{self.date_workorder_start}",'
            if self.date_workorder_completion:
                query += f'{self.databaseInfoIssue["properties"]["date_workorder_completion"]}:"{self.date_workorder_completion}",'
            if self.date_maintenance_technician_arrive:
                query += f'{self.databaseInfoIssue["properties"]["date_maintenance_technician_arrive"]}:"{self.date_maintenance_technician_arrive}",'
            if self.date_problem_found:
                query += f'{self.databaseInfoIssue["properties"]["date_problem_found"]}:"{self.date_problem_found}",'
            if self.date_problem_solve:
                query += f'{self.databaseInfoIssue["properties"]["date_problem_solve"]}:"{self.date_problem_solve}",'
            if self.date_part_ordered:
                query += f'{self.databaseInfoIssue["properties"]["date_part_ordered"]}:"{self.date_part_ordered}",'
            if self.date_part_received:
                query += f'{self.databaseInfoIssue["properties"]["date_part_received"]}:"{self.date_part_received}",'
            query = query[:-1] + "}"
        return query + ")"


    def cypher_issue_whereReturn(self, variable_issue="issue"):
        """Create 2 arrays used for the WHERE clause and the RETURN clause of the Cypher Query from this ISSUE
        Used to filter the database based on specifics properties values
        
        For this case, the properties of this object might be an array
        If a value in an array is "_" this property will be added to the return statement

        Parameters
        ----------
        variable_issue :
            default "issue" to match a specific ISSUE

        Returns
        -------
        type
            a tuple of arrays - where properties, return properties :
            (['issue.description_of_problem = "bob','issue.description_of_problem = "3"]['issue.part_in_process'])

        """

        cypherWhere = []
        cypherReturn = []
        if self.problem:
            for p in self.problem:
                if p == "_":
                    cypherReturn.append(f'{variable_issue}.{self.databaseInfoIssue["properties"]["description_problem"]}')
                else:
                    cypherWhere.append(f'{variable_issue}.{self.databaseInfoIssue["properties"]["description_problem"]} = "{p}"')
        if self.solution:
            for s in self.solution:
                if s == "_":
                    cypherReturn.append(f'{variable_issue}.{self.databaseInfoIssue["properties"]["description_solution"]}')
                else:
                    cypherWhere.append(f'{variable_issue}.{self.databaseInfoIssue["properties"]["description_solution"]} = "{s}"')
        if self.cause:
            for c in self.cause:
                if c == "_":
                    cypherReturn.append(f'{variable_issue}.{self.databaseInfoIssue["properties"]["description_cause"]}')
                else:
                    cypherWhere.append(f'{variable_issue}.{self.databaseInfoIssue["properties"]["description_cause"]} = "{ c }"')
        if self.effects:
            for e in self.effects:
                if e == "_":
                    cypherReturn.append(f'{variable_issue}.{self.databaseInfoIssue["properties"]["description_effect"]}')
                else:
                    cypherWhere.append(f'{variable_issue}.{self.databaseInfoIssue["properties"]["description_effect"]} = "{ e }"')
        if self.machine_down:
            for d in self.machine_down:
                if d == "_":
                    cypherReturn.append(f'{variable_issue}.{self.databaseInfoIssue["properties"]["machine_down"]}')
                else:
                    cypherWhere.append(f'{variable_issue}.{self.databaseInfoIssue["properties"]["machine_down"]} = "{ d }"')
        if self.part_in_process:
            for p in self.part_in_process:
                if p == "_":
                    cypherReturn.append(f'{variable_issue}.{self.databaseInfoIssue["properties"]["part_in_process"]}')
                else:
                    cypherWhere.append(f'{variable_issue}.{self.databaseInfoIssue["properties"]["part_in_process"]} = "{ p }"')
        if self.necessary_part:
            for p in self.necessary_part:
                if p == "_":
                    cypherReturn.append(f'{variable_issue}.{self.databaseInfoIssue["properties"]["necessary_part"]}')
                else:
                    cypherWhere.append(f'{variable_issue}.{self.databaseInfoIssue["properties"]["necessary_part"]} = "{ p }"')
        if self.date_machine_down:
            for d in self.date_machine_down:
                if d == "_":
                    cypherReturn.append(f'{variable_issue}.{self.databaseInfoIssue["properties"]["date_machine_down"]}')
                else:
                    cypherWhere.append(f'{variable_issue}.{self.databaseInfoIssue["properties"]["date_machine_down"]} = "{ d }"')
        if self.date_workorder_start:
            for d in self.date_workorder_start:
                if d == "_":
                    cypherReturn.append(f'{variable_issue}.{self.databaseInfoIssue["properties"]["date_workorder_start"]}')
                else:
                    cypherWhere.append(f'{variable_issue}.{self.databaseInfoIssue["properties"]["date_workorder_start"]} = "{ d }"')
        if self.date_maintenance_technician_arrive:
            for d in self.date_maintenance_technician_arrive:
                if d == "_":
                    cypherReturn.append(f'{variable_issue}.{self.databaseInfoIssue["properties"]["date_maintenance_technician_arrive"]}')
                else:
                    cypherWhere.append(f'{variable_issue}.{self.databaseInfoIssue["properties"]["date_maintenance_technician_arrive"]} = "{ d }"')
        if self.date_problem_found:
            for d in self.date_problem_found:
                if d == "_":
                    cypherReturn.append(f'{variable_issue}.{self.databaseInfoIssue["properties"]["date_problem_found"]}')
                else:
                    cypherWhere.append(f'{variable_issue}.{self.databaseInfoIssue["properties"]["date_problem_found"]} = "{ d }"')
        if self.date_part_ordered:
            for d in self.date_part_ordered:
                if d == "_":
                    cypherReturn.append(f'{variable_issue}.{self.databaseInfoIssue["properties"]["date_part_ordered"]}')
                else:
                    cypherWhere.append(f'{variable_issue}.{self.databaseInfoIssue["properties"]["date_part_ordered"]} = "{ d }"')
        if self.date_part_received:
            for d in self.date_part_received:
                if d == "_":
                    cypherReturn.append(f'{variable_issue}.{self.databaseInfoIssue["properties"]["date_part_received"]}')
                else:
                    cypherWhere.append(f'{variable_issue}.{self.databaseInfoIssue["properties"]["date_part_received"]} = "{ d }"')
        if self.date_problem_solve:
            for d in self.date_problem_solve:
                if d == "_":
                    cypherReturn.append(f'{variable_issue}.{self.databaseInfoIssue["properties"]["date_problem_solve"]}')
                else:
                    cypherWhere.append(f'{variable_issue}.{self.databaseInfoIssue["properties"]["date_problem_solve"]} = "{ d }"')
        if self.date_machine_up:
            for d in self.date_machine_up:
                if d == "_":
                    cypherReturn.append(f'{variable_issue}.{self.databaseInfoIssue["properties"]["date_machine_up"]}')
                else:
                    cypherWhere.append(f'{variable_issue}.{self.databaseInfoIssue["properties"]["date_machine_up"]} = "{ d }"')
        if self.date_workorder_completion:
            for d in self.date_workorder_completion:
                if d == "_":
                    cypherReturn.append(f'{variable_issue}.{self.databaseInfoIssue["properties"]["date_workorder_completion"]}')
                else:
                    cypherWhere.append(f'{variable_issue}.{self.databaseInfoIssue["properties"]["date_workorder_completion"]} = "{ d }"')


        return cypherWhere, cypherReturn
