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

from  database_storage.helper import getListIndexDataframe


def cypherCreate_historicalMaintenanceWorkOrder(schema, originalDataframe, propertyToHeader_dict):

    def create_issue(row, propertyToHeader_issue, schema):
        """
        Create the Object ISSUE from a row in the dataframe that represent the READABLECSV created by the key.py file

        :param row: a row from the dataframe that represent a whole MaintemanceWorkOrder from the CSV file
        :param propertyToHeader_issue: a dictionaries that link the header of the CSV data to the properties of the object
        :return: an ISSUE object or None if something goes wrong
        """

        issue = None

        try:
            # print("----------")
            # print(row)
            # print(propertyToHeader_dict)
            # print(schema)
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
        charsplit = '/'
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

                try:
                    machine._set_manufacturer(row[propertyToHeader_machine['machine']['manufacturer']])
                except KeyError:
                    pass

                try:
                    machine._set_machine_type(row[propertyToHeader_machine['machine']['type']])
                except KeyError:
                    pass

                try:
                    machine._set_locasion(row[propertyToHeader_machine['machine']['locasion']])
                except KeyError:
                    pass

        except KeyError:
            pass

        return machine

    queries = []
    for index, row in tqdm(originalDataframe.iterrows(), total=originalDataframe.shape[0]):
        issue = create_issue(row, propertyToHeader_dict, schema)
        if issue is not None:
            issue._set_id(index)
        machine = create_machine(row, propertyToHeader_dict, schema)
        operators = create_operators(row, propertyToHeader_dict, schema)
        technicians = create_technicians(row, propertyToHeader_dict, schema)

        mwo = MaintenanceWorkOrder(issue=issue,
                                   machine=machine,
                                   operators=operators,
                                   technicians=technicians,
                                   databaseSchema=schema
                                   )

        queries.append(mwo.cypher_mwo_createIssueOtherRelationship())

    return queries


def cypherCreate_tag(schema, dataframe, vocab1g=None, vocabNg=None, allTag=False):
    """
    create the query for all the tages, and link it to the given issue
    :param binnaryDataframe:
    :return:
    """


    def toSpecialtag(keyword, synonyms, classification):
        """
        Create a tag object from the type based on the classification
        :param keyword: the name of the tag
        :param classification: the type of tag I=Item, P=Problem, S=Solution, U=Unknown, S I=SolutionItem, P I=ProblemItem
        :return:
        """

        if classification == "I":
            return TagItem(keyword=keyword, synonyms=synonyms, databaseInfo=schema).cypher_itemTag_all("tag"), \
                   schema["edges"]["issue-item"]
        if classification == "S":
            return TagSolution(keyword=keyword, synonyms=synonyms, databaseInfo=schema).cypher_solutionTag_all("tag"),\
                   schema["edges"]["issue-solution"]
        if classification == "P":
            return TagProblem(keyword=keyword, synonyms=synonyms, databaseInfo=schema).cypher_problemTag_all("tag"),\
                   schema["edges"]["issue-problem"]
        if classification == "U":
            return TagUnknown(keyword=keyword, synonyms=synonyms, databaseInfo=schema).cypher_unknownTag_all("tag"), \
                   schema["edges"]["issue-unknown"]
        if classification == "S I":
            return TagSolutionItem(keyword=keyword, synonyms=synonyms, databaseInfo=schema).cypher_solutionItemTag_all("tag"), \
                   schema["edges"]["issue-solutionitem"]
        if classification == "P I":
            return TagProblemItem(keyword=keyword, synonyms=synonyms, databaseInfo=schema).cypher_problemItemTag_all("tag"), \
                   schema["edges"]["issue-problemitem"]
        if classification == "NA":
            return TagNA(keyword=keyword, synonyms=synonyms, databaseInfo=schema).cypher_naTag_all("tag"), \
                   schema["edges"]["issue-na"]
        if classification == "X":
            return TagStopWord(keyword=keyword, synonyms=synonyms, databaseInfo=schema).cypher_stopWordTag_all("tag"), \
                   schema["edges"]["issue-stopword"]
        return None, None

    queries = []
    issue = Issue(databaseInfo=schema)

    if allTag:
        df = dataframe
    else:
        df = dataframe.drop('NA', axis=1, level=0).drop('X', axis=1, level=0)

    for classification, keyword in tqdm(df, total=df.shape[1]):

        if vocab1g is not None:
            vocabs = vocab1g.append(vocabNg)
            synonyms = vocabs[vocabs["alias"] == keyword].index.values.tolist()
        elif vocabNg is not None:
            vocabs = vocabNg.append(vocab1g)
            synonyms = vocabs[vocabs["alias"] == keyword].index.values.tolist()
        else:
            synonyms = None

        cypherTag, linkType = toSpecialtag(keyword, synonyms, classification)
        if cypherTag:
            mwoIds = getListIndexDataframe(df, keyword, classification)
            query = f'\nMATCH {issue.cypher_issue_all("issue")}' \
                    f'\nWHERE issue.{issue.databaseInfoIssue["properties"]["id"]} IN {mwoIds}' \
                    f'\nMERGE {cypherTag}' \
                    f'\nMERGE (issue)-[{linkType}]->(tag)'

            queries.append(query)

    return queries


