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

    def __init__(self, operation= None, cypherWhere="", cypherMatch="",  cypherReturn="", cReturn=False):
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

        self._set_cypherWhere(cypherWhere)
        self._set_cypherMatch(cypherMatch)
        self._set_cypherReturn(cypherReturn)

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

    def _get_cypherWhere(self):
        return self.cypherWhere

    def _set_cypherWhere(self, cypherWhere):
        self.cypherWhere=cypherWhere

    def _get_cypherReturn(self):
        return self.cypherReturn

    def _set_cypherReturn(self, cypherReturn):
        self.cypherReturn=cypherReturn

    def __add__(self, other):
        cypherWhere=  self.cypherWhere + " AND " + other.cypherWhere
        cypherMatch=  self.cypherMatch.union(other.cypherMatch)
        cypherReturn=  ""

        tmp = Kpi(cypherWhere=cypherWhere,
                  cypherMatch=cypherMatch,
                  cypherReturn=cypherReturn,
        )
        return tmp

    def __sub__(self, other):
        self.cypherWhere = self.cypherWhere + " OR " + other.cypherWhere
        return self

    def __mul__(self, other):
        self.cypherWhere = self.cypherWhere + " XOR " + other.cypherWhere
        return self

    # def __ne__(self, other):
    #     return f'NOT {self.cypher_where()}'

    def cypher_where_kpi(self):
        return "this function has to be defined for all the object inherit from kpi"

    def cypher_match_kpi(self):
        return "this function has to be defined for all the object inherit from kpi"

    def cypher_return_kpi(self):
        return "this function has to be defined for all the object inherit from kpi"

    def cypher_createQuery(self):
        query = f'MATCH {" ,".join(self.cypherMatch)}\n'
        query += f'WHERE {self.cypherWhere}\n'
        query += f'RETURN {self.cypherReturn}'

        return query


class MachineKpi(Machine, Kpi):

    def __init__(self, operation=None, name=None, manufacturer=None, locasion=None, machine_type=None, databaseInfo=None):
        Machine.__init__(self, name=name, manufacturer=manufacturer, locasion=locasion, machine_type=machine_type, databaseInfo=databaseInfo)
        Kpi.__init__(self, operation=operation)

        self.databaseInfo = databaseInfo

        self._set_cypherWhere(self.cypher_where_kpi())
        self._set_cypherMatch(self.cypher_match_kpi())
        self._set_cypherReturn(self.cypher_return_kpi())


    def cypher_where_kpi(self, variable_machine="machine", variable_machinetype="machine_type"):
        return self.cypher_where(self.operation, variable_machine, variable_machinetype)

    def cypher_match_kpi(self, variable_machine="machine", variable_machinetype="machine_type"):
        tmp = f'(issue:{self.databaseInfo["issue"]["label"]["issue"]})-[{self.databaseInfo["edges"]["issue-machine"]}->({self.cypher_machine_label(variable_machine)})'
        if self.machine_type:
            tmp += f'-[{self.databaseInfo["edges"]["machine-machinetype"]}]->({self.cypher_machinetype_label(variable_machinetype)})'
        return tmp

    def cypher_return_kpi(self, variable_machine="machine", variable_machinetype="machine_type"):
        pass