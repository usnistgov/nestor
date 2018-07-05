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


class MaintenanceWorkOrder():
    """a MAINTENENCEWORKORDER represent all the informations that refer to an event in our context:
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

    Parameters
    ----------

    Returns
    -------

    """

    def __init__(self, issue=None, machine=None, operators=None, technicians=None, tag_items=None, tag_problems=None,
                 tag_solutions=None, tag_unknowns=None, tag_problemItems=None, tag_solutionsItems=None,  databaseInfo=None):

        self.databaseInfo = databaseInfo
        self.databaseInfoEdges = databaseInfo['edges']
        self._set_issue(issue)
        self._set_machine(machine)
        self._set_operators(operators)
        self._set_technicians(technicians)
        self._set_tag_items(tag_items)
        self._set_tag_problems(tag_problems)
        self._set_tag_solutions(tag_solutions)
        self._set_tag_unknowns(tag_unknowns)
        self._set_tag_problemItems(tag_problemItems)
        self._set_tag_solutionsItems(tag_solutionsItems)

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

    def _get_tag_items(self):
        return self.tag_items

    def _set_tag_items(self, tag_items):
        if not tag_items:
            self.tag_items = None
        else:
            if not isinstance(tag_items, collections.Iterable) or isinstance(tag_items, str):
                tag_items = [tag_items]
            self.tag_items = tag_items

    def _get_tag_problems(self):
        return self.tag_problems

    def _set_tag_problems(self, tag_problems):
        if not tag_problems:
            self.tag_problems = None
        else:
            if not isinstance(tag_problems, collections.Iterable) or isinstance(tag_problems, str):
                tag_problems = [tag_problems]
            self.tag_problems = tag_problems

    def _get_tag_solutions(self):
        return self.tag_solutions

    def _set_tag_solutions(self, tag_solutions):
        if not tag_solutions:
            self.tag_solutions = None
        else:
            if not isinstance(tag_solutions, collections.Iterable) or isinstance(tag_solutions, str):
                tag_solutions = [tag_solutions]
            self.tag_solutions = tag_solutions

    def _get_tag_unknowns(self):
        return self.tag_unknowns

    def _set_tag_unknowns(self, tag_unknowns):
        if not tag_unknowns:
            self.tag_unknowns = None
        else:
            if not isinstance(tag_unknowns, collections.Iterable) or isinstance(tag_unknowns, str):
                tag_unknowns = [tag_unknowns]
            self.tag_unknowns = tag_unknowns

    def _get_tag_problemItems(self):
        return self.tag_problemItems

    def _set_tag_problemItems(self, tag_problemItems):
        if not tag_problemItems:
            self.tag_problemItems = None
        else:
            if not isinstance(tag_problemItems, collections.Iterable) or isinstance(tag_problemItems, str):
                tag_problemItems = [tag_problemItems]
            self.tag_problemItems = tag_problemItems

    def _get_tag_solutionsItems(self):
        return self.tag_solutionItems

    def _set_tag_solutionsItems(self, tag_solutionsItems):
        if not tag_solutionsItems:
            self.tag_solutionItems = None
        else:
            if not isinstance(tag_solutionsItems, collections.Iterable) or isinstance(tag_solutionsItems, str):
                tag_solutionsItems = [tag_solutionsItems]
            self.tag_solutionItems = tag_solutionsItems

    def __bool__(self):
        return not (
            (self.issue is None) and
            (self.machine is None) and
            (self.technicians is None) and
            (self.operators is None) and
            (self.tag_items is None) and
            (self.tag_problems is None) and
            (self.tag_solutions is None) and
            (self.tag_unknowns is None) and
            (self.tag_problemItems is None) and
            (self.tag_solutionItems is None)
        )

    def __str__(self):
        return "OBJECT: %s -->\n\t\t ISSUE:\n %s" \
               "\n\t\t MACHINE:\n %s" \
               "\n\t\t OPERATORS: \n %s" \
               "\n\t\t TECHNICIAN:\n %s" \
               "\n\t\t ITEM_TAG:\n %s" \
               "\n\t\t PROBLEM_TAGS:\n %s" \
               "\n\t\t SOLUTION_TAGS:\n %s" % \
               (type(self), self.issue, self.machine, self.operators, self.technicians, self.tag_items,
                self.tag_problemts,
                self.tag_solutions)

    def cypher_mwo_createIssueOtherRelationship(self, var_issue="issue", var_machine="machine", var_machine_type="machine_type",
                                                var_operators="operators", var_technicians="technicians", var_tag_items="tag_items",
                                                var_tag_problems="tag_problems", var_tag_solutions="tag_solutions", var_tag_unknowns="tag_unknowns",
                                                var_tag_problemItems="tag_problemItems", var_tag_solutionItems="tag_solutionItems"):
        """Create a Cypher Query to create all the node from the objects as well as the relationship between these object
        The relationships created by this function are the follow:
        
        ISSUE -----> OPERATOR
        ISSUE -----> TECHNICIAN
        ISSUE -----> MACHINE
        MACHINE -----> MACHINE_TYPE
        ISSUE -----> TAGITEM
        ISSUE -----> TAGPROBLEM
        ISSUE -----> TAGSOLUTION
        ISSUE -----> TAGUNKNOWN
        ISSUE -----> TAGPROBLEMITEM
        ISSUE -----> TAGPROBLEMSOLUTION
        
        The node ISSUE are created for every object
        The other nodes are merge only created if it didn't exists
        OPERATOR, TECHNICIAN, MACHINE, MACHINE_TYPE, TAGITEM, TAGPROBLEM, TAGSOLUTION, TAGUNKNOWN, TAGPROBLEMITEM, TAGPROBLEMSOLUTION

        Parameters
        ----------
        var_issue :
            default "issue" to refer to a special node
        var_machine :
            default "machine" to refer to a special node
        var_machine_type :
            default "machine_type" to refer to a special node
        var_operators :
            default "operators" to refer to a special node
        var_technicians :
            default "technicians" to refer to a special node
        var_tag_items :
            default "tag_items" to refer to a special node
        var_tag_problems :
            default "tag_problems" to refer to a special node
        var_tag_solutions :
            default "tag_solutions" to refer to a special node
        var_tag_unknowns :
            default "tag_unknowns" to refer to a special node
        var_tag_problemItems :
            default "tag_problemItems" to refer to a special node
        var_tag_solutionItems :
            default "tag_solutionItems" to refer to a special node

        Returns
        -------
        type
            a string - Cypher Query :
            
            CREATE (issue:ISSUE {...})
            
            MERGE (operator:HUMAN:OPERATOR {...})
            MERGE (issue)-->(operator)
            
            MERGE (technicians:HUMAN:TECHNICIAN {...})
            MERGE (issue)-->(technicians)
            
            MERGE (machine:MACHINE {...})
            MERGE (issue)-->(machine)
            
            MERGE (machine_type:MACHINE_TYPE {...})
            MERGE (machine)-->(machine_type)
            
            MERGE (tag_items:TAG:ONE_GRAM:ITEM {...})
            MERGE (issue)-->(tag_items)
            
            MERGE (tag_problems:TAG:ONE_GRAM:PROBLEM {...})
            MERGE (issue)-->(tag_problems)
            
            MERGE (tag_unknowns:TAG:ONE_GRAM:UNKNOWN {...})
            MERGE (issue)-->(tag_unknowns)
            
            MERGE (tag_problemItems:TAG:N_GRAM:PROBLEM_ITEM {...})
            MERGE (issue)-->(tag_problemItems)
            
            MERGE (tag_solutionItems:TAG:N_GRAM:SOLUTION_ITEM {...})
            MERGE (issue)-->(tag_solutionItems)

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

        if self.tag_items:
            for index, item in enumerate(self.tag_items):
                if item:
                    var = var_tag_items + str(index)
                    query += item.cypher_itemTag_merge(var)
                    query += f'\nMERGE ({var_issue})-[{self.databaseInfoEdges["issue-item"]}]->({var})'

        if self.tag_problems:
            for index, problem in enumerate(self.tag_problems):
                if problem:
                    var = var_tag_problems + str(index)
                    query += problem.cypher_problemTag_merge(var)
                    query += f'\nMERGE ({var_issue})-[{self.databaseInfoEdges["issue-problem"]}]->({var})'

        if self.tag_solutions:
            for index, solution in enumerate(self.tag_solutions):
                if solution:
                    var = var_tag_solutions + str(index)
                    query += solution.cypher_solutionTag_merge(var)
                    query += f'\nMERGE ({var_issue})-[{self.databaseInfoEdges["issue-solution"]}]->({var})'

        if self.tag_unknowns:
            for index, unknown in enumerate(self.tag_unknowns):
                if unknown:
                    var = var_tag_unknowns + str(index)
                    query += unknown.cypher_unknownTag_merge(var)
                    query += f'\nMERGE ({var_issue})-[{self.databaseInfoEdges["issue-unknown"]}]->({var})'

        if self.tag_problemItems:
            for index, problemItem in enumerate(self.tag_problemItems):
                if problemItem:
                    var = var_tag_problemItems + str(index)
                    query += problemItem.cypher_problemItemTag_merge(var)
                    query += f'\nMERGE ({var_issue})-[{self.databaseInfoEdges["issue-problemitem"]}]->({var})'

        if self.tag_solutionItems:
            for index, solutionItem in enumerate(self.tag_solutionItems):
                if solutionItem:
                    var = var_tag_solutionItems + str(index)
                    query += solutionItem.cypher_solutionItemTag_merge(var)
                    query += f'\nMERGE ({var_issue})-[{self.databaseInfoEdges["issue-solutionitem"]}]->({var})'
        return query

    def cypher_mwo_createNgram1GramRelationaship(self, var_tag_Ngramm="tag_Ngramm", var_tag_OneGram="tag_OneGram"):
        """Create a Cypher Query to link the One_Gram with the N_Gram for the current MAINTENANCEWORKORDER

        Parameters
        ----------
        var_tag_Ngramm :
            default "tag_Ngramm" to refer to a special node
        var_tag_OneGram :
            default "tag_OneGram" to refer to a special node

        Returns
        -------
        type
            a string - Cypher Query :
            
            MATCH (tag_Ngramm:TAG:N_GRAM {...})
            MATCH (tag_OneGram1:TAG:ONE_GRAM {...})
            MATCH (tag_OneGram2:TAG:ONE_GRAM {...})
            
            MERGE (tag_Ngramm) --> (tag_OneGram1)
            MERGE (tag_Ngramm) --> (tag_OneGram2)

        """
        queries = []

        if self.tag_problemItems or self.tag_solutionItems:
            if self.tag_problemItems and self.tag_solutionItems:
                tagNgrams = self.tag_problemItems + self.tag_solutionItems
            elif self.tag_problemItems:
                tagNgrams = self.tag_problemItems
            else:
                tagNgrams = self.tag_solutionItems

            for indexNgram, tagNgram in enumerate(tagNgrams):
                var_tag_Ngramm = var_tag_Ngramm + str(indexNgram)
                query = f'\nMATCH {tagNgram.cypher_nGramTag_keyword(var_tag_Ngramm)}'
                var_tagOneGrams = []

                # create the query to match everyOneGram that needs to be linked
                for index1gram, oneGram in enumerate(tagNgram._get_OneGrams()):
                    var_oneGram = var_tag_OneGram + str(indexNgram) + str(index1gram)
                    var_tagOneGrams.append(var_oneGram)

                    query += f'\nMATCH {oneGram.cypher_tag_keyword(var_oneGram)}'

                # Create the query to link all the OneGram to the current NGram
                for var_oneGramm in var_tagOneGrams:
                    query += f'\nMERGE ({var_tag_Ngramm})-[{self.databaseInfoEdges["ngram-onegram"]}]->({var_oneGramm})'


                queries.append(query)

        return queries


    def cypher_mwo_createItemItemRelationaship(self, var_tag_ItemA="tag_ItemA", var_tag_ItemB="tag_ItemB"):
        """Create the relationship between ITEM and ITEM based on the properties CHILD of each ITEM

        Parameters
        ----------
        var_tag_ItemA :
            default "tag_ItemA" to refer to a special node
        var_tag_ItemB :
            default "tag_ItemB" to refer to a special node

        Returns
        -------
        type
            a string - Cypher Query :
            
            MATCH (tag_ItemA:TAG:ONE_GRAM:ITEM {...})
            MERGE (tag_ItemB:TAG:ONE_GRAM:ITEM {...})
            
            MERGE (tag_ItemB) --> (tag_ItemA)

        """
        queries = []
        if self.tag_items:
            for indexA, itemA in enumerate(self.tag_items):
                if itemA._get_children():
                    var_tag_ItemA = var_tag_ItemA + str(indexA)
                    var_tagItems = []
                    query = f'\nMATCH {itemA.cypher_itemTag_keyword(var_tag_ItemA)}'

                    for indexB, itemB in enumerate(itemA._get_children()):
                        var_tag_ItemB = var_tag_ItemB + str(indexA) + str(indexB)
                        var_tagItems.append(var_tag_ItemB)

                        query += f'\nMERGE {itemB.cypher_itemTag_keyword(var_tag_ItemB)}'

                    for var_tagItem in var_tagItems:
                        query += f'\nMERGE ({var_tag_ItemA})<-[{self.databaseInfoEdges["item-item"]}]-({var_tagItem})'

                    queries.append(query)

        return queries


    def cypher_mwo_updateIssueItemRelationaship(self, var_Issue="issue", var_tag_Item="tag_Item"):
        """Create the relationship between ISSUE and ITEM depend on if the ITEM creates a problem or if it solve a solution
        This depend on the properties COMPOSED_OF of the object TAGPROBLEMITEM and TAGSOLUTIONITEM

        Parameters
        ----------
        var_Issue :
            default "issue" to refer to a special node
        var_tag_Item :
            default "tag_Item" to refer to a special node

        Returns
        -------
        type
            a string - Cypher Query :
            
            MATCH (tag_Item:TAG:ONE_GRAM:ITEM {...})
            MATCH (issue:ISSUE {...})
            
            CREATE (issue) --> (tag_Item)

        """

        queries=[]

        if self.tag_solutionItems:
            for indexSI, si in enumerate(self.tag_solutionItems):

                for indexOG, onGram in enumerate(si._get_OneGrams()):
                    var_tag_Item = var_tag_Item + str(indexOG)
                    query = f'\nMATCH {self.issue.cypher_issue_all(var_Issue)}'
                    query += f'\nMATCH {onGram.cypher_oneGramTag_keyword(var_tag_Item)}'
                    query += f'\nWHERE {var_tag_Item}{self.databaseInfo["tag"]["label"]["item"]}'
                    query += f'\nMATCH ({var_Issue})-[oldrel{self.databaseInfoEdges["issue-item"]}]->({var_tag_Item})'
                    query += f'\nCREATE ({var_Issue})-[newrel{self.databaseInfoEdges["issue-itemassolution"]}]->({var_tag_Item})'

                    queries.append(query)

        if self.tag_problemItems:
            for indexPI, pi in enumerate(self.tag_problemItems):
                for indexOG, onGram in enumerate(pi._get_OneGrams()):
                    var_tag_Item = var_tag_Item + str(indexOG)
                    query = f'\nMATCH {self.issue.cypher_issue_all(var_Issue)}'
                    query += f'\nMATCH {onGram.cypher_oneGramTag_keyword(var_tag_Item)}'
                    query += f'\nWHERE {var_tag_Item}{self.databaseInfo["tag"]["label"]["item"]}'
                    query += f'\nMATCH ({var_Issue})-[oldrel{self.databaseInfoEdges["issue-item"]}]->({var_tag_Item})'
                    query += f'\nCREATE ({var_Issue})-[newrel{self.databaseInfoEdges["issue-itemasproblem"]}]->({var_tag_Item})'

                    queries.append(query)

        return queries