def cypherLink_Ngram1gram(schema):

    queries = []

    problemItem = TagProblemItem(databaseInfo=schema)
    solutionItem = TagSolutionItem(databaseInfo=schema)
    item = TagItem(databaseInfo=schema)
    problem = TagProblem(databaseInfo=schema)
    solution = TagSolution(databaseInfo=schema)
    unknown = TagUnknown(databaseInfo=schema)

    query = f'\nMATCH (problemitem{problemItem.label})' \
            f'\nWITH problemitem, split(problemitem.{schema["tag"]["properties"]["keyword"]}, " ") AS halfTags' \
            f'\nUNWIND halfTags AS halfTag' \
            f'\nMATCH (problem{problem.label}{{{schema["tag"]["properties"]["keyword"]}: halfTag}})' \
            f'\nMERGE (problemitem)-[{schema["edges"]["problemitem-problem"]}]->(problem)'
    queries.append(query)

    query = f'\nMATCH (problemitem{problemItem.label})' \
            f'\nWITH problemitem, split(problemitem.{schema["tag"]["properties"]["keyword"]}, " ") AS halfTags' \
            f'\nUNWIND halfTags AS halfTag' \
            f'\nMATCH (item{item.label}{{{schema["tag"]["properties"]["keyword"]}: halfTag}})' \
            f'\nMERGE (problemitem)-[{schema["edges"]["problemitem-item"]}]->(item)'
    queries.append(query)

    query = f'\nMATCH (problemitem{problemItem.label})' \
            f'\nWITH problemitem, split(problemitem.{schema["tag"]["properties"]["keyword"]}, " ") AS halfTags' \
            f'\nUNWIND halfTags AS halfTag' \
            f'\nMATCH (unknown{unknown.label}{{{schema["tag"]["properties"]["keyword"]}: halfTag}})' \
            f'\nMERGE (problemitem)-[{schema["edges"]["problemitem-unknown"]}]->(unknown)'
    queries.append(query)


    query = f'\nMATCH (solutionItem{solutionItem.label})' \
            f'\nWITH solutionItem, split(solutionItem.{schema["tag"]["properties"]["keyword"]}, " ") AS halfTags' \
            f'\nUNWIND halfTags AS halfTag' \
            f'\nMATCH (solution{solution.label}{{{schema["tag"]["properties"]["keyword"]}: halfTag}})' \
            f'\nMERGE (solutionItem)-[{schema["edges"]["solutionitem-solution"]}]->(solution)'
    queries.append(query)

    query = f'\nMATCH (solutionItem{solutionItem.label})' \
            f'\nWITH solutionItem, split(solutionItem.{schema["tag"]["properties"]["keyword"]}, " ") AS halfTags' \
            f'\nUNWIND halfTags AS halfTag' \
            f'\nMATCH (item{item.label}{{{schema["tag"]["properties"]["keyword"]}: halfTag}})' \
            f'\nMERGE (solutionItem)-[{schema["edges"]["solutionitem-item"]}]->(item)'
    queries.append(query)

    query = f'\nMATCH (solutionItem{problemItem.label})' \
            f'\nWITH solutionItem, split(solutionItem.{schema["tag"]["properties"]["keyword"]}, " ") AS halfTags' \
            f'\nUNWIND halfTags AS halfTag' \
            f'\nMATCH (unkknown{unknown.label}{{{schema["tag"]["properties"]["keyword"]}: halfTag}})' \
            f'\nMERGE (solutionItem)-[{schema["edges"]["solutionitem-unknown"]}]->(unknown)'
    queries.append(query)

    return queries


def cypherLink_itemIssue(schema):

    queries= []

    issue= Issue(databaseInfo=schema)
    problemItem = TagProblemItem(databaseInfo=schema)
    solutionItem = TagSolutionItem(databaseInfo=schema)
    item = TagItem(databaseInfo=schema)

    query = f'\nMATCH (issue{issue.label})-[{schema["edges"]["issue-problemitem"]}]->(problemitem{problemItem.label})' \
            f'\nMATCH (issue)-[{schema["edges"]["issue-item"]}]->(item{item.label})' \
            f'\nWHERE (problemitem)-[{schema["edges"]["problemitem-item"]}]->(item)' \
            f'\nMERGE (issue)-[{schema["edges"]["issue-itemasproblem"]}]->(item)'
    queries.append(query)


    query = f'\nMATCH (issue{issue.label})-[{schema["edges"]["issue-solutionitem"]}]->(solutionitem{solutionItem.label})' \
            f'\nMATCH (issue)-[{schema["edges"]["issue-item"]}]->(item{item.label})' \
            f'\nWHERE (solutionitem)-[{schema["edges"]["solutionitem-item"]}]->(item)' \
            f'\nMERGE (issue)-[{schema["edges"]["issue-itemassolution"]}]->(item)'
    queries.append(query)

    return queries


def cypherCreate_itemsTree(schema, current, queries=[]):

    item = TagItem(databaseInfo=schema)

    for children in current["children"]:
        query =  f'\nMATCH (parent{item.label}{{{schema["tag"]["properties"]["keyword"]}:"{current["keyword"]}"}})' \
                 f'\nMATCH (child{item.label}{{{schema["tag"]["properties"]["keyword"]}:"{children["keyword"]}"}})'
        if "approved" in children:
            query += f'\nMERGE (parent)-[{schema["edges"]["item-item"]}{{{schema["tag"]["properties"]["approved"]}:{children["approved"]}}}]->(child)'
        else:
            query += f'\nMERGE (parent)-[{schema["edges"]["item-item"]}]->(child)'
        queries.append(query)
        if "children" in children:
            cypherCreate_itemsTree(schema, children, queries)
            
        print(query)

    return queries
