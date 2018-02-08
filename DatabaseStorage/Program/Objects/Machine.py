from Program.Database.Database_Properties import NodeMachine
from Program.Database.Database_Properties import LabelEdges
from Program.Database.Database_Properties import NodeIssue


class Machine:
    """
        My utility is to represent the MACHINE data from a Maintenance Work Order.
        MACHINE are extracted from a CSV files and store in a Neo4J database using the my methods by create CYPHER queries
        Often they define my using my name

        In the database, I'm link to the node ISSUE with a label COVERED
        And also it is link to a node MACHINE_TYPE wiche store the type of the MACHINE with the label IS_A


        PARAMETERS:
            name            --  String to define the name of the MACHINE
            namufacturer    --  String to define the manufacruter of the MACHINE
            localisation    --  String for the localisation of the MACHINE
            type            --  String for the type of the MACHINE


       METHODS:
            toCypher        --  DEPRECIATE (use toCypherName and toCypherUpdate instead) Used to represent a Cypher query to Create a new MACHINE
            toCypherName    --  Used to represent a CYPHER query to represent a MACHINE in the database
            toCypherUpdate  --  Used to update the information of the node MACHINE in the database
            toCypherType    --  Used to represent the cypher query of the node MACHINE_TYPE
    """

    def __init__(self, name=None, manufacturer=None, locasion=None, machine_type=None):
        self.label_machine = NodeMachine.LABEL_MACHINE.value
        self.label_machine_type = NodeMachine.LABEL_MACHINE_TYPE.value
        self.property_name = NodeMachine.PROPERTY_NAME.value
        self.property_manufacturer = NodeMachine.PROPERTY_MANUFACTURER.value
        self.property_locasion = NodeMachine.PROPERTY_LOCASION.value
        self.property_type = NodeMachine.PROPERTY_TYPE.value
        self.label_link_machine = LabelEdges.LABEL_COVERED.value
        self.label_link_type = LabelEdges.LABEL_ISA.value

        self._set_name(name)
        self._set_manufacturer(manufacturer)
        self._set_locasion(locasion)
        self._set_machine_type(machine_type)

    def _get_name(self):
        """
        :return: the name of the MACHINE
        """
        return self.name

    def _set_name(self, name):
        """
        Set the Name of the MACHINE
        :param name: a string for the name
        """
        if name is "" or name is None:
            self.name = None
        else:
            try:
                self.name = name.lower().lstrip()
            except AttributeError:
                self.name = [n.lower().lstrip() for n in name]

    def _get_manufacturer(self):
        """
        :return: the manufacturer of the MACHINE
        """
        return self.manufacturer

    def _set_manufacturer(self, manufacturer):
        """
        set the name of the manufacturer
        :param manufacturer: a string for the namufacturer name
        """
        if manufacturer is "" or manufacturer is None:
            self.manufacturer = None
        else:
            try:
                self.manufacturer = manufacturer.lower()
            except AttributeError:
                self.manufacturer = [m.lower() for m in manufacturer]

    def _get_locasion(self):
        """
        :return: the localisation of the MACHINE
        """
        return self.locasion

    def _set_locasion(self, locasion):
        """
        Set the localisation of the MAHCINE
        :param locasion: a string for the localisation
        """
        if locasion is "" or locasion is None:
            self.locasion = None
        else:
            try:
                self.locasion = locasion.lower()
            except AttributeError:
                self.locasion = [l.lower() for l in locasion]

    def _get_machine_type(self):
        """
        :return: the type of the MACHINE
        """
        return self.machine_type

    def _set_machine_type(self, machine_type):
        """
        Set the type of the MACHINE
        :param
        """
        if machine_type is "" or machine_type is None:
            self.machine_type = None
        else:
            try:
                self.machine_type = machine_type.lower()
            except AttributeError:
                self.machine_type = [t.lower() for t in machine_type]

    def __str__(self):
        return f"{type(self)}\n\t" \
               f"Name: {self.name}\n\t" \
               f"Manufacturer: {self.manufacturer}\n\t" \
               f"Location: {self.locasion}\n\t" \
               f"Type: {self.machine_type}"

    def cypher_machine_name(self, variable="machine"):
        if self.name is None:
            return ""
        return f'({variable} {self.label_machine}' + \
               "{" + f'{self.property_name}:"{self.name}"' + "})"

    def cypher_machine_all(self, variable="machine"):
        query = f'({variable} {self.label_machine}'
        if self.name or self.manufacturer or self.locasion is not None:
            query += "{"
            if self.name is not None:
                query += f'{self.property_name}:"{self.name}",'
            if self.manufacturer is not None:
                query += f'{self.property_manufacturer}:"{self.manufacturer}",'
            if self.locasion is not None:
                query += f'{self.property_locasion}:"{self.locasion}",'
            query = query[:-1] + "}"
        return query + ")"

    def cypher_machine_type_name(self, variable="machine_type"):
        if self.machine_type is None:
            return ""
        return f'({variable} {self.label_machine_type}' + \
               "{" + f'{self.property_type}:"{self.machine_type}"' + "})"

    def cypher_machine_type_all(self, variable="machine_type"):
        query = f'({variable} {self.label_machine_type}'
        if self.machine_type is not None:
            query += "{" + f'{self.property_type}:"{self.machine_type}"' + "}"
        query += ")"

        return query

    def cypher_machine_create_node(self, variable="machine"):
        if self.name is None:
            return ""
        query = f'MERGE {self.cypher_machine_name(variable)}'
        if self.manufacturer is not None:
            query += f'\nSET {variable}.{self.property_manufacturer} = "{self.manufacturer}"'
        if self.locasion is not None:
            query += f'\nSET {variable}.{self.property_locasion} = "{self.locasion}"'
        return query

    def cypher_machine_type_create_node(self, variable="machine_type"):
        if self.name is None:
            return ""
        query = f'MERGE {self.cypher_machine_name(variable)}'
        return query

    def cypher_kpi(self, variable="machine", variable_type="machine_type"):

        match = f'MATCH (issue {NodeIssue.LABEL_ISSUE.value})-[{self.label_link_machine}]->({variable} {self.label_machine})'
        if self.machine_type is not None:
            match += f'-[{self.label_link_type}]->({variable_type} {self.label_machine_type})'
        where, res = self.cypher_where_properties(variable=variable, variable_type=variable_type)

        return match, " OR ".join(where), res

    def cypher_where_properties(self, variable="tag", variable_type="machine_type"):
        where = []
        res = []
        if self.name is not None:
            for n in self.name:
                if n == "_":
                    res.append(f'{variable}.{self.property_name}')
                else:
                    where.append(f'{variable}.{self.property_name} = "{n}"')

        if self.manufacturer is not None:
            for m in self.manufacturer:
                if m == "_":
                    where.append(f'{variable}.{self.property_manufacturer} = "{m}"')
                else:
                    res.append(f'{variable}.{self.property_manufacturer}')

        if self.locasion is not None:
            for l in self.locasion:
                if l == "_":
                    res.append(f'{variable}.{self.property_locasion}')
                else:
                    where.append(f'{variable}.{self.property_locasion} = "{l}"')

        if self.machine_type is not None:
            for m in self.machine_type:
                if m == "_":
                    res.append(f'{variable_type}.{self.property_type}')
                else:
                    where.append(f'{variable_type}.{self.property_type} = "{m}"')

        return where, res
