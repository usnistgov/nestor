from Program.Database.Database_Properties import NodeTag

class Tag:
    """
    its utility is to represent the TAG data from a Maintenance Work Order.
    TAG are extracted from a CSV files and store in a Neo4J database using the my methods by create CYPHER queries
    Often they define my using my keyword

    In the database a TAG can be a ProblemAction_PA, a ProblemItem_PI, a SolutionAction_SA or a SolutionItem_SI
        The ACTION/ITEM definition is store in my node
        The PROBLEM/SOLUTION is tore with the link between ISSUE and TAG

    In the future it might be a abstract class of the classes ITEM and ACTION.
    And also it might store more than a 1graqmme (single word) tag but a 2,3,4,... grammes


    PARAMETERS:
        keyword    --  String to define the keyword of the TAG

    METHODS:
        toCypher    --  Used to create a Cypher query to represent a new TAG
    """

    def __init__(self, keyword):
        self._set_keyword(keyword)

    def _get_keyword(self):
        """
        :return: the keyword of the TAG
        """
        return self.keyword

    def _set_keyword(self, keyword):
        """
        set the keyword of a TAG
        :param keyword: a String for the keyword
        """
        if keyword is "":
            keyword="unknown"
        self.keyword = keyword

    def __str__(self):
        return "OBJECT: %s --> Keyword: %s "%\
            (type(self), self.keyword)

    def toCypher(self, variable, type):
        """
        Used to create a CYPHER query corresponding to a TAG

        :param variable:  a string to define the variable of the node in CYPHER. It is used to reuse the given node TAG
        :param type: A LABEL from the Enumeration store in the file DatabaseProperty.py
                    it represent the type of a TAG (ITEM OR ACTION)
        :return: a String representing a Cypher query corresponding to a TAG
        """
        if self.keyword is None:
            return ""
        return '(%s %s %s {%s: "%s"})' % \
                (variable, NodeTag.LABEL_TAG.value, type.value, NodeTag.PROPERTY_KEYWORD.value, self.keyword)