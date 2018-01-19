import collections

from Program.Database.Database_Properties import NodeTag
from Program.Database.Database_Properties import LabelEdges

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

    def __init__(self, keyword=None, synonyms=None, links=None):
        self.label_tag=NodeTag.LABEL_TAG.value
        self.property_keyword=NodeTag.PROPERTY_KEYWORD.value
        self.property_synonyms=NodeTag.PROPERTY_SYNONYMS.value
        self.property_links=NodeTag.PROPERTY_LINKS.value

        self._set_keyword(keyword)
        self._set_synonyms(synonyms)
        self._set_links(links)

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
        if keyword is "" or keyword is None:
            self.keyword = None
        else:
            self.keyword = keyword.lower()

    def _get_synonyms(self):
        """
        :return: the keyword of the TAG
        """
        return self.synonyms

    def _set_synonyms(self, synonyms):
        """
        set the keyword of a TAG
        :param keyword: a String for the keyword
        """
        if synonyms is "" or synonyms is None:
            self.synonyms = None
        else:
            if not isinstance(synonyms, collections.Iterable) or isinstance(synonyms, str):
                synonyms = [synonyms]
            self.synonyms = [synonym.lower() for synonym in synonyms]

    def _get_links(self):
        """
        :return: the keyword of the TAG
        """
        return self.links

    def _set_links(self, links):
        """
        set the keyword of a TAG
        :param keyword: a String for the keyword
        """
        if links is "" or links is None:
            self.links = None
        else:
            tmp = []
            if not isinstance(links, collections.Iterable):
                links = [links]
            for link in links:
                if isinstance(link, Tag):
                    tmp.append(link)
            self.links = tmp

    def _get_parents(self):
        """
        :return: the keyword of the TAG
        """
        return self.parents

    def _set_parents(self, parents):
        """
        set the keyword of a TAG
        :param keyword: a String for the keyword
        """
        if parents is "" or parents is None:
            self.parents = None
        else:
            tmp = []
            if not isinstance(parents, collections.Iterable):
                parents = [parents]
            for parent in parents:
                if isinstance(parent, Tag):
                    tmp.append(parent)
            self.parents = tmp

    def __str__(self):
        return f"OBJECT: {type(self)}\n\t" \
               f"Keyword: {self.keyword}\n\t" \
               f"Synonyms: {self.synonyms}\n\t" \
               f"Links: {self.links} "

    def cypher_tag_keyword(self, variable="tag"):
        if self.keyword is None:
            return ""
        return f'({variable} {self.label_tag}' + \
               "{" + f'{self.property_keyword}:"{self.keyword}"' + "})"

    def cypher_tag_all(self, variable="tag"):
        query = f'({variable} {self.label_tag}'
        if self.keyword or self.synonyms is not None:
            query += "{"
            if self.keyword is not None:
                query += f'{self.property_keyword}:"{self.keyword}",'
            if self.synonyms is not None:
                query += f'{self.property_synonyms}:' + '["' + '","'.join(self.synonyms) + '"],'
            query = query[:-1] + "}"
        return query + ")"

    def cypher_tag_create_node(self, variable="tag"):
        if self.keyword is None:
            return ""
        query = f'MERGE {self.cypher_tag_keyword(variable)}'
        if self.synonyms is not None:
            for synonym in self.synonyms:
                query += f'\nFOREACH(x in CASE WHEN "{synonym}" in {variable}.{self.property_synonyms} THEN [] ELSE [1] END |' \
                         f' SET {variable}.{self.property_synonyms} = coalesce({variable}.{self.property_synonyms},[]) + "{synonym}" )'
        return query

class TagAction(Tag):

    def __init__(self, keyword=None, synonyms=None, links=None):
        self.label_action = NodeTag.LABEL_ACTION.value

        super().__init__(keyword, synonyms, links)

    def __str__(self):
        return f"OBJECT: {type(self)}\n\t" \
               f"Keyword: {self.keyword}\n\t" \
               f"Synonyms: {self.synonyms}\n\t" \
               f"Links: {self.links} "

    def cypher_action_keyword(self, variable="tag_action"):
        if self.keyword is None:
            return ""
        return f'({variable} {self.label_tag}{self.label_action}' +\
               "{" + f'{self.property_keyword}:"{self.keyword}"' + "})"

    def cypher_action_all(self, variable="tag_action"):
        query = f'({variable} {self.label_tag}{self.label_action}'
        if self.keyword or self.synonyms is not None:
            query += "{"
            if self.keyword is not None:
                query += f'{self.property_keyword}:"{self.keyword}",'
            if self.synonyms is not None:
                query += f'{self.property_synonyms}:' + '["' + '","'.join(self.synonyms) + '"],'
            query = query[:-1] + "}"
        return query + ")"

    def cypher_action_create_node(self, variable="tag_action"):
        if self.keyword is None:
            return ""
        query = f'{self.cypher_tag_create_node(variable)}' \
                f'\nSET {variable} {self.label_action}'

        return query

