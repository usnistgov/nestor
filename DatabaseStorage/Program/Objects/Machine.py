from Program.Database.Database_Properties import NodeMachine

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

    def __init__(self, name, manufacturer=None, locasion=None, type=None):
        self._set_name(name)
        self._set_manufacturer(manufacturer)
        self._set_locasion(locasion)
        self._set_type(type)


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
        if name is "":
            name = "unknown"
        self.name = name

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
        if manufacturer is "":
            manufacturer = None
        self.manufacturer = manufacturer

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
        if locasion is "":
            locasion = None
        self.locasion = locasion

    def _get_type(self):
        """
        :return: the type of the MACHINE
        """
        return self.type

    def _set_type(self, type):
        """
        Set the type of the MACHINE
        :param type: a string for the type
        """
        if type is "":
            type = None
        self.type = type

    def __str__(self):
        return "OBJECT: %s --> Name: %s || Manufacturer: %s || Location: %s || Type: %s"%\
            (type(self), self.name, self.manufacturer, self.locasion, self.type)

    def toCypher(self, variable):

        """
           DEPRECIATE (use toCypherName and toCypherUpdate instead)
           Used to create a Cypher query node corresponding to a MACHINE

           The problem is that it create a new MACHINE even if one already has the same name in tha database
           but if the new one has more parameters

           :param variable: a string to define the variable of the node in CYPHER. It is used to reuse the given node MACHINE
           :return: a String representing a Cypher query corresponding to a full MACHINE

        """
        if self.name is None:
            return ""

        query = '(%s %s {%s: "%s"'%\
                (variable, NodeMachine.LABEL_MACHINE.value, NodeMachine.PROPERTY_NAME.value, self.name)
        if self.manufacturer is not None:
            query+=', %s: "%s"'%\
                    (NodeMachine.PROPERTY_MANUFACTURER.value, self.manufacturer)
        if self.locasion is not None:
            query+=', %s: "%s"'%\
                    (NodeMachine.PROPERTY_LOCASION.value, self.locasion)
        query+="})"
        return query

    def toCypherType(self, variable):
        """
        Used to create a CYPHER query corresponding to a MACHINE_TYPE

        :param variable: a string to define the variable of the node in CYPHER. It is used to reuse the given node MACHINE_TYPE
        :return: a String representing a Cypher query corresponding to a MACHINE_TYPE
        """
        if self.type is None:
            return ""
        return '(%s %s {%s: "%s"})'%\
            (variable, NodeMachine.LABEL_MACHINE_TYPE.value, NodeMachine.PROPERTY_TYPE.value, self.type)

    def toCypherName(self, variable):
        """
        Used to create a CYPHER query corresponding to a MACHINE only using the name

        :param variable:  a string to define the variable of the node in CYPHER. It is used to reuse the given node MACHINE
        :return: a String representing a Cypher query corresponding to a MACHINE
        """
        if self.name is None:
            return ""
        return '(%s %s {%s: "%s"})' % \
                (variable, NodeMachine.LABEL_MACHINE.value, NodeMachine.PROPERTY_NAME.value, self.name)

    def toCypherUpdate(self, variable):
        """
        Use to to complete the description of the node MACHINE using the information of Manufacturer and Localisation

        :param variable: a string to define the variable of the node in cypher.
                        The variable has to link with a node MACHINE from your database (use toCypherName to find it)
        :return: a cypher query to specify a given MACHINE node by adding the work Manufacturer and Localisation
        """
        if self.manufacturer is None and self.locasion is None:
            return ""
        query = "SET "
        if self.manufacturer is not None:
            query += '%s.%s="%s",' % \
                     (variable, NodeMachine.PROPERTY_MANUFACTURER.value, self.manufacturer)
        if self.locasion is not None:
            query += '%s.%s="%s",' % \
                     (variable, NodeMachine.PROPERTY_LOCASION.value, self.locasion)
        return query[:-1]
