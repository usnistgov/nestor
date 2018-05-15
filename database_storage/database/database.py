"""
File: database.py
Author: Sascha MOCCOZET
Organisation:
   Departament of Commerce USA
   National Institute of Standards and Technology - NIST
   Engineering Laboratory - EL
   Systems Integration Division - SID
   Information Modeling and Testing Group - IMTG
   <Insert Project Name>
Description:
   This file contains the object database - in our case Neo4J database -and the function to interact with this database
   Originally created to store Maintenance Work Order for Manufacturing, it should be totally modular
   but will respect the graph schema created to solve our problem
   It use the neo4j driver for python
"""
import pandas as pd
from tqdm import tqdm
from neo4j.v1 import GraphDatabase


class DatabaseNeo4J(object):
    """
    The class database this object is specially created for Neo4J database
    it is instantiate using:
        - uri: the server url
        - user: the user of the database
        - password: the password of the use
        - schema : a dictionary the desrcibe the schame of the database (node label, edges label, properies name) -see the YAML file database_storage/database/DatabaseSchema.yaml-

    It also contains the methods to transform the result from self.runQuery() into dataframe

    """

    def __init__(self, uri, user, password, schema=None):
        self.schema=schema
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        """
        Close the curent database
        :return: 1 if it works
        """
        self._driver.close()
        return 1

    def runQuery(self, query):
        """
        Execute the cypher query into the given database into a transaction that respect the ACID standard
        :param query: a cypher query
        :return:
        - (1, ResultStatement) if it has been executed with succes
        - (0, None) if it cannot run -The problem often is on the query structure
        """
        try:
            result = None
            with self._driver.session() as session:
                result = session.write_transaction(self._execute_code, query)
            return 1, result
        except:
            return 0, None

    def deleteData(self):
        """
        Delete all the data from the database
        :return: 1 if it works
        """
        with self._driver.session() as session:
            session.write_transaction(self._execute_code, "MATCH(n) OPTIONAL MATCH(n) - [r] - () DELETE n, r")
        return 1

    def createIndexes(self):
        """
        Create the indexs on the database for the properties often asked
        :return: 1 if it works
        """
        self.runQuery(f'CREATE INDEX ON {self.schema["human"]["label"]["human"]}({self.schema["human"]["properties"]["name"]})')
        self.runQuery(f'CREATE INDEX ON {self.schema["machine"]["label"]["machine"]}({self.schema["machine"]["properties"]["name"]})')
        self.runQuery(f'CREATE INDEX ON {self.schema["tag"]["label"]["tag"]}({self.schema["tag"]["properties"]["keyword"]})')
        return 1

    def dropIndexes(self):
        """
        Delete all indexes from the database
        :return: 1 if it works
        """
        with self._driver.session() as session:
            indexes = session.write_transaction(self._execute_code, "CALL db.indexes")
            for index in indexes:
                session.write_transaction(self._execute_code, "DROP %s" % (index[0]))
        return 1


    @staticmethod
    def _execute_code(tx, query):
        """
        Execute a cypher query into a transaction
        :param tx: the Transaction object from the Neo4j Driver
        :param query: a Cypher query
        :return: the result as ResultStatement from Neo4j Driver object
        """
        result = tx.run(query)
        return result
