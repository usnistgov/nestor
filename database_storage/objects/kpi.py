"""
File: human.py
Author: Sascha MOCCOZET
Organisation:
   Departament of Commerce USA
   National Institute of Standards and Technology - NIST
   Engineering Laboratory - EL
   Systems Integration Division - SID
   Information Modeling and Testing Group - IMTG
   <Insert Project Name>
Description:
   This file contains the object KPI,
   It represent every information needed to create any kind of query into the database to get and create KPI's

THE IDEA OF THIS KPI OBJECT IS STILL IN PROCESS, LOTS OF THE IDEA MIGHT CHANGE IN THE FUTUR
"""


import networkx as nx


from database_storage.objects.issue import *
from database_storage.objects.machine import *
from database_storage.objects.human import *
from database_storage.objects.tag import *
from database_storage.helper import updateDict

class Kpi:

    def __init__(self, operation= None, cypherMatch=set(), cypherWhere="", cypherReturn=set()):
        self.dict = {
            '=': '=',
            '<>': '<>',
            '<': '<',
            '>': '>',
            '<=': '<=',
            '>=': '>=',
            '0': 'IS NULL',
            '1': 'IS NOT NULL',
            '.-': 'STARTS WITH',
            '-.': 'ENDS WITH',
            '-': 'CONTAINS'
        }
        self._set_operation(operation)


        self.cypherMatch = set()
        self.cypherWhere = ""
        self.cypherReturn = set()


        # self._set_cypherWhere(cypherWhere)
        self._set_cypherMatch(cypherMatch)
        # self._set_cypherReturn(cypherReturn)

    def _get_operation(self):
        return self.operation

    def _set_operation(self, operation):
        if operation in self.dict:
            self.operation = self.dict[operation]
            print(self.operation)
        else:
            self.operator = None

    def _get_cypherMatch(self):

        return self.cypherMatch

    def _set_cypherMatch(self, cypherMatch):
        if cypherMatch:
            if isinstance(cypherMatch, str):
                self.cypherMatch.add(cypherMatch)
            else:
                self.cypherMatch.update(cypherMatch)

    # def _get_cypherWhere(self):
    #     return self.cypherWhere
    #
    # def _set_cypherWhere(self, cypherWhere):
    #     self.cypherWhere=cypherWhere
    #
    # def _get_cypherReturn(self):
    #     return self.cypherReturn
    #
    # def _set_cypherReturn(self, cypherReturn):
    #     if cypherReturn:
    #         if isinstance(cypherReturn, str):
    #             self.cypherReturn.add(cypherReturn)
    #         else:
    #             self.cypherReturn.update(cypherReturn)

    def __add__(self, other):
        cypherMatch = self.cypherMatch.union(other.cypherMatch)
        cypherWhere = ""
        cypherReturn = set()

        # cypherWhere=  self.cypherWhere + " AND " + other.cypherWhere
        #
        # if self.cypherReturn and other.cypherReturn:
        #     cypherReturn= self.cypherReturn.union(other.cypherReturn)
        # elif self.cypherReturn:
        #     cypherReturn = self.cypherReturn
        # elif other.cypherReturn:
        #     cypherReturn = other.cypherReturn
        # else:
        #     cypherReturn = set()

        tmp = Kpi(cypherMatch=cypherMatch,
                  cypherWhere=cypherWhere,
                  cypherReturn=cypherReturn,
        )
        return tmp

    def __sub__(self, other):
        cypherMatch = self.cypherMatch.union(other.cypherMatch)
        cypherWhere = ""
        cypherReturn = set()

        tmp = Kpi(cypherMatch=cypherMatch,
                  cypherWhere=cypherWhere,
                  cypherReturn=cypherReturn,
                  )
        return tmp


    def __mul__(self, other):
        cypherMatch = self.cypherMatch.union(other.cypherMatch)
        cypherWhere = ""
        cypherReturn = set()

        tmp = Kpi(cypherMatch=cypherMatch,
                  cypherWhere=cypherWhere,
                  cypherReturn=cypherReturn,
                  )
        return tmp

    def cypher_where_kpi(self):
        return "this function has to be defined for all the object inherit from kpi"

    def cypher_match_kpi(self):
        return "this function has to be defined for all the object inherit from kpi"

    def cypher_return_kpi(self):
        return "this function has to be defined for all the object inherit from kpi"

    def cypher_createQuery(self):
        query = f'MATCH {" ,".join(self.cypherMatch)}\n'
        query += f'WHERE {self.cypherWhere}\n'
        query += f'RETURN {" ,".join(self.cypherReturn)}'

        return query


class MachineKpi(Machine, Kpi):

    def __init__(self, operation=None, name=None, manufacturer=None, locasion=None, machine_type=None, databaseInfo=None):
        Machine.__init__(self, name=name, manufacturer=manufacturer, locasion=locasion, machine_type=machine_type, databaseInfo=databaseInfo)
        Kpi.__init__(self, operation=operation)

        self.databaseInfo = databaseInfo

        self._set_cypherMatch(self.cypher_match())
        # self._set_cypherWhere(self.cypher_where(operation))
        # self._set_cypherReturn(self.cypher_return())


    def cypher_match_kpi(self, variable_machine="machine", variable_machinetype="machine_type"):
        tmp = f'(issue:{self.databaseInfo["issue"]["label"]["issue"]})-[{self.databaseInfo["edges"]["issue-machine"]}->({self.cypher_machine_label(variable_machine)})'
        if self.machine_type:
            tmp += f'-[{self.databaseInfo["edges"]["machine-machinetype"]}]->({self.cypher_machinetype_label(variable_machinetype)})'
        return tmp

    # def cypher_where_kpi(self, variable_machine="machine", variable_machinetype="machine_type"):
    #     return self.cypher_where(self.operation, variable_machine, variable_machinetype)

    #
    #
    # def cypher_return_kpi(self, variable_machine="machine", variable_machinetype="machine_type"):
    #     return self.cypher_return(variable_machine,variable_machinetype)


class IssueKpi(Issue, Kpi):

    def __init__(self, operation=None, problem=None, solution=None, cause=None, effects=None,
                 part_in_process=None, necessary_part=None, machine_down=None,
                 cost=None,
                 date_machine_up=None, date_machine_down=None,
                 date_workorder_start=None, date_workorder_completion=None,
                 date_maintenance_technician_arrive=None,
                 date_problem_found=None, date_problem_solved=None,
                 date_part_ordered=None, date_part_received=None,
                 databaseInfo=None):
        Issue.__init__(self, problem=problem, solution=solution, cause=cause, effects=effects,
                       part_in_process=part_in_process, necessary_part=necessary_part, machine_down=machine_down, cost=cost,
                       date_machine_up=date_machine_up, date_machine_down=date_machine_down, date_workorder_start=date_workorder_start,
                       date_workorder_completion=date_workorder_completion, date_maintenance_technician_arrive=date_maintenance_technician_arrive,
                       date_problem_found=date_problem_found, date_problem_solved=date_problem_solved, date_part_ordered=date_part_ordered,
                       date_part_received=date_part_received, databaseInfo=databaseInfo)
        Kpi.__init__(self, operation=operation)

        self.databaseInfo = databaseInfo

        self._set_cypherMatch(self.cypher_match())
        # self._set_cypherWhere(self.cypher_where(operation))
        # self._set_cypherReturn(self.cypher_return())


    def cypher_match_kpi(self, variable_machine="machine", variable_machinetype="machine_type"):
        tmp = f'(issue:{self.databaseInfo["issue"]["label"]["issue"]})'
        return tmp

