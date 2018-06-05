"""
File: helper.py
Name: Sascha MOCCOZET
Organisation:
    Departament of Commerce USA
    National Institute of Standards and Technology - NIST
    Engineering Laboratory - EL
    Systems Integration Division - SID
    Information Modeling and Testing Group - IMTG
    <Insert Project Name>
Description:
    This file contains several function that allow to import different type of CSV
    into a Graph Database using Cypher Queries
    Originally created to store Maintenance Work Order for Manufacturing, it should be totally modular
    but will respect the graph schema created to solve our problem.
"""

from tqdm import tqdm

from database_storage.objects.human import *
from database_storage.objects.issue import *
from database_storage.objects.maintenanceworkorder import *
from database_storage.objects.tag import *
from database_storage.objects.machine import *

from  database_storage.helper import getListIndexDataframe, getListIndexDataframe

charsplit = ','
def graphDatabase_from_TaggedCSV(database, dataframe, propertyToHeader_dict):
    """
    This function is used to import a certain kind of CSV data into the graph database
    The data should follow this structure but doesn't have to contains all the headers.
    The header's name are define by the input -propertyToHeader_dict- :
        * Maintenance Work order specific information:
            - description_of_problem
            - description_of_solution
            - description_of_cause
            - description_of_effect
            - machine_down
            - necessary_part
            - part_in_process
            - cost
            - date_machine_down
            - date_maintenanceworkorder_start
            - date_maintenance_technician_arrive
            - date_problem_found
            - date_part_ordered
            - date_part_received
            - date_problem_solve
            - date_machine_up
            - date_maintenanceworkorder_completion
        Technician information:
            - name
            - skills
            - crafts
        Operator information:
            - name
        Machine information:
            - name
            - manufacturer
            - location
            - type
        Tag Item, Tag Solution, Tag Problem, Tag Unknown, Tag ProblemItem, Tag SolutionItem Infornations:
            - keyword
            - synonyms

    In our case, the Tag informations are extracted using the KeyWordExtractor module we created for this purpose
    Or the tagging App (UI created in front end to extract the tag)

    To see an example of this CSV, you can see the OpenSource Public Mining Data <Refer to Melinda's project>



    :param database: Database object from the module database_storage.database.database
    :param dataframe: Dataframe object from the Pandas Library - represent the of the CSV file -
        See example of the CSV in data/mine_data/csvHeader.yaml
    :param propertyToHeader_dict: dictionary which match the header of the Dataframe (and so tha csv file)
        to the database property and node see example in the file data/mine_data/mine_raw.csv
    :return: 1 when the function has been executed with success - your data are now in your graph database -
    """

    def create_items(row, propertyToHeader_item):
        """
        Create an array of TAGITEMS Objects from a row in the dataframe that represent the READABLECSV created by the key.py file

        :param row: a row from the dataframe that represent a whole MaintemanceWorkOrder from the CSV file
        :param propertyToHeader_item: a dictionaries that link the header of the CSV data to the properties of the object
        :return: an array of TAGITEMS empty if something goes wrong or if there are not item_tag un the csv
        """
        charsplit = ','
        items = []

        try:
            if row[propertyToHeader_item['item']["keyword"]]:
                for item in row[propertyToHeader_item['item']["keyword"]].split(charsplit):
                    items.append(TagItem(keyword=item, databaseInfo=database.schema))
        except KeyError:
            pass

        return items

    def create_problems(row, propertyToHeader_problem):
        """
        Create an array of TAGPROBLEM Objects from a row in the dataframe that represent the READABLECSV created by the key.py file

        :param row: a row from the dataframe that represent a whole MaintemanceWorkOrder from the CSV file
        :param propertyToHeader_problem: a dictionaries that link the header of the CSV data to the properties of the object
        :return: an array of TAGPROBLEM empty if something goes wrong or if there are not problem_tag un the csv
        """
        charsplit = ','
        problems = []

        try:
            if row[propertyToHeader_problem['problem']["keyword"]]:
                for problem in row[propertyToHeader_problem['problem']["keyword"]].split(charsplit):
                    problems.append(TagProblem(keyword=problem, databaseInfo=database.schema))
        except KeyError:
            pass

        return problems

    def create_solutions(row, propertyToHeader_solution):
        """
        Create an array of TAGSOLUTION Objects from a row in the dataframe that represent the READABLECSV created by the key.py file

        :param row: a row from the dataframe that represent a whole MaintemanceWorkOrder from the CSV file
        :param propertyToHeader_solution: a dictionaries that link the header of the CSV data to the properties of the object
        :return: an array of TAGSOLUTION empty if something goes wrong or if there are not solution_tag un the csv
        """
        charsplit = ','
        solutions = []

        try:
            if row[propertyToHeader_solution['solution']["keyword"]]:
                for solution in row[propertyToHeader_solution['solution']["keyword"]].split(charsplit):
                    solutions.append(TagSolution(keyword=solution, databaseInfo=database.schema))
        except KeyError:
            pass

        return solutions

    def create_unknowns(row, propertyToHeader_unknown):
        """
        Create an array of TAGUNKNOWNS Objects from a row in the dataframe that represent the READABLECSV created by the key.py file

        :param row: a row from the dataframe that represent a whole MaintemanceWorkOrder from the CSV file
        :param propertyToHeader_unknown: a dictionaries that link the header of the CSV data to the properties of the object
        :return: an array of TAGUNKNOWNS empty if something goes wrong or if there are not unknown_tag un the csv
        """
        charsplit = ','
        unknowns = []

        try:
            if row[propertyToHeader_unknown['unknown']["keyword"]]:
                for unknown in row[propertyToHeader_unknown['unknown']["keyword"]].split(charsplit):
                    unknowns.append(TagUnknown(keyword=unknown, databaseInfo=database.schema))
        except KeyError:
            pass

        return unknowns

    def create_problemItems(row, propertyToHeader_problemItem):
        """
        Create an array of TAGPROBLEMITEM Objects from a row in the dataframe that represent the READABLECSV created by the key.py file

        :param row: a row from the dataframe that represent a whole MaintemanceWorkOrder from the CSV file
        :param propertyToHeader_problemItem: a dictionaries that link the header of the CSV data to the properties of the object
        :return: an array of TAGPROBLEMITEM empty if something goes wrong or if there are not problemitem_tag un the csv
        """
        charsplit = ','
        problemItems = []

        try:
            if row[propertyToHeader_problemItem['problemitem']["keyword"]]:
                for problemItem in row[propertyToHeader_problemItem['problemitem']["keyword"]].split(charsplit):
                    problemItems.append(TagProblemItem(keyword=problemItem, databaseInfo=database.schema))
        except KeyError:
            pass

        return problemItems

    def create_solutionItems(row, propertyToHeader_solutionItem):
        """
        Create an array of TAGSOLUTIONITEM Objects from a row in the dataframe that represent the READABLECSV created by the key.py file

        :param row: a row from the dataframe that represent a whole MaintemanceWorkOrder from the CSV file
        :param propertyToHeader_solutionItem: a dictionaries that link the header of the CSV data to the properties of the object
        :return: an array of TAGSOLUTIONITEM empty if something goes wrong or if there are not solutionitem_tag un the csv
        """
        charsplit = ','
        solutionItems = []

        try:
            if row[propertyToHeader_solutionItem['solutionitem']["keyword"]]:
                for solutionItem in row[propertyToHeader_solutionItem['solutionitem']["keyword"]].split(charsplit):
                    solutionItems.append(TagSolutionItem(keyword=solutionItem, databaseInfo=database.schema))
        except KeyError:
            pass

        return solutionItems


    def TODO_inagine_linkedItem(items):
        """
        This function is actually used to create a child for the item and so make the ITEM --> ITEM relationship
        It is temporaly and only use to tray some queries

        It should be implemented from the user as an item hierarchy
        :param items:
        :return:
        """
        charsplit="_"
        newItems = []

        for item in items:
            if not charsplit in item._get_keyword():
                newItems.append(item)
            else:
                tmp = item._get_keyword().split(charsplit)
                item._set_children(tmp, database.schema)
                newItems.append(item)
        return newItems


    #for each row in the dataframe
    for index, row in tqdm(dataframe.iterrows(), total=dataframe.shape[0]):

        # creat the objects
        issue = create_issue(row, propertyToHeader_dict, database.schema)
        issue._set_id(index)
        machine = create_machine(row, propertyToHeader_dict, database.schema)
        operators = create_operators(row, propertyToHeader_dict, database.schema)
        technicians = create_technicians(row, propertyToHeader_dict, database.schema)
        items = create_items(row, propertyToHeader_dict)
        problems = create_problems(row, propertyToHeader_dict)
        solutions = create_solutions(row, propertyToHeader_dict)
        unknowns = create_unknowns(row, propertyToHeader_dict)
        problemItems = create_problemItems(row, propertyToHeader_dict)
        solutionItems = create_solutionItems(row, propertyToHeader_dict)

        #create a Maintenance Work Order object from the object above
        mwo = MaintenanceWorkOrder(issue = issue,
                                   machine = machine,
                                   operators = operators,
                                   technicians = technicians,
                                   tag_items = items,
                                   tag_problems = problems,
                                   tag_solutions = solutions,
                                   tag_unknowns = unknowns,
                                   tag_problemItems = problemItems,
                                   tag_solutionsItems = solutionItems,
                                   databaseInfo=database.schema
        )

        queries = []
        #create nodes and the relationship between issue and node
        queries.append(mwo.cypher_mwo_createIssueOtherRelationship())

        # #link each TagNGram with his composed OneGram
        # queries += mwo.cypher_mwo_createNgram1GramRelationaship()
        #
        # #link each item to his parents
        # #for the example we will assume that and ITEM_ITEM is composed of two ITEMs
        # newItems = TODO_inagine_linkedItem(items)
        # # for i in mwo.tag_items:
        # #     print(i)
        # queries += mwo.cypher_mwo_createItemItemRelationaship()
        #
        #
        # #link the Item to Issue based on PROBLEM or SOLUTION
        # queries += mwo.cypher_mwo_updateIssueItemRelationaship()


        #run the query into the database

        for query in queries:
            #print(query)
            done, result = database.runQuery(query)
            if not done:
                print(query)
                #print("ERROR on Maintenance Work Order ", index, "\tOn query", query, "\n\n")

    return 1



