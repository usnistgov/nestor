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

class Human:
    """a HUMAN define every information that refer to the node HUMAN in our database.
    It setup the properties and query to match with every HUMAN in the database
    An HUMAN is define only with a property NAME in the database
    
    It is instantiate using:
        - name: a String or array of string
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
    def __init__(self, name=None,  databaseInfo=None):
        self.databaseInfoHuman = databaseInfo['human']

        self._set_name(name)

    def _get_name(self):
        return self.name

    def _set_name(self, name):
        if isinstance(name, str):
            self.name = name.lower().lstrip().replace('"','\\"')
        elif isinstance(name, list):
            self.name = [n.lower().lstrip().replace('"','\\"') for n in name]
        else:
            self.name = None

    def __bool__(self):
        return not (self.name is None)

    def __str__(self):
        return f"{type(self)}\n\t" \
               f"Name: {self.name}"

    def cypher_human_label(self, variable_human="human"):
        """Create a Cypher query with the given variable and all label for the node HUMAN

        Parameters
        ----------
        variable_human :
            default "human" to refer to a special node

        Returns
        -------
        type
            a string - Cypher Query : human:HUMAN

        """
        return f'{variable_human}{self.databaseInfoHuman["label"]["human"]}'

    def cypher_human_name(self, variable_human="human"):
        """Create a Cypher query to return the specific node HUMAN define by the property NAME

        Parameters
        ----------
        variable_human :
            default "human" to refer to a special node

        Returns
        -------
        type
            a string - Cypher Query : (human:HUMAN{name:"x"})
            OR empty string if the HUMAN has no NAME

        """
        if not self.name:
            return ""
        return f'({self.cypher_human_label(variable_human)}' + \
               "{" + f'{self.databaseInfoHuman["properties"]["name"]}:"{self.name}"' + "})"

    def cypher_human_all(self, variable_human="human"):
        """Create a Cypher query to return the specific node HUMAN define by all the possible properties (NAME)

        Parameters
        ----------
        variable_human :
            default "human" to refer to a specific HUMAN

        Returns
        -------
        type
            a string - Cypher Query : (operator:HUMAN{name:"x"})

        """
        query = f'({self.cypher_human_label(variable_human)}'
        if self.name:
            query += "{" + f'{self.databaseInfoHuman["properties"]["name"]}:"{self.name}"' + "}"
        query += ")"

        return query

    def cypher_human_merge(self, variable_human="human"):
        """Create a Cypher query to merge the node HUMAN using his property NAME
         and Set the missing properties (none in this case)

        Parameters
        ----------
        variable_human :
            default "human" to refer to a specific HUMAN

        Returns
        -------
        type
            a string - Cypher Query : MERGE (technician:HUMAN{name:"x"})

        """
        if not self.name:
            return ""
        query = f'MERGE {self.cypher_human_name(variable_human)}'
        return query


    def cypher_human_whereReturn(self, variable_human="human"):
        """Create 2 arrays used for the WHERE clause and the RETURN clause of the Cypher Query from this HUMAN
        Used to filter the database based on specifics properties values
        
        For this case, the properties of this object might be an array
        If a value in an array is "_" this property will be added to the return statement

        Parameters
        ----------
        variable_human :
            default "human" to match a specific HUMAN

        Returns
        -------
        type
            a tuple of arrays - where properties, return properties :
            (['human.name = "bob','human.name = "3"]['human.name'])

        """
        cypherWhere = []
        cypherReturn = []

        if self.name:
            for n in self.name:
                if n == "_":
                    cypherReturn.append(f'{variable_human}.{self.databaseInfoHuman["properties"]["name"]}')
                else:
                    cypherWhere.append(
                        f'{variable_human}.{self.databaseInfoHuman["properties"]["name"]} = "{n}"')

        return cypherWhere, cypherReturn

class Operator(Human):
    """An OPERATOR inherit from HUMAN
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

    Parameters
    ----------

    Returns
    -------

    """

    def __init__(self, name=None, databaseInfo=None):
        super().__init__(name, databaseInfo=databaseInfo)

    def __bool__(self):
        return not (self.name is None)

    def __str__(self):
        return f"{type(self)}\n\t" \
               f"Name: {self.name}"

    def cypher_operator_label(self, variable_operator="operator"):
        """Create a Cypher query with the given variable and all label for the node OPERATOR

        Parameters
        ----------
        variable_operator :
            default "operator" to refer to a special node

        Returns
        -------
        type
            a string - Cypher Query : operator:HUMAN:OPERATOR

        """
        return f'{self.cypher_human_label(variable_operator)}{self.databaseInfoHuman["label"]["operator"]}'

    def cypher_operator_name(self, variable_operator="operator"):
        """Create a Cypher query to return the specific node OPERATOR define by the property NAME

        Parameters
        ----------
        variable_operator :
            default "operator" to refer to a special node

        Returns
        -------
        type
            a string - Cypher Query : (operator:HUMAN:OPERATOR{name:"x"})
            OR empty string if the OPERATOR has no NAME

        """
        if not self.name:
            return ""
        return f'({self.cypher_operator_label(variable_operator)}' + \
               "{" + f'{self.databaseInfoHuman["properties"]["name"]}:"{self.name}"' + "})"

    def cypher_operator_all(self, variable_operator="operator"):
        """Create a Cypher query to return the specific node OPERATOR define by all the possible properties (NAME)

        Parameters
        ----------
        variable_operator :
            default "operator" to refer to a specific OPERATOR

        Returns
        -------
        type
            a string - Cypher Query : (operator:HUMAN:OPERATOR{name:"x"})

        """

        query = f'({self.cypher_operator_label(variable_operator)}'
        if self.name:
            query += "{" + f'{self.databaseInfoHuman["properties"]["name"]}:"{self.name}"' + "}"
        query += ")"

        return query

    def cypher_operator_merge(self, variable_operator="operator"):
        """Create a Cypher query to merge the node OPERATOR using his property NAME
        and Set the missing properties (none in this case)

        Parameters
        ----------
        variable_operator :
            default "operator" to refer to a specific OPERATOR

        Returns
        -------
        type
            a string - Cypher Query : MERGE (operator:HUMAN:OPERATOR{name:"x"})

        """
        query = self.cypher_human_merge(variable_operator)
        query += f'\nSET {variable_operator} {self.databaseInfoHuman["label"]["operator"]}'

        return query

    def cypher_operator_whereReturn(self, variable_operator="operator"):
        """Create 2 arrays used for the WHERE clause and the RETURN clause of the Cypher Query from this OPERATOR
        Used to filter the database based on specifics properties values
        
        For this case, the properties of this object might be an array
        If a value in an array is "_" this property will be added to the return statement

        Parameters
        ----------
        variable_operator :
            default "operator" to match a specific OPERATOR

        Returns
        -------
        type
            a tuple of arrays - where properties, return properties :
            (['operator.name = "bob','operator.name = "3"]['operator.name'])

        """

        cypherWhere, cypherReturn= self.cypher_human_whereReturn(variable_operator)

        return cypherWhere, cypherReturn


class Technician(Human):
    """An TECHNICIAN inherit from HUMAN
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

    Parameters
    ----------

    Returns
    -------

    """

    def __init__(self, name=None, skills=None, crafts=None, databaseInfo=None):

        super().__init__(name, databaseInfo=databaseInfo)
        self._set_skills(skills)
        self._set_crafts(crafts)

    def _get_skills(self):
        return self.skills

    def _set_skills(self, skills):
        if isinstance(skills, str):
            self.skills = skills.lower().lstrip().replace('"','\\"')
        elif isinstance(skills, list):
            self.skills = [s.lower().lstrip().replace('"','\\"') for s in skills]
        else:
            self.skills = None

    def _get_crafts(self):
        return self.crafts

    def _set_crafts(self, crafts):
        if isinstance(crafts, str):
            self.crafts = crafts.lower().lstrip().replace('"','\\"')
        elif isinstance(crafts, list):
            self.crafts = [c.lower().lstrip().replace('"','\\"') for c in crafts]
        else:
            self.crafts = None

    def __bool__(self):
        return not (
            (self.name is None) and
            (self.skills is None) and
            (self.name is None)
        )

    def __str__(self):
        return f"{type(self)}\n\t" \
               f"Name: {self.name}\n\t" \
               f"Skills: {self.skills}\n\t" \
               f"Crafts: {self.crafts}"

    def cypher_technician_label(self, variable_technician="technician"):
        """Create a Cypher query with the given variable and all label for the node TECHNICIAN

        Parameters
        ----------
        variable_technician :
            default "technician" to refer to a special node

        Returns
        -------
        type
            a string - Cypher Query : technician:HUMAN:TECHNICIAN

        """
        return f'{self.cypher_human_label(variable_technician)}{self.databaseInfoHuman["label"]["technician"]}'

    def cypher_technician_name(self, variable_technician="technician"):
        """Create a Cypher query to return the specific node TECHNICIAN define by the property NAME

        Parameters
        ----------
        variable_technician :
            default "technician" to refer to a special node

        Returns
        -------
        type
            a string - Cypher Query : (operator:HUMAN:TECHNICIAN{name:"x"})
            OR empty string if the TECHNICIAN has no NAME

        """
        if not self.name:
            return ""
        return f'({self.cypher_technician_whereReturn(variable_technician)}' + \
               "{" + f'{self.databaseInfoHuman["properties"]["name"]}:"{self.name}"' + "})"

    def cypher_technician_all(self, variable_technician="technician"):
        """Create a Cypher query to return the specific node TECHNICIAN define by all the possible properties (NAME, SKILLS, CRAFTS)

        Parameters
        ----------
        variable_technician :
            default "technician" to refer to a specific TECHNICIAN

        Returns
        -------
        type
            a string - Cypher Query : (operator:HUMAN:TECHNICIAN{name:"x", skills:["x","y"], crafts:["x"]})

        """
        query = f'({self.cypher_technician_whereReturn(variable_technician)}'
        if self.name or self.skills or self.crafts is not None:
            query += "{"
            if self.name is not None:
                query += f'{self.databaseInfoHuman["properties"]["name"]}:"{self.name}",'
            if self.skills is not None:
                query += f'{self.databaseInfoHuman["properties"]["skills"]}:' + '["' + '","'.join(self.skills) + '"],'
            if self.crafts is not None:
                query += f'{self.databaseInfoHuman["properties"]["crafts"]}:' + '["' + '","'.join(self.crafts) + '"],'
            query = query[:-1] + "}"
        return query + ")"

    def cypher_technician_merge(self, variable_technician="technician"):
        """Create a Cypher query to merge the node TECHNICIAN using his property NAME
         and Set the missing properties (SKILLS, CRAFTS)

        Parameters
        ----------
        variable_technician :
            default "technician" to refer to a specific TECHNICIAN

        Returns
        -------
        type
            a string - Cypher Query : MERGE (technician:HUMAN:TECHNICIAN{name:"x"})
            SET technician.skills = ["x","y"]
            SET technician.crafts = ["x"]
            in the database, SKILLS and CRAFTS are array, so we add values to the array if not already in

        """
        query = self.cypher_human_merge(variable_technician)
        if self.skills:
            for skill in self.skills:
                query += f'\nFOREACH(x in CASE WHEN "{skill}" in {variable_technician}.{self.databaseInfoHuman["properties"]["skills"]} THEN [] ELSE [1] END |' \
                         f'  SET {variable_technician}.{self.databaseInfoHuman["properties"]["skills"]} = coalesce({variable_technician}.{self.databaseInfoHuman["properties"]["skills"]},[]) + "{skill}" )'
        if self.crafts:
            for craft in self.crafts:
                query += f'\nFOREACH(x in CASE WHEN "{craft}" in {variable_technician}.{self.databaseInfoHuman["properties"]["crafts"]} THEN [] ELSE [1] END |' \
                         f'  SET {variable}.{self.databaseInfoHuman["properties"]["crafts"]} = coalesce({variable_technician}.{self.databaseInfoHuman["properties"]["crafts"]},[]) + "{craft}" )'
        query += f'\nSET {variable_technician} {self.databaseInfoHuman["label"]["technician"]}'
        return query

    def cypher_technician_whereReturn(self, variable_technician="technician"):
        """Create 2 arrays used for the WHERE clause and the RETURN clause of the Cypher Query from this TECHNICIAN
        Used to filter the database based on specifics properties values
        
        For this case, the properties of this object might be an array
        If a value in an array is "_" this property will be added to the return statement

        Parameters
        ----------
        variable_technician :
            default "technician" to match a specific TECHNICIAN

        Returns
        -------
        type
            a tuple of arrays - where properties, return properties :
            (['technician.name = "bob"','"y" in technician.skills']['technician.crafts'])

        """
        cypherWhere, cypherReturn= self.cypher_human_whereReturn(variable_technician)

        if self.skills:
            for s in self.skills:
                if s == "_":
                    cypherReturn.append(f'{variable_technician}.{self.databaseInfoHuman["properties"]["skills"]}')
                else:
                    cypherWhere.append(f'"{s}" IN {variable_technician}.{self.databaseInfoHuman["properties"]["skills"]}')

        if self.crafts:
            for c in self.crafts:
                if c == "_":
                   cypherReturn.append(f'{variable_technician}.{self.databaseInfoHuman["properties"]["crafts"]}')
                else:
                    cypherWhere.append(f'"{c}" IN {variable_technician}.{self.databaseInfoHuman["properties"]["crafts"]}')

        return cypherWhere, cypherReturn
