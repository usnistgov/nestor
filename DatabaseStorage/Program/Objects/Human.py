import collections

from Program.Database.Database_Properties import NodeHuman


class Human:

    """

    Its utility is to represent the HUMAN data from a Maintenance Work Order.
    HUMAN are extracted from a CSV files and store in a Neo4J database using the my methods by create CYPHER queries
    Often defined using my name (it needs a name)

    In the database it can be a OPERATOR or a TECHNICIAN,
        If it is an OPERATOR, it only have a a parameter name and it is link to the node ISSUE with an edges REQUESTED_BY
        If it is a TECHNICIAN, it have the parameter name, skills and crafts and it is link to the node ISSUE with an edges SOLVE_BY


    In the future it might be a abstract class of the classes TECHNICIAN and OPERATOR.

    PARAMETERS:
        name    --  String to define the name of the HUMAN
        skills  --  Array of string to define all skills of this HUMAN based on the KPI he solved (only for TECHNICIAN)
        crafts  --  Array of string to define all crafts of this HUMAN based on the KPI he solved (only for TECHNICIAN)


    METHODS:
        toCypher        --  DEPRECIATE (use toCypherName and toCypherUpdate instead) Used to represent a Cypher query to Create a new HUMAN
        toCypherName    --  Used to represent a CYPHER query to represent a HUMAN in the database using the name
        toCypherUpdate  --  Used to update the information of the node HUMAN in the database
                            If in the database a HUMAN already have my name, It updated it and add skills and crafts
    """

    def __init__(self, name, skills=None, crafts=None):
        self._set_name(name)
        self._set_skills(skills)
        self._set_crafts(crafts)

    def _get_name(self):
        """
        :return: the name of the HUMAN
        """
        return self.name

    def _set_name(self, name):
        """
        Set the name of the HUMAN
        if the name is empty "" it became "unknown"

        :param name: a String
        """
        if name is "" or name is None:
            name = "unknown"
        self.name = name.title()

    def _get_skills(self):
        """
        :return: the skills of the HUMAN
        """
        return self.skills

    def _set_skills(self, skills):
        """
        Set the skills of the HUMAN
        The skills is store in an array

        :param skills: an Array of String or a String
        """
        if skills is "" or skills is None:
            self.skills = None
        if skills is not None:
            if not isinstance(skills, collections.Iterable) or isinstance(skills, str):
                    skills = [skills]
        self.skills = skills

    def _get_crafts(self):
        """
        :return: the crafts of the Human
        """
        return self.crafts

    def _set_crafts(self, crafts):
        """
        Set the crafts of the HUMAN
        The crafts is store in an array

        :param crafts: an Array of String or a String
        """
        if crafts is "" or cratfs is None:
            crafts = None
        if not isinstance(crafts, collections.Iterable) or isinstance(crafts, str):
                crafts = [crafts]
        self.crafts = [craft.lower() for craft in crafts]

    def __str__(self):
        return "OBJECT: %s --> Name: %s || skills: %s || crafts: %s"%\
            (type(self), self.name, self.skills, self.crafts)

    def toCypher(self, variable, work):
        """
        DEPRECIATE (use toCypherName and toCypherUpdate instead)
        Used to create a Cypher query node corresponding to a HUMAN

        The problem is that it create a new HUMAN even if one already has the same name in tha database
        but if the new one has more parameters

        :param variable: a string to define the variable of the node in CYPHER. It is used to reuse the given node HUMAN
        :param work: A LABEL from the Enumeration store in the file DatabaseProperty.py
                    it represent the work of a HUMAN (TECHNICIAN OR OPERATOR)
        :return: a String representing a Cypher query corresponding to a full HUMAN
        """
        if self.name is None:
            return ""

        query = '(%s %s %s {%s:"%s"' \
                % (variable, NodeHuman.LABEL_HUMAN.value, work.value,  NodeHuman.PROPERTY_NAME.value, self.name)
        if self.skills is not None and len(self.skills) is not 0:
            query += ', %s:[' % (NodeHuman.PROPERTY_SKILLS.value)
            for i in range(0, len(self.skills)):
                query += '"%s",' % (self.skills[i])
            query = query[:-1] + "]"
        if self.crafts is not None and len(self.crafts) is not 0:
            query += ', %s:[' % NodeHuman.PROPERTY_CRAFTS.value
            for i in range(0, len(self.crafts)):
                query += '"%s",' % (self.crafts[i])
            query = query[:-1] + "]"

        query += "})"
        return query

    def toCypherName(self, variable):
        """
        Used to create a CYPHER query corresponding to a HUMAN only using the name

        :param variable: a string to define the variable of the node in CYPHER. It is used to reuse name the given node HUMAN
        :return: a String representing a Cypher query to corresponding to a HUMAN with only th name
        """
        if self.name is None:
            return ""
        return '(%s %s {%s: "%s"})' % \
                (variable, NodeHuman.LABEL_HUMAN.value, NodeHuman.PROPERTY_NAME.value, self.name)

    def toCypherUpdate(self, variable, work=None):
        """
        Used to set the work of a given HUMAN (TECHNICIAN or OPERATOR)
        and to complete the description of the node HUMAN using the information of Skills and Crafts

        :param variable: a string to define the variable of the node in CYPHER.
                        The variable has to link with a node HUMAN from your database (use toCypherName to find it)
        :param work: A LABEL from the Enumeration store in the file DatabaseProperty.py
                    it represent the work of a HUMAN (TECHNICIAN OR OPERATOR)
        :return: a CYPHER query to specify a given HUMAN node by adding the work skills and crafts and set the work
        """
        query = ""
        if work is not None:
            query += "\nSET %s %s"% (variable, work.value)
        if self.skills is None and self.crafts is None:
            return query
        if self.skills is not None:
            for skill in self.skills:
                query += '\nFOREACH(x in CASE WHEN "%s" in %s.%s THEN [] ELSE [1] END |' \
                         '  SET %s.%s = coalesce(%s.%s,[]) + "%s" )' %\
                         (skill, variable, NodeHuman.PROPERTY_SKILLS.value, variable, NodeHuman.PROPERTY_SKILLS.value, variable, NodeHuman.PROPERTY_SKILLS.value, skill)
        if self.crafts is not None:
            for craft in self.crafts:
                query += '\nFOREACH(x in CASE WHEN "%s" in %s.%s THEN [] ELSE [1] END |' \
                         '  SET %s.%s = coalesce(%s.%s,[]) + "%s" )' %\
                         (craft, variable, NodeHuman.PROPERTY_CRAFTS.value, variable, NodeHuman.PROPERTY_CRAFTS.value, variable, NodeHuman.PROPERTY_CRAFTS.value, craft)

        return query

"""
    def fromCypher(self, result):
        self._set_name(result[NodeHuman.PROPERTY_NAME.value])
        self._set_skills(result[NodeHuman.PROPERTY_SKILLS.value])
        self._set_crafts(result[NodeHuman.PROPERTY_CRAFTS.value])
"""