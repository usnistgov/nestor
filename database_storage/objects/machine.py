"""
File: machine.py
Author: Sascha MOCCOZET
Organisation:
   Departament of Commerce USA
   National Institute of Standards and Technology - NIST
   Engineering Laboratory - EL
   Systems Integration Division - SID
   Information Modeling and Testing Group - IMTG
   <Insert Project Name>
Description:
   This file contains the object MACHINE

   This object is a container that represent our world (maintenance work order data) but,
    in the database the node label and the properties key can be easily changed in the YAML file DatabaseSchema.YAML

    In the database, only the name of the properties can changed but not the type of data or the number of properties
    (you can have less but not more)

"""

class Machine:
    """
    A MACHINE define every information that refer to the node MACHINE and MACHINE_TYPE in our database.
    It setup the properties and query to match with every MACHINE and MACHINE_TYPE in the database
    The MACHINE is define using the property NAME, MANUFACTURER, LOCATION
    The MACHINE_TYPE is define using a property TYPE

    It is instantiate using:
        - name: a String or array of string
        - manufacturer : a String or array of string
        - locasion: a String or array of string
        - machine_type: a String or array of string
        - databaseInfo: the dictionary that describe the database information (name of properties, and Label)

    It contains getter and setter for every properties, it is highly recommend to use the setter
     because it represent the data as a standard way - the way it is store in the database
    It contains a string representation
    It contains a boolean representation
    """


    def __init__(self, name=None, manufacturer=None, locasion=None, machine_type=None, databaseInfo=None):
        self.databaseInfoMachine = databaseInfo['machine']

        self._set_name(name)
        self._set_manufacturer(manufacturer)
        self._set_locasion(locasion)
        self._set_machine_type(machine_type)

    def _get_name(self):
        return self.name

    def _set_name(self, name):
        if isinstance(name, str):
            self.name = name.lower().lstrip().replace('"','\\"')
        elif isinstance(name, list):
            self.name = [n.lower().lstrip().replace('"','\\"') for n in name]
        else:
            self.name = None

    def _get_manufacturer(self):
        return self.manufacturer

    def _set_manufacturer(self, manufacturer):
        if isinstance(manufacturer, str):
            self.manufacturer = manufacturer.lower().lstrip().replace('"','\\"')
        elif isinstance(manufacturer, list):
            self.manufacturer = [m.lower().lstrip().replace('"','\\"') for m in manufacturer]
        else:
            self.manufacturer = None

    def _get_locasion(self):
        return self.location

    def _set_locasion(self, location):
        if isinstance(location, str):
            self.location = location.lower().lstrip().replace('"','\\"')
        elif isinstance(location, list):
            self.location = [l.lower().lstrip().replace('"','\\"') for l in location]
        else:
            self.location = None

    def _get_machine_type(self):
        return self.machine_type

    def _set_machine_type(self, machine_type):
        if isinstance(machine_type, str):
            self.machine_type = machine_type.lower().lstrip().replace('"','\\"')
        elif isinstance(machine_type, list):
            self.machine_type = [m.lower().lstrip().replace('"','\\"') for m in machine_type]
        else:
            self.machine_type = None

    def __bool__(self):
        return not (
            (self.name is None) and
            (self.manufacturer is None) and
            (self.location is None) and
            (self.machine_type is None)
            )

    def __str__(self):
        return  f'object  =  {type(self)}\n'\
                f'\tname  =  {self.name}\n'\
                f'\tmanufacturer  =  {self.manufacturer}\n'\
                f'\tlocation  =  {self.location}\n'\
                f'\tmachine_type  =  {self.machine_type}\n'

    def cypher_machine_label(self, variable_machine="machine"):
        """
        Create a Cypher query with the given variable and all label for the node MACHINE
        :param variable_machine: default "machine" to refer to a special node
        :return: a string - Cypher Query : machine:MACHINE
        """
        return f'{variable_machine}{self.databaseInfoMachine["label"]["machine"]}'

    def cypher_machine_name(self, variable_machine="machine"):
        """
         Create a Cypher query to return the specific node MACHINE define by the property NAME
         :param variable_machine: default "machine" to refer to a special node
         :return: a string - Cypher Query : (machine:MACHINE{name:"x"})
             OR empty string if the MACHINE has no NAME
         """
        if not self.name:
            return ""
        return f'({self.cypher_machine_label(variable_machine)}' + \
               "{" + f'{self.databaseInfoMachine["properties"]["name"]}:"{self.name}"' + "})"

    def cypher_machine_all(self, variable_machine="machine"):
        """
        Create a Cypher query to return the specific node MACHINE define by all the possible properties (NAME, MANUFACTURER, LOCATION)
        :param variable_machine: default "machine" to refer to a specific MACHINE
        :return: a string - Cypher Query : (machine:MACHINE{name:"x", manufacturer:"x", location:"x"})
        """
        query = f'({self.cypher_machine_label(variable_machine)}'
        if self.name or self.manufacturer or self.location is not None:
            query += "{"
            if self.name:
                query += f'{self.databaseInfoMachine["properties"]["name"]}:"{self.name}",'
            if self.manufacturer:
                query += f'{self.databaseInfoMachine["properties"]["manufacturer"]}:"{self.manufacturer}",'
            if self.location:
                query += f'{self.databaseInfoMachine["properties"]["location"]}:"{self.location}",'
            query = query[:-1] + "}"
        return query + ")"

    def cypher_machine_merge(self, variable_machine="machine"):
        """
         Create a Cypher query to merge the node MACHINE using his property NAME
         and Set the missing properties (MANUFACTURER, LOCATION)
         :param variable_machine: default "machine" to refer to a specific MACHINE
         :return: a string - Cypher Query : MERGE (machine:MACHINE{name:"x"})
                                            SET machine.manufacturer = "x"
                                            SET machine.location = "x"
         """
        if not self.name:
            return ""
        query = f'\nMERGE {self.cypher_machine_name(variable_machine)}'
        if self.manufacturer:
            query += f'\nSET {variable_machine}.{self.databaseInfoMachine["properties"]["manufacturer"]} = "{self.manufacturer}"'
        if self.location:
            query += f'\nSET {variable_machine}.{self.databaseInfoMachine["properties"]["location"]} = "{self.location}"'
        return query

    def cypher_machinetype_label(self, variable_machinetype="machine_type"):
        """
        Create a Cypher query with the given variable and all label for the node MACHINE_TYPE
        :param variable_machinetype: default "machine_type" to refer to the node
        :return: a string - Cypher Query : machine_type:MACHINE_TYPE
        """
        return f'{variable_machinetype}{self.databaseInfoMachine["label"]["type"]}'


    def cypher_machinetype_type(self, variable_machinetype="machine_type"):
        """
         Create a Cypher query to return the specific node MACHINE_TYPE define by the property TYPE
         :param variable_machinetype: default "machine_type" to refer to a special node
         :return: a string - Cypher Query : (machine_type:MACHINE_TYPE{type:"x"})
             OR empty string if the MACHINE_TYPE has no TYPE
         """
        if not self.machine_type:
            return ""
        return f'( {self.cypher_machinetype_label(variable_machinetype)}' + \
               "{" + f'{self.databaseInfoMachine["properties"]["type"]}:"{self.machine_type}"' + "})"

    def cypher_machinetype_all(self, variable_machinetype="machine_type"):
        """
        Create a Cypher query to return the specific node MACHINE_TYPE define by all the possible properties (TYPE)
        :param variable_machinetype: default "machine_type" to refer to a specific MACHINE_TYPE
        :return: a string - Cypher Query : (machine_type:MACHINE_TYPE{type:"x"})
        """
        query = f'( {self.cypher_machinetype_label(variable_machinetype)}'
        if self.machine_type:
            query += "{" + f'{self.databaseInfoMachine["properties"]["type"]}:"{self.machine_type}"' + "}"
        query += ")"

        return query


    def cypher_machinetype_merge(self, variable_machinetype="machine_type"):
        """
         Create a Cypher query to merge the node MACHINE_TYPE using his property TYPE
         and Set the missing properties (none in that case)
         :param variable_machinetype: default "machine_type" to refer to a specific MACHINE_TYPE
         :return: a string - Cypher Query : MERGE (machine_type:MACHINE_TYPE{type:"x"})
         """
        if not self.name:
            return ""
        query = f'\nMERGE {self.cypher_machinetype_type(variable_machinetype)}'
        return query

    def cypher_where(self, operation, variable_machine="machine", variable_machinetype="machine_type"):
        """
        Create 2 arrays used for the WHERE clause and the RETURN clause of the Cypher Query from this MACHINE
        Used to filter the database based on specifics properties values

        For this case, the properties of this object might be an array
        If a value in an array is "_" this property will be added to the return statement

        :param variable_machine: default "machine" to match a specific MACHINE
        :return: a tuple of arrays - where properties, return properties :
            (['machine.name = "bob','machine.manufacturer = "3", 'machine.location = "y"']['machine.location'])
        """
        cypherWhere = None
        if operation == "IS NULL" or operation == "IS NOT NULL":
            if self.name:
                cypherWhere = f'{variable_machine}.{self.databaseInfoMachine["properties"]["name"]} {operation}'
            elif self.location:
                cypherWhere = f'{variable_machine}.{self.databaseInfoMachine["properties"]["location"]} {operation}'
            elif self.manufacturer:
                cypherWhere = f'{variable_machine}.{self.databaseInfoMachine["properties"]["manufacture"]} {operation}'
            elif self.machine_type:
                cypherWhere = f'{variable_machinetype}.{self.databaseInfoMachine["properties"]["type"]} {operation}'
        else:
            if self.name:
                cypherWhere = f'{variable_machine}.{self.databaseInfoMachine["properties"]["name"]} {operation} "{self.name}"'
            elif self.location:
                cypherWhere = f'{variable_machine}.{self.databaseInfoMachine["properties"]["location"]} {operation} "{self.location}"'
            elif self.manufacturer:
                cypherWhere = f'{variable_machine}.{self.databaseInfoMachine["properties"]["manufacture"]} {operation} "{self.manufacturer}"'
            elif self.machine_type:
                cypherWhere = f'{variable_machinetype}.{self.databaseInfoMachine["properties"]["type"]} {operation} "{self.machine_type}"'

        return cypherWhere


    def cypher_match(self, operation, variable_machine="machine", variable_machinetype="machine_type"):
        """
        Create 2 arrays used for the WHERE clause and the RETURN clause of the Cypher Query from this MACHINE
        Used to filter the database based on specifics properties values

        For this case, the properties of this object might be an array
        If a value in an array is "_" this property will be added to the return statement

        :param variable_machine: default "machine" to match a specific MACHINE
        :return: a tuple of arrays - where properties, return properties :
            (['machine.name = "bob','machine.manufacturer = "3", 'machine.location = "y"']['machine.location'])
        """
        cypherMatch = []
        cypherMatch.append(f'({self.cypher_machine_label(variable_machine)})')
        if self.machine_type:
            cypherMatch.append(f'({self.cypher_machinetype_label(variable_machinetype)})')

        return cypherMatch