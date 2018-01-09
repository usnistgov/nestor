import collections

from Program.Database.Database_Properties import LabelEdges
from Program.Database.Database_Properties import NodeHuman
from Program.Database.Database_Properties import NodeTag


class MaintenanceWorkOrder():
    """
    The maintenance Work Order (MWO) represent every new MWO
    MWO are extracted from a CSV files and store in a Neo4J database using the my methods by create CYPHER queries

    In the database, a given MWO is split into different nodes used to create links between different MWOs
    a MWO can have only 1 node ISSUE and i node MACHINE (with 1 MACHINE_TYPE)
    But it can be linked with multiple OPERATOR and TECHNICIAN as well as multiple TAG

    In the future, it might be representing with the item of the soltuion and the one of the problem

    the MWO is represented in the database with the following information:
    (ISSUE) -[COVERED]-> (MACHINE) -[IS_A]-> (MACHINE_TYPE)
    (ISSUE) -[REQUESTED_BY]-> (OPERATOR)
    (ISSUE) -[SOLVE_BY]-> (TECHNICIAN)
    (ISSUE) -[PROBLEM]-> (TAG)
    (ISSUE) -[SOLUTION]-> (TAG)

    PARAMETERS:
            issue           --  (Object) Issue, The information specific to a MWO
            machine         --  (Object) Machine, the information based on the Machine
            operator        --  Array (Object) Human, the information of the Operators
            technician      --  Array (Object) Human, the information of the Technicians
            problemtags     --  Array (Object) Tag, the information of the Tag describing the problem
            solutiontags    --  Array (Object) Tag, the information of the Tag describing the solution


       METHODS:
            create_database --  return the query to create a new MWO
    """

    def __init__(self, issue, machine=None, operators=None, technicians=None, itemtags=None, problemtags=None, solutiontags=None):
        self._set_issue(issue)
        self._set_machine(machine)
        self._set_operators(operators)
        self._set_technicians(technicians)
        self._set_itemtags(itemtags)
        self._set_problemtags(problemtags)
        self._set_solutiontags(solutiontags)

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
        if not isinstance(operators, collections.Iterable) or isinstance(operators, str):
            operators = [operators]
        self.operators = operators

    def _get_technician(self):
        return self.technician

    def _set_technicians(self, technicians):
        if not isinstance(technicians, collections.Iterable) or isinstance(technicians, str):
            technicians = [technicians]
        self.technicians = technicians

    def _get_itemtags(self):
        return self.itemtags

    def _set_itemtags(self, itemtags):
        if not isinstance(itemtags, collections.Iterable) or isinstance(itemtags, str):
            itemtags = [itemtags]
        self.itemtags = itemtags

    def _get_problemtags(self):
        return self.problemtags

    def _set_problemtags(self, problemtags):
        if not isinstance(problemtags, collections.Iterable) or isinstance(problemtags, str):
            problemtags = [problemtags]
        self.problemtags = problemtags

    def _get_solutiontags(self):
        return self.solutiontags

    def _set_solutiontags(self, solutiontags):
        if not isinstance(solutiontags, collections.Iterable) or isinstance(solutiontags, str):
            solutiontags = [solutiontags]
        self.solutiontags = solutiontags

    def __str__(self):
        return "OBJECT: %s -->\n\t\t ISSUE:\n %s" \
               "\n\t\t MACHINE:\n %s" \
               "\n\t\t OPERATORS: \n %s" \
               "\n\t\t TECHNICIAN:\n %s" \
               "\n\t\t ITEM_TAG:\n %s" \
               "\n\t\t PROBLEM_TAGS:\n %s" \
               "\n\t\t SOLUTION_TAGS:\n %s" % \
               (type(self), self.issue, self.machine, self.operators, self.technicians, self.itemtags, self.problemtags,
                self.solutiontags)


    def create_database(self, varIssue, varMachine, varMachinetype, varOperators, varTechnicians, varItemtag,
                        varProblemtags, varSolutiontags):
        """
        The query created an inuque Issue
        But merge the others:
            if a node already exists in the database with the given information
                it update it if this MWO have more information
            if a node didn't exists in the database
                it create a new one

        :param varIssue: A string to represent the Issue
        :param varMachine: A string to represent the Machine
        :param varMachinetype: A string to represent the Machine Type
        :param varOperators: A string to represent the Operators
        :param varTechnicians: A string to represent the Technicians
        :param varItemtag: A string to represent the Tag Item
        :param varProblemtags: A string to represent the Tag Problem Action
        :param varSolutiontags: A string to represent the Tag Solution Action
        :return: a query to create a new MWO
        """
        query = "CREATE %s" % (self.issue.toCypherDescription(varIssue))
        query += "\n %s" % (self.issue.toCypherUpdate(varIssue))

