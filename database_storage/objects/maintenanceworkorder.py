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
   This file contains the object MIANTENENCEWORKORDER,
   It represent every information needed to create the database Node and relationship

"""

import collections


class MaintenanceWorkOrder:
    """
    a MAINTENENCEWORKORDER represent all the informations that refer to an event in our context:
    When a machine as an issue, all the information related to that are merge inbto tha object
    Several function are used to create the needed Cypher query that can be executed into the database.

   This object should be use when extracting the CSV for every row we create a MAINTENENCEWORKORDER object
   It is instantiate using:
       - issue: an ISSUE from the issue object
       - machine : a MACHINE from the machine.py file
       - operators: a OPERATOR or array of OPERATOR from the human.py file
       - technicians: a TECHNICIAN or array of TECHNICIAN from the human.py file
       - tag_items: an array of TAGITEM from the tag.py file
       - tag_problems: an array of TAGPROBLEM from the tag.py file
       - tag_solutions: an array of TAGSOLUTION from the tag.py file
       - tag_unknowns: an array of TAGUNKNOWN from the tag.py file
       - tag_problemItems: an array of TAGPROBLEMITEM from the tag.py file
       - tag_solutionsItems: an array of TAGSOLUTIONITEM from the tag.py file
       - databaseInfo: the dictionary that describe the database information (name of properties, and Label)

       It contains getter and setter for every properties, it is highly recommend to use the setter
        because it represent the data as a standard way - the way it is store in the database
       It contains a string representation
       It contains a boolean representation
       """

    def __init__(self, issue=None, machine=None, operators=None, technicians=None,  databaseSchema=None):

        self.databaseInfo = databaseSchema
        self.databaseInfoEdges = databaseSchema['edges']
        self._set_issue(issue)
        self._set_machine(machine)
        self._set_operators(operators)
        self._set_technicians(technicians)

    def _get_issue(self):
        return self.issue

    def _set_issue(self, issue):
        self.issue = issue

    def _get_machine(self):
        return self.machine

    def _set_machine(self, machine):
        self.machine = machine

    def _get_operators(self):
        return self.operators

    def _set_operators(self, operators):
        if not operators:
            self.operators = None
        else:
            if not isinstance(operators, collections.Iterable) or isinstance(operators, str):
                operators = [operators]
            self.operators = operators

    def _get_technician(self):
        return self.technicians

    def _set_technicians(self, technicians):
        if not technicians:
            self.technicians = None
        else:
            if not isinstance(technicians, collections.Iterable) or isinstance(technicians, str):
                technicians = [technicians]
            self.technicians = technicians

    def __bool__(self):
        return not (
            (self.issue is None) and
            (self.machine is None) and
            (self.technicians is None) and
            (self.operators is None)
        )

    def __str__(self):
        str =   f'object  =  {type(self)}\n\n' \
                f'ISSUE  :\n\t{self.issue}\n\n' \
                f'MACHINE  :\n\t{self.machine}\n\n'
        str += f'OPERATORs  :\n'
        if self.operators:
            for ope in self.operators:
                str += f'\t{ope.__str__()}\n\n'
        else:
            str += "\tNO OPERATOR\n\n"
        str += f'TECHNICIANs  :\n'
        if self.technicians:
            for tec in self.technicians:
                str += f'\t{tec.__str__()}\n\n'
        else:
            str += "\tNO OPERATOR\n\n"
        return str


    def cypher_mwo_createIssueOtherRelationship(self, var_issue="issue", var_machine="machine", var_machine_type="machine_type",
                                                var_operators="operators", var_technicians="technicians"):
        """
        Create a Cypher Query to create all the node from the objects as well as the relationship between these object
        The relationships created by this function are the follow:

        ISSUE -----> OPERATOR
        ISSUE -----> TECHNICIAN
        ISSUE -----> MACHINE
        MACHINE -----> MACHINE_TYPE

        The node ISSUE are created for every object
        The other nodes are merge only created if it didn't exists
        OPERATOR, TECHNICIAN, MACHINE, MACHINE_TYPE,


        :param var_issue: default "issue" to refer to a special node
        :param var_machine: default "machine" to refer to a special node
        :param var_machine_type: default "machine_type" to refer to a special node
        :param var_operators: default "operators" to refer to a special node
        :param var_technicians: default "technicians" to refer to a special node
        :return: a string - Cypher Query :

        CREATE (issue:ISSUE {...})

        MERGE (operator:HUMAN:OPERATOR {...})
        MERGE (issue)-->(operator)

        MERGE (technicians:HUMAN:TECHNICIAN {...})
        MERGE (issue)-->(technicians)

        MERGE (machine:MACHINE {...})
        MERGE (issue)-->(machine)

        MERGE (machine_type:MACHINE_TYPE {...})
        MERGE (machine)-->(machine_type)

        """

        query = f'\nCREATE {self.issue.cypher_issue_all(var_issue)}'

        if self.machine:
            query += self.machine.cypher_machine_merge(var_machine)
            query += f'\nMERGE ({var_issue})-[{self.databaseInfoEdges["issue-machine"]}]->({var_machine})'

            if self.machine._get_machine_type():
                query += self.machine.cypher_machinetype_merge(var_machine_type)
                query += f'\nMERGE ({var_machine})-[{self.databaseInfoEdges["machine-machinetype"]}]->({var_machine_type})'

        if self.operators:
            for index, operator in enumerate(self.operators):
                if operator:
                    var = var_operators + str(index)
                    query += operator.cypher_operator_merge(var)
                    query += f'\nMERGE ({var_issue})-[{self.databaseInfoEdges["issue-operator"]}]->({var})'

        if self.technicians:
            for index, technician in enumerate(self.technicians):
                if technician:
                    var = var_technicians + str(index)
                    query += technician.cypher_technician_merge(var)
                    query += f'\nMERGE ({var_issue})-[{self.databaseInfoEdges["issue-technician"]}]->({var})'

        return query