def graphDatabase_from_binnaryCSV(database, originalDataframe, binnaryDataframe, binnaryRelationshipDataframe, propertyToHeader_dict):


    def cypherCreate_tags(dataframe):
        """
        create the query for all the tages, and link it to the given issue
        :param binnaryDataframe:
        :return:
        """

        def toSpecialtag(keyword, classification):
            """
            Create a tag object from the type based on the classification
            :param keyword: the name of the tag
            :param classification: the type of tag I=Item, P=Problem, S=Solution, U=Unknown, S I=SolutionItem, P I=ProblemItem
            :return:
            """

            if classification == "I":
                return TagItem(keyword=keyword, databaseInfo=database.schema), database.schema["edges"]["issue-item"]
            if classification == "S":
                return TagSolution(keyword=keyword, databaseInfo=database.schema), database.schema["edges"][
                    "issue-solution"]
            if classification == "P":
                return TagProblem(keyword=keyword, databaseInfo=database.schema), database.schema["edges"][
                    "issue-problem"]
            if classification == "U":
                return TagUnknown(keyword=keyword, databaseInfo=database.schema), database.schema["edges"][
                    "issue-unknown"]
            if classification == "S I":
                return TagSolutionItem(keyword=keyword, databaseInfo=database.schema), database.schema["edges"][
                    "issue-solutionitem"]
            if classification == "P I":
                return TagProblemItem(keyword=keyword, databaseInfo=database.schema), database.schema["edges"][
                    "issue-problemitem"]
            return None, None

        queries = []
        issue = Issue(databaseInfo=database.schema)
        df = dataframe.drop('NA', axis=1, level=0).drop('X', axis=1, level=0)
        for classification, keyword in tqdm(df, total=df.shape[1]):
            tag, linkType = toSpecialtag(keyword, classification)
            if tag:
                mwoIds = getListIndexDataframe(df, keyword, classification)
                query = f'\nMATCH {issue.cypher_issue_all("issue")}' \
                        f'\nWHERE issue.{issue.databaseInfoIssue["properties"]["id"]} IN {mwoIds}' \
                        f'\nMERGE (tag{tag.label} {{{tag.databaseInfoTag["properties"]["keyword"]}: \'{keyword}\'}})' \
                        f'\nMERGE (issue)-[{linkType}]->(tag)' \
                        f'\nRETURN 1'

                queries.append(query)

        return queries



    def cypherCreate_originalData(database, originalDataframe, propertyToHeader_dict):
        """
        Create the object MWO that contains the Issue, Technician, Machine
        return a list of queries to create this maintenance work order
        :param database:
        :param originalDataframe:
        :param propertyToHeader_dict:
        :return: list of Cypher queries to create the mwo
        """

        queries = []
        for index, row in tqdm(originalDataframe.iterrows(), total=originalDataframe.shape[0]):
            issue = create_issue(row, propertyToHeader_dict, database.schema)
            issue._set_id(index)
            machine = create_machine(row, propertyToHeader_dict, database.schema)
            operators = create_operators(row, propertyToHeader_dict, database.schema)
            technicians = create_technicians(row, propertyToHeader_dict, database.schema)

            mwo = MaintenanceWorkOrder(issue=issue,
                                       machine=machine,
                                       operators=operators,
                                       technicians=technicians,
                                       databaseInfo=database.schema
                                       )

            queries.append(mwo.cypher_mwo_createIssueOtherRelationship())

        return queries

    def cypherCreateLink_1GramNgram(database):

        queries = []

        problemItem = TagProblemItem(databaseInfo=database.schema)
        solutionItem = TagSolutionItem(databaseInfo=database.schema)
        item = TagItem(databaseInfo=database.schema)
        problem = TagProblem(databaseInfo=database.schema)
        solution = TagSolution(databaseInfo=database.schema)
        unknown = TagUnknown(databaseInfo=database.schema)

        query = f'\nMATCH (problemitem{problemItem.label})' \
                f'\nWITH problemitem, split(problemitem.{database.schema["tag"]["properties"]["keyword"]}, " ") AS halfTags' \
                f'\nUNWIND halfTags AS halfTag' \
                f'\nMATCH (problem{problem.label}{{{database.schema["tag"]["properties"]["keyword"]}: halfTag}})' \
                f'\nMERGE (problemitem)-[{database.schema["edges"]["problemitem-problem"]}]->(problem)'
        queries.append(query)

        query = f'\nMATCH (problemitem{problemItem.label})' \
                f'\nWITH problemitem, split(problemitem.{database.schema["tag"]["properties"]["keyword"]}, " ") AS halfTags' \
                f'\nUNWIND halfTags AS halfTag' \
                f'\nMATCH (item{item.label}{{{database.schema["tag"]["properties"]["keyword"]}: halfTag}})' \
                f'\nMERGE (problemitem)-[{database.schema["edges"]["problemitem-item"]}]->(item)'
        queries.append(query)

        query = f'\nMATCH (problemitem{problemItem.label})' \
                f'\nWITH problemitem, split(problemitem.{database.schema["tag"]["properties"]["keyword"]}, " ") AS halfTags' \
                f'\nUNWIND halfTags AS halfTag' \
                f'\nMATCH (unknown{unknown.label}{{{database.schema["tag"]["properties"]["keyword"]}: halfTag}})' \
                f'\nMERGE (problemitem)-[{database.schema["edges"]["problemitem-unknown"]}]->(unknown)'
        queries.append(query)


        query = f'\nMATCH (solutionItem{solutionItem.label})' \
                f'\nWITH solutionItem, split(solutionItem.{database.schema["tag"]["properties"]["keyword"]}, " ") AS halfTags' \
                f'\nUNWIND halfTags AS halfTag' \
                f'\nMATCH (solution{solution.label}{{{database.schema["tag"]["properties"]["keyword"]}: halfTag}})' \
                f'\nMERGE (solutionItem)-[{database.schema["edges"]["solutionitem-solution"]}]->(solution)'
        queries.append(query)

        query = f'\nMATCH (solutionItem{solutionItem.label})' \
                f'\nWITH solutionItem, split(solutionItem.{database.schema["tag"]["properties"]["keyword"]}, " ") AS halfTags' \
                f'\nUNWIND halfTags AS halfTag' \
                f'\nMATCH (item{item.label}{{{database.schema["tag"]["properties"]["keyword"]}: halfTag}})' \
                f'\nMERGE (solutionItem)-[{database.schema["edges"]["solutionitem-item"]}]->(item)'
        queries.append(query)

        query = f'\nMATCH (solutionItem{problemItem.label})' \
                f'\nWITH solutionItem, split(solutionItem.{database.schema["tag"]["properties"]["keyword"]}, " ") AS halfTags' \
                f'\nUNWIND halfTags AS halfTag' \
                f'\nMATCH (unkknown{unknown.label}{{{database.schema["tag"]["properties"]["keyword"]}: halfTag}})' \
                f'\nMERGE (solutionItem)-[{database.schema["edges"]["solutionitem-unknown"]}]->(unknown)'
        queries.append(query)

        print(query)

        return queries


    def cypherCreateNewLink_issueItem(database):

        queries= []

        issue= Issue(databaseInfo=database.schema)
        problemItem = TagProblemItem(databaseInfo=database.schema)
        solutionItem = TagSolutionItem(databaseInfo=database.schema)
        item = TagItem(databaseInfo=database.schema)

        query = f'\nMATCH (issue{issue.label})-[{database.schema["edges"]["issue-problemitem"]}]->(problemitem{problemItem.label})' \
                f'\nMATCH (issue)-[{database.schema["edges"]["issue-item"]}]->(item{item.label})' \
                f'\nWHERE (problemitem)-[{database.schema["edges"]["problemitem-item"]}]->(item)' \
                f'\nMERGE (issue)-[{database.schema["edges"]["issue-itemasproblem"]}]->(item)'
        queries.append(query)

        query = f'\nMATCH (issue{issue.label})-[{database.schema["edges"]["issue-solutionitem"]}]->(solutionitem{solutionItem.label})' \
                f'\nMATCH (issue)-[{database.schema["edges"]["issue-item"]}]->(item{item.label})' \
                f'\nWHERE (solutionitem)-[{database.schema["edges"]["solutionitem-item"]}]->(item)' \
                f'\nMERGE (issue)-[{database.schema["edges"]["issue-itemassolution"]}]->(item)'
        queries.append(query)

        return queries


    #
    # def create_items(tags):
    #     """
    #     Create an array of TAGITEMS Objects from a row in the dataframe that represent the READABLECSV created by the key.py file
    #
    #     :param row: a row from the dataframe that represent a whole MaintemanceWorkOrder from the CSV file
    #     :param propertyToHeader_item: a dictionaries that link the header of the CSV data to the properties of the object
    #     :return: an array of TAGITEMS empty if something goes wrong or if there are not item_tag un the csv
    #     """
    #     items= []
    #     for item in tags:
    #         items.append(TagItem(keyword = item, databaseInfo=database.schema))
    #     return items
    #
    # def create_problems(tags):
    #     """
    #     Create an array of TAGPROBLEM Objects from a row in the dataframe that represent the READABLECSV created by the key.py file
    #
    #     :param row: a row from the dataframe that represent a whole MaintemanceWorkOrder from the CSV file
    #     :param propertyToHeader_problem: a dictionaries that link the header of the CSV data to the properties of the object
    #     :return: an array of TAGPROBLEM empty if something goes wrong or if there are not problem_tag un the csv
    #     """
    #     problems = []
    #     for problem in tags:
    #         problems.append(TagProblem(keyword=problem, databaseInfo=database.schema))
    #     return problems
    #
    # def create_solutions(tags):
    #     """
    #     Create an array of TAGSOLUTION Objects from a row in the dataframe that represent the READABLECSV created by the key.py file
    #
    #     :param row: a row from the dataframe that represent a whole MaintemanceWorkOrder from the CSV file
    #     :param propertyToHeader_solution: a dictionaries that link the header of the CSV data to the properties of the object
    #     :return: an array of TAGSOLUTION empty if something goes wrong or if there are not solution_tag un the csv
    #     """
    #     solutions = []
    #     for solution in tags:
    #         solutions.append(TagSolution(keyword=solution, databaseInfo=database.schema))
    #     return solutions
    #
    # def create_unknowns(tags):
    #     """
    #     Create an array of TAGUNKNOWNS Objects from a row in the dataframe that represent the READABLECSV created by the key.py file
    #
    #     :param row: a row from the dataframe that represent a whole MaintemanceWorkOrder from the CSV file
    #     :param propertyToHeader_unknown: a dictionaries that link the header of the CSV data to the properties of the object
    #     :return: an array of TAGUNKNOWNS empty if something goes wrong or if there are not unknown_tag un the csv
    #     """
    #     unknowns = []
    #     for unknown in tags:
    #         unknowns.append(TagUnknown(keyword=unknown, databaseInfo=database.schema))
    #     return unknowns
    #
    # def create_problemItems(tags):
    #     """
    #     Create an array of TAGPROBLEMITEM Objects from a row in the dataframe that represent the READABLECSV created by the key.py file
    #
    #     :param row: a row from the dataframe that represent a whole MaintemanceWorkOrder from the CSV file
    #     :param propertyToHeader_problemItem: a dictionaries that link the header of the CSV data to the properties of the object
    #     :return: an array of TAGPROBLEMITEM empty if something goes wrong or if there are not problemitem_tag un the csv
    #     """
    #     problemItems = []
    #     for problemItem in tags:
    #         problemItems.append(TagProblemItem(keyword=problemItem, databaseInfo=database.schema))
    #     return problemItems
    #
    # def create_solutionItems(tags):
    #
    #     """
    #     Create an array of TAGSOLUTIONITEM Objects from a row in the dataframe that represent the READABLECSV created by the key.py file
    #
    #     :param row: a row from the dataframe that represent a whole MaintemanceWorkOrder from the CSV file
    #     :param propertyToHeader_solutionItem: a dictionaries that link the header of the CSV data to the properties of the object
    #     :return: an array of TAGSOLUTIONITEM empty if something goes wrong or if there are not solutionitem_tag un the csv
    #     """
    #     solutionItems = []
    #     for solutionItem in tags:
    #         solutionItems.append(TagSolutionItem(keyword=solutionItem, databaseInfo=database.schema))
    #     return solutionItems

    queries = []
    queries += cypherCreate_originalData(database, originalDataframe, propertyToHeader_dict)
    print("-- Queries from the HISTORICAL dataset created !!")
    queries += cypherCreate_tags(binnaryDataframe)
    print("-- Queries from the 1GRAM TAGGED dataset created !!")
    queries += cypherCreate_tags(binnaryRelationshipDataframe)
    print("-- Queries from the NGRAM TAGGED dataset created !!")


    queries += cypherCreateLink_1GramNgram(database)
    print("-- Queries to linked 1GRAM TAG and NGRAM TAG created!!")

    queries += cypherCreateNewLink_issueItem(database)
    print("-- Queries to update ITEM TAG to ISSUE relationship created!!")




    database.runQueries(queries)
    print("-- Queries stored into the database")

    return 1