####    MACHINE     ######
        if self.machine is not None:
            if self.machine._get_name() is not None:
                query += "\n\nMERGE %s" % (self.machine.toCypherName(varMachine))
                query += "\n %s " % (self.machine.toCypherUpdate(varMachine))
                query += '\nMERGE(%s)-[%s]->(%s)' % (varIssue, LabelEdges.LABEL_COVERED.value, varMachine)

####    MACHINE_TYPE     ######
        if self.machine._get_type() is not None:
            query += "\n\nMERGE %s" % (self.machine.toCypherType(varMachinetype))
            query += '\nMERGE (%s)-[%s]->(%s)' % (varMachine, LabelEdges.LABEL_ISA.value, varMachinetype)

####    OPERATORS     ######
        if self.operators is not None and len(self.operators) is not 0:
            for i in range(0, len(self.operators)):
                if self.operators[i]._get_name() is not None:
                    query += "\n\nMERGE %s" % \
                             (self.operators[i].toCypherName(varOperators + str(i)))
                    query += "\n%s" % (self.operators[i].toCypherUpdate(varOperators + str(i), NodeHuman.LABEL_OPERATOR))
                    query += '\nMERGE (%s)-[%s]->(%s)' % \
                             (varIssue, LabelEdges.LABEL_REQUESTED.value, varOperators + str(i))

####    TECHNICIANS     ######
        if self.technicians is not None and len(self.technicians) is not 0:
            for i in range(0, len(self.technicians)):
                if self.technicians[i]._get_name() is not None:
                    query += "\n\nMERGE %s" % \
                             (self.technicians[i].toCypherName(varTechnicians + str(i)))
                    query += "\n%s" % (self.technicians[i].toCypherUpdate(varTechnicians + str(i), NodeHuman.LABEL_TECHNICIAN))
                    query += '\nMERGE (%s)-[%s]->(%s)' % \
                             (varIssue, LabelEdges.LABEL_SOLVE.value, varTechnicians + str(i))

####    ITEM     ######
        if self.itemtags is not None and len(self.itemtags) is not 0:
            for i in range(0, len(self.itemtags)):
                if self.itemtags[i]._get_keyword() is not None:
                    query += "\n\nMERGE %s" % \
                             (self.itemtags[i].toCypher(varItemtag + str(i), NodeTag.LABEL_ITEM))
                    query += '\nMERGE (%s)-[%s]->(%s)' % \
                             (varIssue, LabelEdges.LABEL_CONTAINS.value, varItemtag + str(i))

####    PROBLEM     ######
        if self.problemtags is not None and len(self.problemtags) is not 0:
            for i in range(0, len(self.problemtags)):
                if self.problemtags[i]._get_keyword() is not None:
                    query += "\n\nMERGE %s" % \
                             (self.problemtags[i].toCypher(varProblemtags + str(i), NodeTag.LABEL_ACTION))
                    query += '\nMERGE (%s)-[%s]->(%s)' % \
                             (varIssue, LabelEdges.LABEL_PROBLEM.value, varProblemtags + str(i))

####    SOLUTION     ######
        if self.solutiontags is not None and len(self.solutiontags) is not 0:
            for i in range(0, len(self.solutiontags)):
                if self.solutiontags[i]._get_keyword() is not None:
                    query += "\n\nMERGE %s" % \
                             (self.solutiontags[i].toCypher(varSolutiontags + str(i), NodeTag.LABEL_ACTION))
                    query += '\nMERGE (%s)-[%s]->(%s)' % \
                             (varIssue, LabelEdges.LABEL_SOLUTION.value, varSolutiontags + str(i))

        return query
