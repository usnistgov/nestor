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
   This file contains the object HUMAN, TECHNICIAN and OPERATOR that follow the given hierarchy:
   HUMAN
       OPERATOR
       TECHNICIAN

   This object is a container that represent our world (maintenance work order data) but,
    in the database the node label and the properties key can be easily changed in the YAML file DatabaseSchema.YAML

    In the database, only the name of the properties can changed but not the type of data or the number of properties
    (you can have less but not more)
    However, the hierarchy followed the rules created in this file
"""

from database_storage.helper import standardizeString

class Human:
    """
    a HUMAN define every information that refer to the node HUMAN in our database.
    It setup the properties and query to match with every HUMAN in the database
    An HUMAN is define only with a property NAME in the database

    It is instantiate using:
        - name: a String or array of string
        - databaseInfo: the dictionary that describe the database information (name of properties, and Label)

    It contains getter and setter for every properties, it is highly recommend to use the setter
     because it represent the data as a standard way - the way it is store in the database
    It contains a string representation
    It contains a boolean representation
    """
    def __init__(self, name=None,  databaseInfo=None):
        self.databaseInfoHuman = databaseInfo['human']
        self.label = self.databaseInfoHuman['label']['human']

        self._set_name(name)

    def _get_name(self):
        return self.name

    def _set_name(self, name):
        if isinstance(name, str):
            self.name = standardizeString(name).lower()
        else:
            self.name = None

    def __bool__(self):
        return not (self.name is None)

    def __str__(self):
        return  f'object  =  {type(self)}\n' \
                f'\tlabel  =  {self.label}\n' \
                f'\tname  =  {self.name}'

    def cypher_human_name(self, variable_human="human"):
        """
        Create a Cypher query to return the specific node HUMAN define by the property NAME
        :param variable_human: default "human" to refer to a special node
        :return: a string - Cypher Query : (human:HUMAN{name:"x"})
            OR empty string if the HUMAN has no NAME
        """
        if not self.name:
            return ""
        return f'({variable_human}{self.label}' + \
               "{" + f'{self.databaseInfoHuman["properties"]["name"]}:\'{self.name}\'' + "})"

    def cypher_human_all(self, variable_human="human"):
        """
        Create a Cypher query to return the specific node HUMAN define by all the possible properties (NAME)
        :param variable_human: default "human" to refer to a specific HUMAN
        :return: a string - Cypher Query : (operator:HUMAN{name:"x"})
        """
        query = f'({variable_human}{self.label}'
        if self.name:
            query += "{" + f'{self.databaseInfoHuman["properties"]["name"]}:\'{self.name}\'' + "}"
        query += ")"

        return query

    def cypher_human_merge(self, variable_human="human"):
        """
         Create a Cypher query to merge the node HUMAN using his property NAME
         and Set the missing properties (none in this case)
         :param variable_human: default "human" to refer to a specific HUMAN
         :return: a string - Cypher Query : MERGE (technician:HUMAN{name:"x"})
         """
        if not self.name:
            return ""
        query = f'\nMERGE {self.cypher_human_name(variable_human)}'
        return query


class Operator(Human):
    """
    An OPERATOR inherit from HUMAN
    It define every information that refer to the node OPERATOR in our database.
    It setup the properties and query to match with every HUMAN OPERATOR in the database
    There are no additional properties than the HUMAN one but functions are different

    It is instantiate using:
        - name: a String or list of string that represent the property NAME of the OPERATOR
        - databaseInfo: the dictionary that describe the database information (name of properties, and Label)

    It contains getter and setter for every properties, it is highly recommend to use the setter
     because it represent the data as a standard way - the way it is store in the database
    It contains a string representation
    It contains a boolean representation
    """

    def __init__(self, name=None, databaseInfo=None):
        super().__init__(name=name, databaseInfo=databaseInfo)
        self.label += self.databaseInfoHuman['label']['operator']

    def __bool__(self):
        return not (self.name is None)

    def __str__(self):
        return f'{super().__str__()}'


    def cypher_operator_name(self, variable_operator="operator"):
        """
        Create a Cypher query to return the specific node OPERATOR define by the property NAME
        :param variable_operator: default "operator" to refer to a special node
        :return: a string - Cypher Query : (operator:HUMAN:OPERATOR{name:"x"})
            OR empty string if the OPERATOR has no NAME
        """
        if not self.name:
            return ""
        return f'({variable_operator}{self.label}' + \
               "{" + f'{self.databaseInfoHuman["properties"]["name"]}:\'{self.name}\'' + "})"

    def cypher_operator_all(self, variable_operator="operator"):
        """
        Create a Cypher query to return the specific node OPERATOR define by all the possible properties (NAME)
        :param variable_operator: default "operator" to refer to a specific OPERATOR
        :return: a string - Cypher Query : (operator:HUMAN:OPERATOR{name:"x"})
        """

        query = f'({variable_operator}{self.label}'
        if self.name:
            query += "{" + f'{self.databaseInfoHuman["properties"]["name"]}:\'{self.name}\'' + "}"
        query += ")"

        return query

    def cypher_operator_merge(self, variable_operator="operator"):
        """
        Create a Cypher query to merge the node OPERATOR using his property NAME
        and Set the missing properties (none in this case)
        :param variable_operator: default "operator" to refer to a specific OPERATOR
        :return: a string - Cypher Query : MERGE (operator:HUMAN:OPERATOR{name:"x"})
        """
        query = self.cypher_human_merge(variable_operator)
        query += f'\nSET {variable_operator} {self.databaseInfoHuman["label"]["operator"]}'

        return query


class Technician(Human):
    """
    An TECHNICIAN inherit from HUMAN
    It define every information that refer to the node TECHNICIAN in our database.
    It setup the properties and query to match with every HUMAN TECHNICIAN in the database
    The additional properties are SKILLS (array in the database) and CRAFTS (array in the database)

    It is instantiate using:
        - name: a String or array of string
        - skills : array of string
        - crafts : array of string
        - databaseInfo: the dictionary that describe the database information (name of properties, and Label)

    It contains getter and setter for every properties, it is highly recommend to use the setter
     because it represent the data as a standard way - the way it is store in the database
    It contains a string representation
    It contains a boolean representation
    """

    def __init__(self, name=None, skills=None, crafts=None, databaseInfo=None):

        super().__init__(name=name, databaseInfo=databaseInfo)
        self.label += self.databaseInfoHuman['label']['technician']
        self._set_skills(skills)
        self._set_crafts(crafts)

    def _get_skills(self):
        return self.skills

    def _set_skills(self, skills):
        if isinstance(skills, str):
            self.skills = standardizeString(skills).lower()
        elif isinstance(skills, list):
            self.skills = [standardizeString(s).lower() for s in skills]
        else:
            self.skills = None

    def _get_crafts(self):
        return self.crafts

    def _set_crafts(self, crafts):
        if isinstance(crafts, str):
            self.crafts = standardizeString(crafts).lower()
        elif isinstance(crafts, list):
            self.crafts = [standardizeString(c).lower() for c in crafts]
        else:
            self.crafts = None

    def __bool__(self):
        return not (
            (self.name is None) and
            (self.skills is None) and
            (self.name is None)
        )

    def __str__(self):
        return  f'{super().__str__()}\n'\
                f'\tskills  =  {self.skills}\n'\
                f'\tcrafts  =  {self.crafts}'

    def cypher_technician_name(self, variable_technician="technician"):
        """
         Create a Cypher query to return the specific node TECHNICIAN define by the property NAME
         :param variable_technician: default "technician" to refer to a special node
         :return: a string - Cypher Query : (operator:HUMAN:TECHNICIAN{name:"x"})
             OR empty string if the TECHNICIAN has no NAME
         """
        if not self.name:
            return ""
        return f'({variable_technician}{self.label}' + \
               "{" + f'{self.databaseInfoHuman["properties"]["name"]}:\'{self.name}\'' + "})"

    def cypher_technician_all(self, variable_technician="technician"):
        """
        Create a Cypher query to return the specific node TECHNICIAN define by all the possible properties (NAME, SKILLS, CRAFTS)
        :param variable_technician: default "technician" to refer to a specific TECHNICIAN
        :return: a string - Cypher Query : (operator:HUMAN:TECHNICIAN{name:"x", skills:["x","y"], crafts:["x"]})
        """
        query = f'({variable_technician}{self.label}'
        if self.name or self.skills or self.crafts is not None:
            query += "{"
            if self.name is not None:
                query += f'{self.databaseInfoHuman["properties"]["name"]}:\'{self.name}\','
            if self.skills is not None:
                query += f'{self.databaseInfoHuman["properties"]["skills"]}:' + '[\'' + '\',\''.join(self.skills) + '\'],'
            if self.crafts is not None:
                query += f'{self.databaseInfoHuman["properties"]["crafts"]}:' + '[\'' + '\',\''.join(self.crafts) + '\'],'
            query = query[:-1] + "}"
        return query + ")"

    def cypher_technician_merge(self, variable_technician="technician"):
        """
         Create a Cypher query to merge the node TECHNICIAN using his property NAME
         and Set the missing properties (SKILLS, CRAFTS)
         :param variable_technician: default "technician" to refer to a specific TECHNICIAN
         :return: a string - Cypher Query : MERGE (technician:HUMAN:TECHNICIAN{name:"x"})
                                            SET technician.skills = ["x","y"]
                                            SET technician.crafts = ["x"]
                in the database, SKILLS and CRAFTS are array, so we add values to the array if not already in
         """
        query = self.cypher_human_merge(variable_technician)
        if self.skills:
            for skill in self.skills:
                query += f'\nFOREACH(x in CASE WHEN \'{skill}\' in {variable_technician}.{self.databaseInfoHuman["properties"]["skills"]} THEN [] ELSE [1] END |' \
                         f'  SET {variable_technician}.{self.databaseInfoHuman["properties"]["skills"]} = coalesce({variable_technician}.{self.databaseInfoHuman["properties"]["skills"]},[]) + \'{skill}\' )'
        if self.crafts:
            for craft in self.crafts:
                query += f'\nFOREACH(x in CASE WHEN \'{craft}\' in {variable_technician}.{self.databaseInfoHuman["properties"]["crafts"]} THEN [] ELSE [1] END |' \
                         f'  SET {variable_technician}.{self.databaseInfoHuman["properties"]["crafts"]} = coalesce({variable_technician}.{self.databaseInfoHuman["properties"]["crafts"]},[]) + \'{craft}\' )'
        query += f'\nSET {variable_technician} {self.databaseInfoHuman["label"]["technician"]}'
        return query