def create_issue(row, propertyToHeader_issue, schema):
    """
    Create the Object ISSUE from a row in the dataframe that represent the READABLECSV created by the key.py file

    :param row: a row from the dataframe that represent a whole MaintemanceWorkOrder from the CSV file
    :param propertyToHeader_issue: a dictionaries that link the header of the CSV data to the properties of the object
    :return: an ISSUE object or None if something goes wrong
    """

    issue = None

    try:
        issue = Issue(problem=row[propertyToHeader_issue['issue']['description_problem']],
                      databaseInfo=schema)
        try:
            issue._set_id(row[propertyToHeader_issue['issue']['id']])
        except:
            pass
        try:
            issue._set_solution(row[propertyToHeader_issue['issue']['description_solution']])
        except KeyError:
            pass
        try:
            issue._set_cause(row[propertyToHeader_issue['issue']['description_cause']])
        except KeyError:
            pass
        try:
            issue._set_effects(row[propertyToHeader_issue['issue']['description_effect']])
        except KeyError:
            pass
        try:
            issue._set_part_in_process(row[propertyToHeader_issue['issue']['part_in_process']])
        except KeyError:
            pass
        try:
            issue._set_necessary_part(row[propertyToHeader_issue['issue']['necessary_part']])
        except KeyError:
            pass
        try:
            issue._set_machine_down(row[propertyToHeader_issue['issue']['machine_down']])
        except KeyError:
            pass
        try:
            issue._set_cost(row[propertyToHeader_issue['issue']['cost']])
        except KeyError:
            pass
        # TODO add a date clenizer for only 1 value
        try:
            issue._set_date_machine_down(row[propertyToHeader_issue['issue']['date_machine_down']])
        except KeyError:
            pass
        try:
            issue._set_date_machine_up(row[propertyToHeader_issue['issue']['date_machine_up']])
        except KeyError:
            pass
        try:
            issue._set_date_workorder_completion(row[propertyToHeader_issue['issue']['date_workorder_completion']])
        except KeyError:
            pass
        try:
            issue._set_date_workorder_start(row[propertyToHeader_issue['issue']['date_workorder_start']])
        except KeyError:
            pass
        try:
            issue._set_date_maintenance_technician_arrive(
                row[propertyToHeader_issue['issue']['date_maintenance_technician_arrive']])
        except KeyError:
            pass
        try:
            issue._set_date_problem_solve(row[propertyToHeader_issue['issue']['date_problem_solve']])
        except KeyError:
            pass
        try:
            issue._set_date_problem_found(row[propertyToHeader_issue['issue']['date_problem_found']])
        except KeyError:
            pass
        try:
            issue._set_date_part_ordered(row[propertyToHeader_issue['issue']['date_part_ordered']])
        except KeyError:
            pass
        try:
            issue._set_date_part_received(row[propertyToHeader_issue['issue']['date_part_received']])
        except KeyError:
            pass

    except KeyError:
        pass
    return issue

