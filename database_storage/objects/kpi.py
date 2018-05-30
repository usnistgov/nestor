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
    """a KPI represent all the informations that refer to create a query to create a kpi:
        This object contains every object for every kind of node possible into the database.
    
        it does not contains any array, but an object tha can contains a list for every of the object properties
        This might change to be an array and change be a boolean the way we create the return values
    
       This object is used every time we create a kpi
       It is instantiate using:
           - database: from the DATABASE Object from database.py file
           - kpiDict: a dictionary that represent the filter of the object
                it is used to represent the object we kpi will have
                We store it into a dictionary so that it can easily be saved and shared
                It looks like the dictionary fulldict that is the base of it and set up all the possible values
    
           It contains getter and setter for every properties, it is highly recommend to use the setter
            because it represent the data as a standard way - the way it is store in the database
           It contains a string representation
           It contains a boolean representation

    Parameters
    ----------

    Returns
    -------

    """

    def __init__(self, database, kpiDict):
        self.database=database
        self.query = None
        self.result = None
        self.dataframe_observation=None
        self.fullDict = {
            'issue':{
                    'description_problem': None,
                    'description_solution': None,
                    'description_cause': None,
                    'description_effect': None,
                    'machine_down': None,
                    'necessary_part': None,
                    'part_in_process': None,

                    'date_machine_down': None,
                    'date_workorder_start': None,
                    'date_maintenance_technician_arrive': None,
                    'date_problem_found': None,
                    'date_part_ordered': None,
                    'date_part_received': None,
                    'date_problem_solve': None,
                    'date_machine_up': None,
                    'date_workorder_completion': None
                },
            'human':{
                'name': None
            },
            'operator': {
                'name': None
            },
            'technician': {
                'name': None,
                'skills': None,
                'crafts': None
            },
            'machine': {
                'name': None,
                'manufacturer': None,
                'location': None
            },
            'machine_type': {
                'type': None
            },
            'tag': {
                'keyword': None,
                'synonyms':  None
            },
            'tag_oneGram': {
                'keyword':  None,
                'synonyms':  None
            },
            'tag_nGram': {
                'keyword':  None,
                'synonyms':  None
            },
            'tag_item': {
                'keyword':  None,
                'synonyms':  None
            },
            'tag_itemAsProblem': {
                'keyword':  None,
                'synonyms':  None
            },
            'tag_itemAsSolution': {
                'keyword':  None,
                'synonyms':  None
            },
            'tag_problem': {
                'keyword':  None,
                'synonyms':  None
            },
            'tag_solution': {
                'keyword':  None,
                'synonyms':  None
            },
            'tag_unknown': {
                'keyword':  None,
                'synonyms':  None
            },
            'tag_poblemItem': {
                'keyword':  None,
                'synonyms':  None
            },
            'tag_solutionItem': {
                'keyword':  None,
                'synonyms':  None
            }
        }

        updateDict(self.fullDict, kpiDict)


    def createObjects(self):
        self.issue = Issue(
            problem= self.fullDict["issue"]["description_problem"],
            solution= self.fullDict["issue"]["description_solution"],
            cause= self.fullDict["issue"]["description_cause"],
            effects= self.fullDict["issue"]["description_effect"],
            part_in_process= self.fullDict["issue"]["part_in_process"],
            necessary_part= self.fullDict["issue"]["necessary_part"],
            machine_down= self.fullDict["issue"]["machine_down"],
            date_machine_up= self.fullDict["issue"]["date_machine_up"],
            date_machine_down= self.fullDict["issue"]["date_machine_down"],
            date_workorder_start= self.fullDict["issue"]["date_workorder_start"],
            date_workorder_completion= self.fullDict["issue"]["date_workorder_completion"],
            date_maintenance_technician_arrive= self.fullDict["issue"]["date_maintenance_technician_arrive"],
            date_problem_found= self.fullDict["issue"]["date_problem_found"],
            date_problem_solved= self.fullDict["issue"]["date_problem_solve"],
            date_part_ordered= self.fullDict["issue"]["date_part_ordered"],
            date_part_received= self.fullDict["issue"]["date_part_received"],
            databaseInfo=self.database.schema
        )

        self.human = Human(
            name= self.fullDict["human"]["name"],
            databaseInfo=self.database.schema
        )

        self.operator = Operator(
            name= self.fullDict["operator"]["name"],
            databaseInfo=self.database.schema
        )

        self.technician = Technician(
            name= self.fullDict["technician"]["name"],
            skills= self.fullDict["technician"]["skills"],
            crafts= self.fullDict["technician"]["crafts"],
            databaseInfo=self.database.schema
        )

        self.machine = Machine(
            name= self.fullDict["machine"]["name"],
            manufacturer= self.fullDict["machine"]["manufacturer"],
            locasion= self.fullDict["machine"]["location"],
            machine_type= self.fullDict["machine_type"]["type"],
            databaseInfo=self.database.schema
        )

        self.tag = Tag(
            keyword= self.fullDict["tag"]["keyword"],
            synonyms= self.fullDict["tag"]["synonyms"],
            databaseInfo=self.database.schema
        )

        self.tag_oneGram = TagOneGram(
            keyword= self.fullDict["tag_oneGram"]["keyword"],
            synonyms= self.fullDict["tag_oneGram"]["synonyms"],
            databaseInfo=self.database.schema
        )

        self.tag_nGram = TagNGram(
            keyword= self.fullDict["tag_nGram"]["keyword"],
            synonyms= self.fullDict["tag_nGram"]["synonyms"],
            databaseInfo=self.database.schema
        )

        self.tag_item = TagItem(
            keyword= self.fullDict["tag_item"]["keyword"],
            synonyms= self.fullDict["tag_item"]["synonyms"],
            databaseInfo=self.database.schema
        )

        self.tag_itemAsProblem = TagItem(
            keyword=self.fullDict["tag_itemAsProblem"]["keyword"],
            synonyms=self.fullDict["tag_itemAsProblem"]["synonyms"],
            databaseInfo=self.database.schema
        )

        self.tag_itemAsSolution = TagItem(
            keyword=self.fullDict["tag_itemAsSolution"]["keyword"],
            synonyms=self.fullDict["tag_itemAsSolution"]["synonyms"],
            databaseInfo=self.database.schema
        )

        self.tag_problem = TagProblem(
            keyword= self.fullDict["tag_problem"]["keyword"],
            synonyms= self.fullDict["tag_problem"]["synonyms"],
            databaseInfo=self.database.schema
        )

        self.tag_solution = TagSolution(
            keyword= self.fullDict["tag_solution"]["keyword"],
            synonyms= self.fullDict["tag_solution"]["synonyms"],
            databaseInfo=self.database.schema
        )

        self.tag_unknown = TagUnknown(
            keyword= self.fullDict["tag_unknown"]["keyword"],
            synonyms= self.fullDict["tag_unknown"]["synonyms"],
            databaseInfo=self.database.schema
        )

        self.tag_problemItem = TagProblemItem(
            keyword= self.fullDict["tag_poblemItem"]["keyword"],
            synonyms= self.fullDict["tag_poblemItem"]["synonyms"],
            databaseInfo=self.database.schema
        )

        self.tag_solutionItem = TagSolutionItem(
            keyword= self.fullDict["tag_solutionItem"]["keyword"],
            synonyms= self.fullDict["tag_solutionItem"]["synonyms"],
            databaseInfo=self.database.schema
        )


    def __bool__(self):
        return not (
            (self.issue is None) and
            (self.machine is None) and
            (self.human is None) and
            (self.technician is None) and
            (self.operator is None) and
            (self.tag is None) and
            (self.tag_oneGram is None) and
            (self.tag_item is None) and
            (self.tag_problem is None) and
            (self.tag_solution is None) and
            (self.tag_unknown is None) and
            (self.tag_nGram is None) and
            (self.tag_problemItem is None) and
            (self.tag_solutionItem is None)
        )

    def tree_itemsHierarchie(self, child=False, parent=False):
        """

        Parameters
        ----------
        child :
            boolean default False, if True it will return the children hierarchy of all the given TAG_ITEM
        parent :
            boolean default False, if True it will return the parent hierarchy of all the given TAG_ITEM

        Returns
        -------
        type
            an array of tuple of Graph from networkx library
            [(childGraphItem1, parentGraphItem1), (childGraphItem2, parentGraphItem2), ...]

        """

        def children_hierarchy(currentTag, graph):
            """Recursive function
            Create the networkx graph the represent the children hierarchy of the given TAGITEM
            Only works for the item tag right now

            Parameters
            ----------
            currentTag :
                the TAGITEM form the graph will be created
            graph :
                the graph with all the relationship and the node

            Returns
            -------
            type
                the graph with a new Node

            """

            currentKeyword = currentTag._get_keyword()

            #create and send a query to the database to get the children of the current node
            query = f'MATCH {currentTag.cypher_tag_keyword("current")}-[{self.database.schema["edges"]["item-item"]}]->({currentTag.cypher_itemTag_label("next")})'
            query += f'\nRETURN next.{self.database.schema["tag"]["properties"]["keyword"]}'
            done, result = self.database.runQuery(query)

            # for each children add it to the graph, create a link between the parent and the child and recursive on the function
            for index, nextKeywords in enumerate(result.records()):
                nextKeyword = nextKeywords.values()[0]
                nextTag = TagItem(keyword=nextKeyword, databaseInfo=self.database.schema)

                graph.add_node(nextKeyword, tag =nextTag)
                graph.add_edge(currentKeyword, nextKeyword)
                graph = children_hierarchy(nextTag, graph)

            return graph


        def parent_hierarchy(currentTag, graph):
            """Recursive function
            Create the networkx graph the represent the parent hierarchy of the given TAGITEM
            Only works for the item tag right now

            Parameters
            ----------
            currentTag :
                the TAGITEM form the graph will be created
            graph :
                the graph with all the relationship and the node

            Returns
            -------
            type
                the graph with a new Node

            """

            currentKeyword = currentTag._get_keyword()

            #create and send a query to the database to get the children of the current node
            query = f'MATCH {currentTag.cypher_tag_keyword("current")}<-[{self.database.schema["edges"]["item-item"]}]-({currentTag.cypher_itemTag_label("next")})'
            query += f'\nRETURN next.{self.database.schema["tag"]["properties"]["keyword"]}'
            done, result = self.database.runQuery(query)

            # for each children add it to the graph, create a link between the parent and the child and recursive on the function
            for index, nextKeywords in enumerate(result.records()):
                nextKeyword = nextKeywords.values()[0]
                nextTag = TagItem(keyword=nextKeyword, databaseInfo=self.database.schema)

                graph.add_node(nextKeyword, tag =nextTag)
                graph.add_edge(nextKeyword, currentKeyword)
                graph = parent_hierarchy(nextTag, graph)

            return graph

        graphs = []
        for currentKeyword in self.tag_item._get_keyword():
            currentTag = TagItem(keyword=currentKeyword, databaseInfo=self.database.schema)
            gChild = nx.DiGraph()
            gParent = nx.DiGraph()

            if parent:
                gParent.add_node(currentKeyword, tag=currentTag)
                gParent = parent_hierarchy(currentTag, gParent)

            if child:
                gChild.add_node(currentKeyword, tag=currentTag)
                gChild = children_hierarchy(currentTag, gChild)

            tuple = (gParent, gChild)
            graphs.append(tuple)

        return graphs


    def cypher_filterDatabase(self, variable_issue="issue", variable_machine="machine", variable_type="machine_type",
                              variable_human="human", variable_operator="operator", variable_technician="technician",
                              variable_tag="tag", variable_tagOnGram="onegram_tag", variable_tagItem="tag_item",
                              variable_tagItemAsProblem="tag_itemAsProblem", variable_tagItemAsSolution="tag_itemAsSolution",
                              variable_tagProblem="tag_problem", variable_tagSolution="tag_solution",
                              variable_tagUnknown="tag_unknown", variable_tagNGram="ngram_tag",
                              variable_tagProblemItem="problemitem_tag", variable_tagSolutionItem="solutionitem_tag"):
        """Create a Cypher Query used to simply filter the database and return that query

        Parameters
        ----------
        variable_issue :
            default "issue" to refer to a special node
        variable_machine :
            default "machine" to refer to a special node
        variable_type :
            default "machine_type" to refer to a special node
        variable_human :
            default "human" to refer to a special node
        variable_operator :
            default "operator" to refer to a special node
        variable_technician :
            default "technician" to refer to a special node
        variable_tag :
            default "tag" to refer to a special node
        variable_tagOnGram :
            default "onegram_tag" to refer to a special node
        variable_tagItem :
            default "tag_item" to refer to a special node
        variable_tagItemAsProblem :
            default "tag_itemAsProblem" to refer to a special node
        variable_tagItemAsSolution :
            default "tag_itemAsSolution" to refer to a special node
        variable_tagProblem :
            default "tag_problem" to refer to a special node
        variable_tagSolution :
            default "tag_solution" to refer to a special node
        variable_tagUnknown :
            default "tag_unknown" to refer to a special node
        variable_tagNGram :
            default "ngram_tag" to refer to a special node
        variable_tagProblemItem :
            default "problemitem_tag" to refer to a special node
        variable_tagSolutionItem :
            default "solutionitem_tag" to refer to a special node

        Returns
        -------
        type
            a string - Cypher Query
            MATCH (node:LABEL)
            MATCH ...
            WHERE node.property = "X" AND node.property = "Y"
            RETURN node.property

        """

        queryMatch=[]
        queryWhere=[]
        queryReturn=[]

        m = f'({self.issue.cypher_issue_label(variable_issue)})'
        queryMatch.append(m)

        if self.issue:
            print("issue")
            w,r = self.issue.cypher_issue_whereReturn(variable_issue)
            queryWhere += w
            queryReturn += r

        if self.machine:
            print("machine")
            m = f'({variable_issue})-[{self.database.schema["edges"]["issue-machine"]}]->({self.machine.cypher_machine_label(variable_machine)})'
            w, r = self.machine.cypher_machine_whereReturn(variable_machine)
            if self.machine._get_machine_type():
                m += f'-[{self.database.schema["edges"]["machine-machinetype"]}]->({self.machine.cypher_machinetype_label(variable_type)})'
                tmp = self.machine.cypher_machinetype_whereReturn(variable_type)
                w += tmp[0]
                r = tmp[1]

            queryMatch.append(m)
            queryWhere += w
            queryReturn += r

        if self.human:
            print("human")
            m= f'({variable_issue})-->({self.human.cypher_human_label(variable_human)})'
            w, r = self.human.cypher_human_whereReturn(variable_human)

            queryMatch.append(m)
            queryWhere += w
            queryReturn += r

        if self.technician:
            print("technician")
            m = f'({variable_issue})-[{self.database.schema["edges"]["issue-technician"]}]->({self.technician.cypher_technician_label(variable_technician)})'
            w,r= self.technician.cypher_technician_whereReturn(variable_technician)
            queryMatch.append(m)
            queryWhere += w
            queryReturn += r

        if self.operator:
            print("operator")
            m = f'({variable_issue})-[{self.database.schema["edges"]["issue-operator"]}]->({self.operator.cypher_operator_label(variable_operator)})'
            w, r = self.operator.cypher_operator_whereReturn(variable_operator)
            queryMatch.append(m)
            queryWhere += w
            queryReturn += r

        if self.tag:
            print("tag")
            m = f'({variable_issue})-->({self.tag.cypher_tag_label(variable_tag)})'
            w, r = self.tag.cypher_tag_whereReturn(variable_tag)
            queryMatch.append(m)
            queryWhere += w
            queryReturn += r

        if self.tag_oneGram:
            print("tag_oneGram")
            m= f'({variable_issue})-->({self.tag_oneGram.cypher_oneGramTag_label(variable_tagOnGram)})'
            w, r = self.tag_oneGram.cypher_oneGramTag_whereReturn(variable_tagOnGram)
            queryMatch.append(m)
            queryWhere += w
            queryReturn += r

        if self.tag_item:
            print("tag_item")
            m= f'({variable_issue})-[{self.database.schema["edges"]["issue-item"]}]->({self.tag_item.cypher_itemTag_label(variable_tagItem)})'
            w, r = self.tag_item.cypher_itemTag_whereReturn(variable_tagItem)
            queryMatch.append(m)
            queryWhere += w
            queryReturn += r

        if self.tag_itemAsProblem:
            print("tag_itemAsProblem")
            m= f'({variable_issue})-[{self.database.schema["edges"]["issue-itemasproblem"]}]->({self.tag_itemAsProblem.cypher_itemTag_label(variable_tagItemAsProblem)})'
            w, r = self.tag_itemAsProblem.cypher_itemTag_whereReturn(variable_tagItemAsSProblem)
            queryMatch.append(m)
            queryWhere += w
            queryReturn += r

        if self.tag_itemAsSolution:
            print("tag_itemAsSolution")
            m= f'({variable_issue})-[{self.database.schema["edges"]["issue-itemassolution"]}]->({self.tag_itemAsSolution.cypher_itemTag_label(variable_tagItemAsSolution)})'
            w, r = self.tag_itemAsSolution.cypher_itemTag_whereReturn(variable_tagItemAsSolution)
            queryMatch.append(m)
            queryWhere += w
            queryReturn += r

        if self.tag_problem:
            print("tag_problem")
            m= f'({variable_issue})-[{self.database.schema["edges"]["issue-problem"]}]->({self.tag_problem.cypher_problemTag_label(variable_tagProblem)})'
            w, r = self.tag_problem.cypher_problemTag_whereReturn(variable_tagProblem)
            queryMatch.append(m)
            queryWhere += w
            queryReturn += r

        if self.tag_solution:
            print("tag_solution")
            m= f'({variable_issue})-[{self.database.schema["edges"]["issue-solution"]}]->({self.tag_solution.cypher_solutionTag_label(variable_tagSolution)})'

            w, r = self.tag_solution.cypher_solutionTag_whereReturn(variable_tagSolution)
            queryMatch.append(m)
            queryWhere += w
            queryReturn += r

        if self.tag_unknown:
            print("tag_unknown")
            m= f'({variable_issue})-[{self.database.schema["edges"]["issue-unknown"]}]->({self.tag_unknown.cypher_unknownTag_label(variable_tagUnknown)})'

            w, r= self.tag_unknown.cypher_unknownTag_whereReturn(variable_tagUnknown)
            queryMatch.append(m)
            queryWhere += w
            queryReturn += r

        if self.tag_nGram:
            print("tag_nGram")
            m= f'({variable_issue})-->({self.tag_nGram.cypher_nGramTag_label(variable_tagNGram)})'

            w, r= self.tag_nGram.cypher_nGramTag_whereReturn(variable_tagNGram)
            queryMatch.append(m)
            queryWhere += w
            queryReturn += r

        if self.tag_problemItem:
            print("tag_problemItem")
            m= f'({variable_issue})-[{self.database.schema["edges"]["issue-problemitem"]}]->({self.tag_problemItem.cypher_problemItemTag_label(variable_tagProblemItem)})'

            w, r = self.tag_problemItem.cypher_problemItemTag_whereReturn(variable_tagProblemItem)
            queryMatch.append(m)
            queryWhere += w
            queryReturn += r

        if self.tag_solutionItem:
            print("tag_solutionItem")
            m= f'({variable_issue})-[{self.database.schema["edges"]["issue-solutionitem"]}]->({self.tag_solutionItem.cypher_solutionItemTag_label(variable_tagSolutionItem)})'

            w, r = self.tag_solutionItem.cypher_solutionItemTag_whereReturn(variable_tagSolutionItem)
            queryMatch.append(m)
            queryWhere += w
            queryReturn += r

        # TODO if the dict is all null nothing will run
        # print("match ---------" ,queryMatch)
        # print("where ------------ ",queryWhere)
        # print("return ----------- ",queryReturn)
        if queryReturn:
            query = f'MATCH {", ".join(queryMatch)}'
            if queryWhere:
                query += f'\nWHERE {" OR ".join(queryWhere)}'
            query += f'\nRETURN {", ".join(queryReturn)}'
            self.query = query
            return query
        else:
            return ""