class TagUnknown(Tag):

    def __init__(self, keyword=None, synonyms=None, links=None):
        self.label_unknown = NodeTag.LABEL_UNKNOWN.value

        super().__init__(keyword, synonyms, links)

    def __str__(self):
        return f"OBJECT: {type(self)}\n\t" \
               f"Keyword: {self.keyword}\n\t" \
               f"Synonyms: {self.synonyms}\n\t" \
               f"Links: {self.links} "

    def cypher_unknown_keyword(self, variable="tag_unknown"):
        if self.keyword is None:
            return ""
        return f'({variable} {self.label_tag}{self.label_unknown}' + \
               "{" + f'{self.property_keyword}:"{self.keyword}"' + "})"

    def cypher_unknown_all(self, variable="tag_unknown"):
        query = f'({variable} {self.label_tag}{self.label_unknown}'
        if self.keyword or self.synonyms is not None:
            query += "{"
            if self.keyword is not None:
                query += f'{self.property_keyword}:"{self.keyword}",'
            if self.synonyms is not None:
                query += f'{self.property_synonyms}:' + '["' + '","'.join(self.synonyms) + '"],'
            query = query[:-1] + "}"
        return query + ")"

    def cypher_unknown_create_node(self, variable="tag_unknown"):
        if self.keyword is None:
            return ""
        query = f'{self.cypher_tag_create_node(variable)}' \
                f'\nSET {variable} {self.label_unknown}'
        return query

class TagItem(Tag):

    def __init__(self, keyword=None, synonyms=None, links=None, parents=None):
        self.label_item = NodeTag.LABEL_ITEM.value
        self.property_parents = NodeTag.PROPERTY_PARENTS.value

        super().__init__(keyword, synonyms, links)
        self._set_parents(parents)

    def __str__(self):
        return f"OBJECT: {type(self)}\n\t" \
               f"Keyword: {self.keyword}\n\t" \
               f"Synonyms: {self.synonyms}\n\t" \
               f"Links: {self.links} " \
               f"Parents: {self.parents}\n\t"

    def cypher_item_keyword(self, variable="tag_item"):
        if self.keyword is None:
            return ""
        return f'({variable} {self.label_tag}{self.label_item}' + \
               "{" + f'{self.property_keyword}:"{self.keyword}"' + "})"

    def cypher_item_all(self, variable="tag_item"):
        query = f'({variable} {self.label_tag}{self.label_item}'
        if self.keyword or self.synonyms is not None:
            query += "{"
            if self.keyword is not None:
                query += f'{self.property_keyword}:"{self.keyword}",'
            if self.synonyms is not None:
                query += f'{self.property_synonyms}:' + '["' + '","'.join(self.synonyms) + '"],'
            query = query[:-1] + "}"
        return query + ")"

    def cypher_item_create_node(self, variable="tag_item"):
        if self.keyword is None:
            return ""
        query = f'{self.cypher_tag_create_node(variable)}' \
                f'\nSET {variable} {self.label_item}'

        return query


class TagActionItem(Tag):
    def __init__(self, keyword=None, synonyms=None, links=None, parents=None):
        self.label_action_item = NodeTag.LABEL_ACTION_ITEM.value
        self.property_parents = NodeTag.PROPERTY_PARENTS.value

        super().__init__(keyword, synonyms, links)
        self._set_parents(parents)

    def __str__(self):
        return f"OBJECT: {type(self)}\n\t" \
               f"Keyword: {self.keyword}\n\t" \
               f"Synonyms: {self.synonyms}\n\t" \
               f"Links: {self.links} " \
               f"Parents: {self.parents}\n\t"

    def cypher_action_item_keyword(self, variable="tag_action_item"):
        if self.keyword is None:
            return ""
        return f'({variable} {self.label_tag}{self.label_action_item}' + \
               "{" + f'{self.property_keyword}:"{self.keyword}"' + "})"

    def cypher_action_item_all(self, variable="tag_action_item"):
        query = f'({variable} {self.label_tag}{self.label_action_item}'
        if self.keyword or self.synonyms is not None:
            query += "{"
            if self.keyword is not None:
                query += f'{self.property_keyword}:"{self.keyword}",'
            if self.synonyms is not None:
                query += f'{self.property_synonyms}:' + '["' + '","'.join(self.synonyms) + '"],'
            query = query[:-1] + "}"
        return query + ")"

    def cypher_action_item_create_node(self, variable="tag_action_item"):
        if self.keyword is None:
            return ""
        query = f'{self.cypher_tag_create_node(variable)}' \
                f'\nSET {variable} {self.label_action_item}'

        return query
