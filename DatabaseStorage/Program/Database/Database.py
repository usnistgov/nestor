from neo4j.v1 import GraphDatabase

from DatabaseStorage.Program.Database.Database_Properties import *


class DatabaseNeo4J(object):
    """
    It contains all the function to interact with the Neo4J database

    PARAMETERS:
        None

    METHODS:
        close           --  close the given database
        runQuery        --  execute the query on the database
        deleteData      --  drop all the data in the database
        createIndexes   --  create the needed index
        dropIndexes     --  drop all indexes from the database
    """

    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        """
        close the database
        """
        self._driver.close()

    def runQuery(self, query):
        """
        execute a query and run a result
        :param query: a string representing a cypher query
        :return: the result of the query
        """
        result = None
        with self._driver.session() as session:
            result = session.write_transaction(self._execute_code, query)
        return result, 1

    def deleteData(self):
        """
        delete all the data from the database
        """
        with self._driver.session() as session:
            session.write_transaction(self._execute_code, "MATCH(n) OPTIONAL MATCH(n) - [r] - () DELETE n, r")
        return 1

    def createIndexes(self):
        """
        create needed index indexes
        :return:
        """
        with self._driver.session() as session:
            session.write_transaction(self._execute_code, "CREATE INDEX ON %s(%s)" % (
            NodeHuman.LABEL_HUMAN.value, NodeHuman.PROPERTY_NAME.value))
            session.write_transaction(self._execute_code, "CREATE INDEX ON %s(%s)" % (
            NodeMachine.LABEL_MACHINE.value, NodeMachine.PROPERTY_NAME.value))
            session.write_transaction(self._execute_code, "CREATE INDEX ON %s(%s)" % (
            NodeMachine.LABEL_MACHINE_TYPE.value, NodeMachine.PROPERTY_TYPE.value))
            session.write_transaction(self._execute_code, "CREATE INDEX ON %s(%s)" % (
            NodeTag.LABEL_TAG.value, NodeTag.PROPERTY_KEYWORD.value))
        return 1

    def dropIndexes(self):
        """
        drop all indexes on the database
        """
        with self._driver.session() as session:
            indexes = session.write_transaction(self._execute_code, "CALL db.indexes")
            for index in indexes:
                session.write_transaction(self._execute_code, "DROP %s" % (index[0]))
        return 1

    def get_all_labels(self):
        """
        return
        :return: a dictionary with all the label and properties from the database
        """
        query = "MATCH (node) RETURN DISTINCT labels(node)"
        results_label, done = self.runQuery(query)
        label_property_dict = dict()

        for result_label in results_label.records():
            for labels in result_label.values():
                for label in labels:
                    query = f'MATCH (node:{label})<-[relation]-() RETURN type(relation)'
                    results_relation, done = self.runQuery(query)

                    label_property_dict.update({label: {p for proper in results_relation.records() for prop in
                                                        proper.values() for p in prop}})


                    # query = f'MATCH (node:{label}) RETURN keys(node)'
                    # results_properties, done = self.runQuery(query)
                    # label_property_dict.update({label: {p for proper in results_properties.records() for prop in proper.values() for p in prop}})

        return label_property_dict

    @staticmethod
    def _execute_code(tx, query):
        result = tx.run(query)
        return result
