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



from database_storage.objects.human import *
from database_storage.objects.issue import *
from database_storage.objects.maintenanceworkorder import *
from database_storage.objects.tag import *
from tqdm import tqdm

from database_storage.objects.machine import *

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

    def create_issue(row,propertyToHeader_issue):
        """
        Create the Object ISSUE from a row in the dataframe that represent the READABLECSV created by the key.py file

        :param row: a row from the dataframe that represent a whole MaintemanceWorkOrder from the CSV file
        :param propertyToHeader_issue: a dictionaries that link the header of the CSV data to the properties of the object
        :return: an ISSUE object or None if something goes wrong
        """

        issue = None

        try:
            issue = Issue(problem=row[propertyToHeader_issue['description_problem']],
                          solution=row[propertyToHeader_issue['description_solution']],
                          databaseInfo=database.schema)
            try:
                issue._set_cause(row[propertyToHeader_issue['description_cause']])
            except KeyError:
                pass
            try:
                issue._set_effects(row[propertyToHeader_issue['description_effect']])
            except KeyError:
                pass
            try:
                issue._set_part_in_process(row[propertyToHeader_issue['part_in_process']])
            except KeyError:
                pass
            try:
                issue._set_necessary_part(row[propertyToHeader_issue['necessary_part']])
            except KeyError:
                pass
            try:
                issue._set_machine_down(row[propertyToHeader_issue['machine_down']])
            except KeyError:
                pass
            try:
                issue._set_cost(row[propertyToHeader_issue['cost']])
            except KeyError:
                pass
            #TODO add a date clenizer for only 1 value
            try:
                issue._set_date_machine_down(row[propertyToHeader_issue['date_machine_down']])
            except KeyError:
                pass
            try:
                issue._set_date_machine_up(row[propertyToHeader_issue['date_machine_up']])
            except KeyError:
                pass
            try:
                issue._set_date_workorder_completion(row[propertyToHeader_issue['date_workorder_completion']])
            except KeyError:
                pass
            try:
                issue._set_date_workorder_start(row[propertyToHeader_issue['date_workorder_start']])
            except KeyError:
                pass
            try:
                issue._set_date_maintenance_technician_arrive(row[propertyToHeader_issue['date_maintenance_technician_arrive']])
            except KeyError:
                pass
            try:
                issue._set_date_problem_solve(row[propertyToHeader_issue['date_problem_solve']])
            except KeyError:
                pass
            try:
                issue._set_date_problem_found(row[propertyToHeader_issue['date_problem_found']])
            except KeyError:
                pass
            try:
                issue._set_date_part_ordered(row[propertyToHeader_issue['date_part_ordered']])
            except KeyError:
                pass
            try:
                issue._set_date_part_received(row[propertyToHeader_issue['date_part_received']])
            except KeyError:
                pass

        except KeyError:
            pass
        return issue

    def create_technicians(row, propertyToHeader_technician):
        """
        Create an array of TECHNICIAN Objects from a row in the dataframe that represent the READABLECSV created by the key.py file

        :param row: a row from the dataframe that represent a whole MaintemanceWorkOrder from the CSV file
        :param propertyToHeader_technician: a dictionaries that link the header of the CSV data to the properties of the object
        :return: an array of TECNICIANs empty if something goes wrong or if there are not technician un the csv
        """
        charsplit = "/"
        skills = []
        try:
            for skill in row[propertyToHeader_technician['skills']].split(charsplit):
                skills.append(skill)
        except KeyError:
            pass

        crafts = []
        try:
            for craft in row[propertyToHeader_technician['crafts']].split(charsplit):
                crafts.append(craft)
        except KeyError:
            pass

        technicians = []
        try:
            if row[propertyToHeader_technician['name']]:
                for name in row[propertyToHeader_technician['name']].split(charsplit):
                    technicians.append(Technician(name=name, skills=skills, crafts=crafts, databaseInfo=database.schema))
        except KeyError:
            pass

        return technicians

    def create_operators(row,propertyToHeader_operator):
        """
        Create an array of OPERATOR Objects from a row in the dataframe that represent the READABLECSV created by the key.py file

        :param row: a row from the dataframe that represent a whole MaintemanceWorkOrder from the CSV file
        :param propertyToHeader_operator: a dictionaries that link the header of the CSV data to the properties of the object
        :return: an array of OPERATORs empty if something goes wrong or if there are not operators un the csv
        """
        charsplit = "/"
        operators = []
        try:
            if row[propertyToHeader_operator['name']]:
                for name in row[propertyToHeader_operator['name']].split(charsplit):
                    operators.append(Operator(name=name, databaseInfo=database.schema))
        except KeyError:
            pass

        return operators

    def create_machine(row, propertyToHeader_machine):
        """
        Create a MACHINE Objects from a row in the dataframe that represent the READABLECSV created by the key.py file

        :param row: a row from the dataframe that represent a whole MaintemanceWorkOrder from the CSV file
        :param propertyToHeader_machine: a dictionaries that link the header of the CSV data to the properties of the object
        :return:an MACHINE object or None if something goes wrong or if there are not machine un the csv
        """

        machine = None

        try:
            if row[propertyToHeader_machine['name']]:
                machine = Machine(name=row[propertyToHeader_machine['name']], databaseInfo=database.schema)
                #print(row[propertyToHeader_machine['name']])

                try:
                    machine._set_manufacturer(row[propertyToHeader_machine['manufacturer']])
                    #print(row[propertyToHeader_machine['manufacturer']])
                except KeyError:
                    pass

                try:
                    machine._set_machine_type(row[propertyToHeader_machine['type']])
                    #print(row[propertyToHeader_machine['type']])
                except KeyError:
                    pass

                try:
                    machine._set_locasion(row[propertyToHeader_machine['locasion']])
                    #print(row[propertyToHeader_machine['locasion']])
                except KeyError:
                    pass

        except KeyError:
            pass

        return machine

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
            if row[propertyToHeader_item["keyword"]]:
                for item in row[propertyToHeader_item["keyword"]].split(charsplit):
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
            if row[propertyToHeader_problem["keyword"]]:
                for problem in row[propertyToHeader_problem["keyword"]].split(charsplit):
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
            if row[propertyToHeader_solution["keyword"]]:
                for solution in row[propertyToHeader_solution["keyword"]].split(charsplit):
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
            if row[propertyToHeader_unknown["keyword"]]:
                for unknown in row[propertyToHeader_unknown["keyword"]].split(charsplit):
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
            if row[propertyToHeader_problemItem["keyword"]]:
                for problemItem in row[propertyToHeader_problemItem["keyword"]].split(charsplit):
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
            if row[propertyToHeader_solutionItem["keyword"]]:
                for solutionItem in row[propertyToHeader_solutionItem["keyword"]].split(charsplit):
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
        issue = create_issue(row, propertyToHeader_dict['issue'])
        machine = create_machine(row, propertyToHeader_dict['machine'])
        operators = create_operators(row, propertyToHeader_dict['operator'])
        technicians = create_technicians(row, propertyToHeader_dict['technician'])
        items = create_items(row, propertyToHeader_dict['item'])
        problems = create_problems(row, propertyToHeader_dict['problem'])
        solutions = create_solutions(row, propertyToHeader_dict['solution'])
        unknowns = create_unknowns(row, propertyToHeader_dict['unknown'])
        problemItems = create_problemItems(row, propertyToHeader_dict['problemitem'])
        solutionItems = create_solutionItems(row, propertyToHeader_dict['solutionitem'])

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

        #link each TagNGram with his composed OneGram
        queries += mwo.cypher_mwo_createNgram1GramRelationaship()

        #link each item to his parents
        #for the example we will assume that and ITEM_ITEM is composed of two ITEMs
        newItems = TODO_inagine_linkedItem(items)
        # for i in mwo.tag_items:
        #     print(i)
        queries += mwo.cypher_mwo_createItemItemRelationaship()


        #link the Item to Issue based on PROBLEM or SOLUTION
        queries += mwo.cypher_mwo_updateIssueItemRelationaship()


        #run the query into the database

        for query in queries:
            #print(query)
            done, result = database.runQuery(query)
            if not done:
                print(query)
                print("ERROR on Maintenance Work Order ", index, "\tOn query", query, "\n\n")

    return 1