def create_technicians(row, propertyToHeader_technician, schema):
    """
    Create an array of TECHNICIAN Objects from a row in the dataframe that represent the READABLECSV created by the key.py file

    :param row: a row from the dataframe that represent a whole MaintemanceWorkOrder from the CSV file
    :param propertyToHeader_technician: a dictionaries that link the header of the CSV data to the properties of the object
    :return: an array of TECNICIANs empty if something goes wrong or if there are not technician un the csv
    """
    charsplit = "/"
    skills = []
    try:
        for skill in row[propertyToHeader_technician['technician']['skills']].split(charsplit):
            skills.append(skill)
    except KeyError:
        pass

    crafts = []
    try:
        for craft in row[propertyToHeader_technician['technician']['crafts']].split(charsplit):
            crafts.append(craft)
    except KeyError:
        pass

    technicians = []
    try:
        if row[propertyToHeader_technician['technician']['name']]:
            for name in row[propertyToHeader_technician['technician']['name']].split(charsplit):
                technicians.append(
                    Technician(name=name, skills=skills, crafts=crafts, databaseInfo=schema))
    except KeyError:
        pass

    return technicians

def create_operators(row, propertyToHeader_operator, schema):
    """
    Create an array of OPERATOR Objects from a row in the dataframe that represent the READABLECSV created by the key.py file

    :param row: a row from the dataframe that represent a whole MaintemanceWorkOrder from the CSV file
    :param propertyToHeader_operator: a dictionaries that link the header of the CSV data to the properties of the object
    :return: an array of OPERATORs empty if something goes wrong or if there are not operators un the csv
    """
    charsplit = "/"
    operators = []
    try:
        if row[propertyToHeader_operator['operator']['name']]:
            for name in row[propertyToHeader_operator['operator']['name']].split(charsplit):
                operators.append(Operator(name=name, databaseInfo=schema))
    except KeyError:
        pass

    return operators

def create_machine(row, propertyToHeader_machine, schema):
    """
    Create a MACHINE Objects from a row in the dataframe that represent the READABLECSV created by the key.py file

    :param row: a row from the dataframe that represent a whole MaintemanceWorkOrder from the CSV file
    :param propertyToHeader_machine: a dictionaries that link the header of the CSV data to the properties of the object
    :return:an MACHINE object or None if something goes wrong or if there are not machine un the csv
    """

    machine = None

    try:
        if row[propertyToHeader_machine['machine']['name']]:
            machine = Machine(name=row[propertyToHeader_machine['machine']['name']], databaseInfo=schema)
            # print(row[propertyToHeader_machine['name']])

            try:
                machine._set_manufacturer(row[propertyToHeader_machine['machine']['manufacturer']])
                # print(row[propertyToHeader_machine['manufacturer']])
            except KeyError:
                pass

            try:
                machine._set_machine_type(row[propertyToHeader_machine['machine']['type']])
                # print(row[propertyToHeader_machine['type']])
            except KeyError:
                pass

            try:
                machine._set_locasion(row[propertyToHeader_machine['machine']['locasion']])
                # print(row[propertyToHeader_machine['locasion']])
            except KeyError:
                pass

    except KeyError:
        pass

    return machine