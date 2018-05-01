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
   This file contains the object TAG, TAGONEGRAM, TAGITEM, TAGPROBLEM, TAGSOLUTION, TAGUNKNOWN,
   TAGNGRAM, TAGPROBLEMITEM, TAGSOLUTIONITEM  that follow the given hierarchy:
   TAG
       TAGONEGRAM
            TAGITEM
            TAGPROBLEM
            TAGSOLUTION
            TAGUNKNOWN
       TAGNGRAM
            TAGPROBLEMITEM
            TAGSOLUTIONITEM

    This tags have been extracted from Unstructured Natural Language Raw Text by a tool built for this project
    - see file kex.py as well as the User Interface to interact with it in tagginUI folder -
    A tag represent a world that represent different world (named token) with the same meaning

    They have been classify based on our problem but it is a container that represent our world (maintenance work order data)
    In the database the node label and the properties key can be easily changed in the YAML file DatabaseSchema.YAML

    In the database, only the name of the properties can changed but not the type of data or the number of properties
    (you can have less but not more)
    However, the hierarchy followed the rules created in this file
"""
class Tag:
    """
     a TAG defines every information that refer to all the node TAG in our database.
     It setup the properties and query to match with every subclass of the Hierarchy in the database
     A TAG is define with a property KEYWORD in the database as well as the SYNONYMS that is a list of token

     It is instantiate using:
         - keyword : a String or array of string
         - synonyms : array of string
         - similarTo : array of string
         - databaseInfo: the dictionary that describe the database information (name of properties, and Label)

     It contains getter and setter for every properties, it is highly recommend to use the setter
      because it represent the data as a standard way - the way it is store in the database
     It contains a string representation
     It contains a boolean representation
     """

    def __init__(self, keyword=None, synonyms=None, similarTo=None, databaseInfo=None):
        self.databaseInfoTag = databaseInfo['tag']

        self._set_keyword(keyword)
        self._set_synonyms(synonyms)
        self._set_similarTo(similarTo, databaseInfo)

    def _get_keyword(self):
        return self.keyword

    def _set_keyword(self, keyword):
        if isinstance(keyword, str):
            self.keyword = keyword.lower().lstrip().replace('"','\\"')
        elif isinstance(keyword,list):
            self.keyword = [k.lower().lstrip().replace('"','\\"') for k in keyword]
        else:
            self.keyword = None

    def _get_synonyms(self):
        return self.synonyms

    def _set_synonyms(self, synonyms):
        if isinstance(synonyms, str):
            self.synonyms = synonyms.lower().lstrip().replace('"', '\\"')
        elif isinstance(synonyms, list):
            self.synonyms = [s.lower().lstrip().replace('"', '\\"') for s in synonyms]
        else:
            self.synonyms = None

    def _get_similarTo(self):
        return self.similarTo

    def _set_similarTo(self, similarTo, databaseInfo):
        if isinstance(similarTo, str):
            self.similarTo = [Tag(keyword=similarTo, databaseInfo=databaseInfo)]
        elif isinstance(similarTo, list):
            tmp = []
            for s in similarTo:
                if isinstance(s, str):
                    tmp.append(Tag( keyword=s, databaseInfo=databaseInfo))
                elif isinstance(s, Tag):
                    tmp.append(s)
            if tmp:
                self.similarTo = tmp
            else:
                self.similarTo = None
        else:
            self.similarTo = None

    def __bool__(self):
        return not(
            (self.keyword is None) and
            (self.synonyms is None)
        )

    def __str__(self):
        return f"OBJECT: {type(self)}\n\t" \
               f"Keyword: {self.keyword}\n\t" \
               f"Synonyms: {self.synonyms}\n\t" \
               f"similarTo: {self.similarTo}\n\t" \

    def cypher_tag_label(self, variable_tag="tag"):
        """
        Create a Cypher query with the given variable and all label for the node TAG
        :param variable_tag: default "tag" to refer to a special node
        :return: a string - Cypher Query : tag:TAG
        """
        return f'{variable_tag}{self.databaseInfoTag["label"]["tag"]}'

    def cypher_tag_keyword(self, variable_tag="tag"):
        """
         Create a Cypher query to return the specific node TAG define by the property KEYWORD
         :param variable_tag: default "tag" to refer to a special node
         :return: a string - Cypher Query : (tag:TAG{keyword:"x"})
             OR empty string if the TAG has no KEYWORD
         """
        if not self.keyword:
            return ""
        return f'({self.cypher_tag_label(variable_tag)}' + \
               "{" + f'{self.databaseInfoTag["properties"]["keyword"]}:"{self.keyword}"' + "})"

    def cypher_tag_all(self, variable_tag="tag"):
        """
        Create a Cypher query to return the specific node TAG define by all the possible properties (KEYWORD, SYNONYMS)
        :param variable_tag: default "tag" to refer to a specific TAG
        :return: a string - Cypher Query : (tag:TAG{keyword:"x", synonyms:["x","y"]})
        """
        query = f'({self.cypher_tag_label(variable_tag)}'
        if self.keyword or self.synonyms is not None:
            query += "{"
            if self.keyword is not None:
                query += f'{self.databaseInfoTag["properties"]["keyword"]}:"{self.keyword}",'
            if self.synonyms is not None:
                query += f'{self.databaseInfoTag["properties"]["synonyms"]}:' + '["' + '","'.join(self.synonyms) + '"],'
            query = query[:-1] + "}"
        return query + ")"

    def cypher_tag_merge(self, variable_tag="tag"):
        """
         Create a Cypher query to merge the node TAG using his property KEYWORD
         and Set the missing properties (SYNONYMS)
         :param variable_tag: default "tag" to refer to a specific TAG
         :return: a string - Cypher Query : MERGE (tag:TAG{keyword:"x"})
                                            SET tag.synonyms = ["x","y"]
                in the database, SYNONYMS is an array, so we add values to the array if not already in
         """
        if not self.keyword:
            return ""
        query = f'\nMERGE {self.cypher_tag_keyword(variable_tag)}'
        if self.synonyms:
            for synonym in self.synonyms:
                query += f'\nFOREACH(x in CASE WHEN "{synonym}" in {variable_tag}.{self.databaseInfoTag["properties"]["synonyms"]} THEN [] ELSE [1] END |' \
                         f' SET {variable_tag}.{self.databaseInfoTag["properties"]["synonyms"]} = coalesce({variable_tag}.{self.databaseInfoTag["properties"]["synonyms"]},[]) + "{synonym}" )'

        return query

    def cypher_tag_whereReturn(self, variable_tag="tag"):
        """
        Create 2 arrays used for the WHERE clause and the RETURN clause of the Cypher Query from this TAG
        Used to filter the database based on specifics properties values

        For this case, the properties of this object might be an array
        If a value in an array is "_" this property will be added to the return statement

        :param variable_tag: default "tag" to match a specific TAG
        :return: a tuple of arrays - where properties, return properties :
            (['tag.keyword = "bob','tag.keyword = "3"]['tag.synonyms'])
        """
        cypherWhere = []
        cypherReturn = []

        if self.keyword:
            for k in self.keyword:
                if k == "_":
                    cypherReturn.append(f'{variable_tag}.{self.databaseInfoTag["properties"]["keyword"]}')
                else:
                    cypherWhere.append(
                        f'{variable_tag}.{self.databaseInfoTag["properties"]["keyword"]} = "{k}"')

        if self.synonyms:
            for s in self.synonyms:
                if s == "_":
                    cypherReturn.append(f'{variable_tag}.{self.databaseInfoTag["properties"]["synonyms"]}')
                else:
                    cypherWhere.append(f'"{s}" IN {variable_tag}.{self.databaseInfoTag["properties"]["synonyms"]}')

        return cypherWhere, cypherReturn


class TagOneGram(Tag):
    """
    An TAGONEGRAM inherit from TAG
     it defines every information that refer to all the node TAGONEGRAM in our database.
     It setup the properties and query to match with every subclass of the Hierarchy in the database
     A TAGONEGRAM is define with a property KEYWORD in the database as well as the SYNONYMS that is a list of token

     It is instantiate using:
         - keyword : a String or array of string
         - synonyms : array of string
         - similarTo : array of string
         - databaseInfo: the dictionary that describe the database information (name of properties, and Label)

     It contains getter and setter for every properties, it is highly recommend to use the setter
      because it represent the data as a standard way - the way it is store in the database
     It contains a string representation
     It contains a boolean representation
     """

    def __init__(self, keyword=None, synonyms=None, similarTo=None, databaseInfo=None):
        super().__init__(keyword, synonyms, similarTo, databaseInfo)

    def __bool__(self):
        return not (
            (self.keyword is None) and
            (self.synonyms is None)
        )

    def __str__(self):
        return f"OBJECT: {type(self)}\n\t" \
               f"Keyword: {self.keyword}\n\t" \
               f"Synonyms: {self.synonyms}\n\t" \
               f"similarTo: {self.similarTo}\n\t" \

    def cypher_oneGramTag_label(self, variable_tagOnGram="onegram_tag"):
        """
        Create a Cypher query with the given variable and all label for the node TAGONEGRAM
        :param variable_tagOnGram: default "onegram_tag" to refer to a special node
        :return: a string - Cypher Query : onegram_tag:TAG:TAGONEGRAM
        """
        return f'{self.cypher_tag_label(variable_tagOnGram)}{self.databaseInfoTag["label"]["onegram"]}'

    def cypher_oneGramTag_keyword(self, variable_tagOnGram="onegram_tag"):
        """
         Create a Cypher query to return the specific node TAGONEGRAM define by the property KEYWORD
         :param variable_tagOnGram: default "onegram_tag" to refer to a special node
         :return: a string - Cypher Query : (onegram_tag:TAG:TAGONEGRAM{keyword:"x"})
             OR empty string if the TAGONEGRAM has no KEYWORD
         """

        if not self.keyword:
            return ""
        return f'({self.cypher_oneGramTag_label(variable_tagOnGram)}' + \
               "{" + f'{self.databaseInfoTag["properties"]["keyword"]}:"{self.keyword}"' + "})"

    def cypher_oneGramTag_all(self, variable_tagOnGram="onegram_tag"):
        """
        Create a Cypher query to return the specific node TAGONEGRAM define by all the possible properties (KEYWORD, SYNONYMS)
        :param variable_tagOnGram: default "onegram_tag" to refer to a specific TAGONEGRAM
        :return: a string - Cypher Query : (onegram_tag:TAG:TAGONEGRAM{keyword:"x", synonyms:["x","y"]})
        """

        query = f'({self.cypher_oneGramTag_label(variable_tagOnGram)}'
        if self.keyword or self.synonyms is not None:
            query += "{"
            if self.keyword:
                query += f'{self.databaseInfoTag["properties"]["keyword"]}:"{self.keyword}",'
            if self.synonyms:
                query += f'{self.databaseInfoTag["properties"]["synonyms"]}:' + '["' + '","'.join(self.synonyms) + '"],'
            query = query[:-1] + "}"
        return query + ")"

    def cypher_oneGramTag_merge(self, variable_tagOnGram="onegram_tag"):
        """
           Create a Cypher query to merge the node TAGONEGRAM using his property KEYWORD
           and Set the missing properties (SYNONYMS)
           :param variable_tagOnGram: default "onegram_tag" to refer to a specific TAG
           :return: a string - Cypher Query : MERGE (onegram_tag:TAG:TAGONEGRAM{keyword:"x"})
                                              SET onegram_tag.synonyms = ["x","y"]
                  in the database, SYNONYMS is an array, so we add values to the array if not already in
           """
        if self.cypher_tag_merge(variable_tagOnGram) == "":
            return ""
        query = self.cypher_tag_merge(variable_tagOnGram)
        query += f'\nSET {variable_tagOnGram} {self.databaseInfoTag["label"]["onegram"]}'
        return query



    def cypher_oneGramTag_whereReturn(self, variable_tagOnGram="onegram_tag"):
        """
        Create 2 arrays used for the WHERE clause and the RETURN clause of the Cypher Query from this TAGONEGRAM
        Used to filter the database based on specifics properties values

        For this case, the properties of this object might be an array
        If a value in an array is "_" this property will be added to the return statement

        :param variable_tagOnGram: default "onegram_tag" to match a specific TAGONEGRAM
        :return: a tuple of arrays - where properties, return properties :
            (['onegram_tag.keyword = "bob','onegram_tag.keyword = "3"]['onegram_tag.synonyms'])
        """
        cypherWhere, cypherReturn = self.cypher_tag_whereReturn(variable_tagOnGram)

        return cypherWhere, cypherReturn

class TagItem(TagOneGram):
    """
    An TAGITEM inherit from TAGONEGRAM and so from TAG
     it defines every information that refer to all the node TAGITEM in our database.
     A TAGITEM is define with a property KEYWORD in the database as well as the SYNONYMS that is a list of token
     and also the CHILDREN it is used to create a hierarchy of ITEM in a tree

     It is instantiate using:
         - keyword : a String or array of string
         - synonyms : array of string
         - similarTo : array of string
         - children : array of string
         - databaseInfo: the dictionary that describe the database information (name of properties, and Label)

     It contains getter and setter for every properties, it is highly recommend to use the setter
      because it represent the data as a standard way - the way it is store in the database
     It contains a string representation
     It contains a boolean representation
     """

    def __init__(self, keyword=None, synonyms=None, similarTo=None, children=None, databaseInfo=None):
        super().__init__(keyword, synonyms, similarTo, databaseInfo)
        self._set_children(children, databaseInfo)

    def _get_children(self):
        return self.children

    def _set_children(self, children, databaseInfo):
        if isinstance(children, str):
            self.children = [TagItem(keyword=children, databaseInfo=databaseInfo)]
        elif isinstance(children, list):
            tmp = []
            for c in children:
                if isinstance(c, str):
                    tmp.append(TagItem( keyword=c, databaseInfo=databaseInfo))
                elif isinstance(c, Tag):
                    tmp.append(c)
            if tmp:
                self.children = tmp
            else:
                self.children = None
        else:
            self.children = None


    def __bool__(self):
        return not (
            (self.keyword is None) and
            (self.synonyms is None) and
            (self.children is None)
        )


    def __str__(self):
        return f"OBJECT: {type(self)}\n\t" \
               f"Keyword: {self.keyword}\n\t" \
               f"Synonyms: {self.synonyms}\n\t" \
               f"similarTo: {self.similarTo} \n\t" \
               f"children: {self.children}\n\t"

    def cypher_itemTag_label(self, variable_tagItem="tag_item"):
        """
        Create a Cypher query with the given variable and all label for the node TAGITEM
        :param variable_tagItem: default "tag_item" to refer to a special node
        :return: a string - Cypher Query : tag_item:TAG:TAGONEGRAM:TAGITEM
        """
        return f'{self.cypher_oneGramTag_label(variable_tagItem)}{self.databaseInfoTag["label"]["item"]}'

    def cypher_itemTag_keyword(self, variable_tagItem="tag_item"):
        """
         Create a Cypher query to return the specific node TAGITEM define by the property KEYWORD
         :param variable_tagItem: default "tag_item" to refer to a special node
         :return: a string - Cypher Query : (tag_item:TAG:TAGONEGRAM:TAGITEM{keyword:"x"})
             OR empty string if the TAGITEM has no KEYWORD
         """

        if not self.keyword:
            return ""
        return f'({self.cypher_itemTag_label(variable_tagItem)}' + \
               "{" + f'{self.databaseInfoTag["properties"]["keyword"]}:"{self.keyword}"' + "})"

    def cypher_itemTag_all(self, variable_tagItem="tag_item"):
        """
        Create a Cypher query to return the specific node TAGITEM define by all the possible properties (KEYWORD, SYNONYMS)
        :param variable_tagItem: default "tag_item" to refer to a specific TAGITEM
        :return: a string - Cypher Query : (tag_item:TAG:TAGONEGRAM:TAGITEM{keyword:"x", synonyms:["x","y"]})
        """
        query = f'({self.cypher_itemTag_label(variable_tagItem)}'
        if self.keyword or self.synonyms is not None:
            query += "{"
            if self.keyword:
                query += f'{self.databaseInfoTag["properties"]["keyword"]}:"{self.keyword}",'
            if self.synonyms:
                query += f'{self.databaseInfoTag["properties"]["synonyms"]}:' + '["' + '","'.join(self.synonyms) + '"],'
            query = query[:-1] + "}"
        return query + ")"

    def cypher_itemTag_merge(self, variable_tagItem="tag_item"):
        """
           Create a Cypher query to merge the node TAGITEM using his property KEYWORD
           and Set the missing properties (SYNONYMS)
           :param variable_tagItem: default "tag_item" to refer to a specific TAG
           :return: a string - Cypher Query : MERGE (tag_item:TAG:TAGONEGRAM:TAGITEM{keyword:"x"})
                                              SET tag_item.synonyms = ["x","y"]
                  in the database, SYNONYMS is an array, so we add values to the array if not already in
           """
        if self.cypher_oneGramTag_merge(variable_tagItem) == "":
            return ""

        query = self.cypher_oneGramTag_merge(variable_tagItem)
        query += f'\nSET {variable_tagItem} {self.databaseInfoTag["label"]["item"]}'
        return query


    def cypher_itemTag_whereReturn(self, variable_tagItem="tag_item"):
        """
        Create 2 arrays used for the WHERE clause and the RETURN clause of the Cypher Query from this TAGITEM
        Used to filter the database based on specifics properties values

        For this case, the properties of this object might be an array
        If a value in an array is "_" this property will be added to the return statement

        :param variable_tagItem: default "tag_item" to match a specific TAGITEM
        :return: a tuple of arrays - where properties, return properties :
            (['tag_item.keyword = "bob','tag_item.keyword = "3"]['tag_item.synonyms'])
        """
        cypherWhere, cypherReturn = self.cypher_oneGramTag_whereReturn(variable_tagItem)

        return cypherWhere, cypherReturn


class TagProblem(TagOneGram):
    """
    An TAGPROBLEM inherit from TAGONEGRAM and so from TAG
     it defines every information that refer to all the node TAGPROBLEM in our database.
     A TAGPROBLEM is define with a property KEYWORD in the database as well as the SYNONYMS that is a list of token

     It is instantiate using:
         - keyword : a String or array of string
         - synonyms : array of string
         - similarTo : array of string
         - databaseInfo: the dictionary that describe the database information (name of properties, and Label)

     It contains getter and setter for every properties, it is highly recommend to use the setter
      because it represent the data as a standard way - the way it is store in the database
     It contains a string representation
     It contains a boolean representation
     """

    def __init__(self, keyword=None, synonyms=None, similarTo=None, databaseInfo=None):
        super().__init__(keyword, synonyms, similarTo, databaseInfo)

    def __bool__(self):
        return not (
            (self.keyword is None) and
            (self.synonyms is None)
        )

    def __str__(self):
        return f"OBJECT: {type(self)}\n\t" \
               f"Keyword: {self.keyword}\n\t" \
               f"Synonyms: {self.synonyms}\n\t" \
               f"similarTo: {self.similarTo} "

    def cypher_problemTag_label(self, variable_tagProblem="tag_problem"):
        """
        Create a Cypher query with the given variable and all label for the node TAGPROBLEM
        :param variable_tagProblem: default "tag_problem" to refer to a special node
        :return: a string - Cypher Query : tag_problem:TAG:TAGONEGRAM:TAGPROBLEM
        """
        return f'{self.cypher_oneGramTag_label(variable_tagProblem)}{self.databaseInfoTag["label"]["problem"]}'

    def cypher_problemTag_keyword(self, variable_tagProblem="tag_problem"):
        """
         Create a Cypher query to return the specific node TAGPROBLEM define by the property KEYWORD
         :param variable_tagProblem: default "tag_problem" to refer to a special node
         :return: a string - Cypher Query : (tag_problem:TAG:TAGONEGRAM:TAGPROBLEM{keyword:"x"})
             OR empty string if the TAGPROBLEM has no KEYWORD
         """

        if not self.keyword:
            return ""
        return f'({self.cypher_problemTag_label(variable_tagProblem)}' + \
               "{" + f'{self.databaseInfoTag["properties"]["keyword"]}:"{self.keyword}"' + "})"

    def cypher_problemTag_all(self, variable_tagProblem="tag_problem"):
        """
        Create a Cypher query to return the specific node TAGPROBLEM define by all the possible properties (KEYWORD, SYNONYMS)
        :param variable_tagProblem: default "tag_problem" to refer to a specific TAGPROBLEM
        :return: a string - Cypher Query : (tag_problem:TAG:TAGONEGRAM:TAGPROBLEM{keyword:"x", synonyms:["x","y"]})
        """
        query = f'({self.cypher_problemTag_label(variable_tagProblem)}'
        if self.keyword or self.synonyms is not None:
            query += "{"
            if self.keyword:
                query += f'{self.databaseInfoTag["properties"]["keyword"]}:"{self.keyword}",'
            if self.synonyms:
                query += f'{self.databaseInfoTag["properties"]["synonyms"]}:' + '["' + '","'.join(self.synonyms) + '"],'
            query = query[:-1] + "}"
        return query + ")"

    def cypher_problemTag_merge(self, variable_tagProblem="tag_problem"):
        """
         Create a Cypher query to merge the node TAGPROBLEM using his property KEYWORD
         and Set the missing properties (SYNONYMS)
         :param variable_tagProblem: default "tag_problem" to refer to a specific TAG
         :return: a string - Cypher Query : MERGE (tag_problem:TAG:TAGONEGRAM:TAGPROBLEM{keyword:"x"})
                                            SET tag_problem.synonyms = ["x","y"]
                in the database, SYNONYMS is an array, so we add values to the array if not already in
         """
        if self.cypher_oneGramTag_merge(variable_tagProblem) == "":
            return ""

        query = self.cypher_oneGramTag_merge(variable_tagProblem)
        query += f'\nSET {variable_tagProblem} {self.databaseInfoTag["label"]["problem"]}'
        return query

    def cypher_problemTag_whereReturn(self, variable_tagProblem="tag_problem"):
        """
        Create 2 arrays used for the WHERE clause and the RETURN clause of the Cypher Query from this TAGPROBLEM
        Used to filter the database based on specifics properties values

        For this case, the properties of this object might be an array
        If a value in an array is "_" this property will be added to the return statement

        :param variable_tagProblem: default "tag_problem" to match a specific TAGPROBLEM
        :return: a tuple of arrays - where properties, return properties :
            (['tag_problem.keyword = "bob','tag_problem.keyword = "3"]['tag_problem.synonyms'])
        """
        cypherWhere, cypherReturn = self.cypher_oneGramTag_whereReturn(variable_tagProblem)

        return cypherWhere, cypherReturn


class TagSolution(TagOneGram):
    """
    An TAGSOLUTION inherit from TAGONEGRAM and so from TAG
     it defines every information that refer to all the node TAGSOLUTION in our database.
     A TAGSOLUTION is define with a property KEYWORD in the database as well as the SYNONYMS that is a list of token

     It is instantiate using:
         - keyword : a String or array of string
         - synonyms : array of string
         - similarTo : array of string
         - databaseInfo: the dictionary that describe the database information (name of properties, and Label)

     It contains getter and setter for every properties, it is highly recommend to use the setter
      because it represent the data as a standard way - the way it is store in the database
     It contains a string representation
     It contains a boolean representation
     """

    def __init__(self, keyword=None, synonyms=None, similarTo=None, databaseInfo=None):
        super().__init__(keyword, synonyms, similarTo, databaseInfo)

    def __bool__(self):
        return not (
            (self.keyword is None) and
            (self.synonyms is None)
        )

    def __str__(self):
        return f"OBJECT: {type(self)}\n\t" \
               f"Keyword: {self.keyword}\n\t" \
               f"Synonyms: {self.synonyms}\n\t" \
               f"similarTo: {self.similarTo} "

    def cypher_solutionTag_label(self, variable_tagSolution="tag_solution"):
        """
        Create a Cypher query with the given variable and all label for the node TAGSOLUTION
        :param variable_tagSolution: default "tag_solution" to refer to a special node
        :return: a string - Cypher Query : tag_solution:TAG:TAGONEGRAM:TAGSOLUTION
        """
        return f'{self.cypher_oneGramTag_label(variable_tagSolution)}{self.databaseInfoTag["label"]["solution"]}'

    def cypher_solutionTag_keyword(self, variable_tagSolution="tag_solution"):
        """
         Create a Cypher query to return the specific node TAGSOLUTION define by the property KEYWORD
         :param variable_tagSolution: default "tag_solution" to refer to a special node
         :return: a string - Cypher Query : (tag_solution:TAG:TAGONEGRAM:TAGSOLUTION{keyword:"x"})
             OR empty string if the TAGSOLUTION has no KEYWORD
         """

        if not self.keyword:
            return ""
        return f'({self.cypher_solutionTag_label(variable_tagSolution)}' + \
               "{" + f'{self.databaseInfoTag["properties"]["keyword"]}:"{self.keyword}"' + "})"

    def cypher_solutionTag_all(self, variable_tagSolution="tag_solution"):
        """
        Create a Cypher query to return the specific node TAGSOLUTION define by all the possible properties (KEYWORD, SYNONYMS)
        :param variable_tagSolution: default "tag_solution" to refer to a specific TAGSOLUTION
        :return: a string - Cypher Query : (tag_solution:TAG:TAGONEGRAM:TAGSOLUTION{keyword:"x", synonyms:["x","y"]})
        """
        query = f'({self.cypher_solutionTag_label(variable_tagSolution)}'
        if self.keyword or self.synonyms is not None:
            query += "{"
            if self.keyword:
                query += f'{self.databaseInfoTag["properties"]["keyword"]}:"{self.keyword}",'
            if self.synonyms:
                query += f'{self.databaseInfoTag["properties"]["synonyms"]}:' + '["' + '","'.join(self.synonyms) + '"],'
            query = query[:-1] + "}"
        return query + ")"

    def cypher_solutionTag_merge(self, variable_tagSolution="tag_solution"):
        """
         Create a Cypher query to merge the node TAGSOLUTION using his property KEYWORD
         and Set the missing properties (SYNONYMS)
         :param variable_tagSolution: default "tag_solution" to refer to a specific TAG
         :return: a string - Cypher Query : MERGE (tag_solution:TAG:TAGONEGRAM:TAGSOLUTION{keyword:"x"})
                                            SET tag_solution.synonyms = ["x","y"]
                in the database, SYNONYMS is an array, so we add values to the array if not already in
         """

        if self.cypher_oneGramTag_merge(variable_tagSolution) == "":
            return ""

        query = self.cypher_oneGramTag_merge(variable_tagSolution)
        query += f'\nSET {variable_tagSolution} {self.databaseInfoTag["label"]["solution"]}'
        return query

    def cypher_solutionTag_whereReturn(self, variable_tagSolution="tag_solution"):
        """
        Create 2 arrays used for the WHERE clause and the RETURN clause of the Cypher Query from this TAGSOLUTION
        Used to filter the database based on specifics properties values

        For this case, the properties of this object might be an array
        If a value in an array is "_" this property will be added to the return statement

        :param variable_tagSolution: default "tag_solution" to match a specific TAGSOLUTION
        :return: a tuple of arrays - where properties, return properties :
            (['tag_solution.keyword = "bob','tag_solution.keyword = "3"]['tag_solution.synonyms'])
        """
        cypherWhere, cypherReturn = self.cypher_oneGramTag_whereReturn(variable_tagSolution)

        return cypherWhere, cypherReturn


class TagUnknown(TagOneGram):
    """
    An TAGUNKNOWN inherit from TAGONEGRAM and so from TAG
     it defines every information that refer to all the node TAGUNKNOWN in our database.
     A TAGUNKNOWN is define with a property KEYWORD in the database as well as the SYNONYMS that is a list of token

     It is instantiate using:
         - keyword : a String or array of string
         - synonyms : array of string
         - similarTo : array of string
         - databaseInfo: the dictionary that describe the database information (name of properties, and Label)

     It contains getter and setter for every properties, it is highly recommend to use the setter
      because it represent the data as a standard way - the way it is store in the database
     It contains a string representation
     It contains a boolean representation
     """

    def __init__(self, keyword=None, synonyms=None, similarTo=None, databaseInfo=None):
        super().__init__(keyword, synonyms, similarTo, databaseInfo)

    def __bool__(self):
        return not (
            (self.keyword is None) and
            (self.synonyms is None)
        )

    def __str__(self):
        return f"OBJECT: {type(self)}\n\t" \
               f"Keyword: {self.keyword}\n\t" \
               f"Synonyms: {self.synonyms}\n\t" \
               f"similarTo: {self.similarTo} "

    def cypher_unknownTag_label(self, variable_tagUnknown="tag_unknown"):
        """
        Create a Cypher query with the given variable and all label for the node TAGUNKNOWN
        :param variable_tagUnknown: default "tag_unknown" to refer to a special node
        :return: a string - Cypher Query : tag_unknown:TAG:TAGONEGRAM:TAGUNKNOWN
        """
        return f'{self.cypher_oneGramTag_label(variable_tagUnknown)}{self.databaseInfoTag["label"]["unknown"]}'

    def cypher_unknownTag_keyword(self, variable_tagUnknown="tag_unknown"):
        """
         Create a Cypher query to return the specific node TAGUNKNOWN define by the property KEYWORD
         :param variable_tagUnknown: default "tag_unknown" to refer to a special node
         :return: a string - Cypher Query : (tag_unknown:TAG:TAGONEGRAM:TAGUNKNOWN{keyword:"x"})
             OR empty string if the TAGUNKNOWN has no KEYWORD
         """

        if not self.keyword:
            return ""
        return f'({self.cypher_unknownTag_label(variable_tagUnknown)}' + \
               "{" + f'{self.databaseInfoTag["properties"]["keyword"]}:"{self.keyword}"' + "})"

    def cypher_unknownTag_all(self, variable_tagUnknown="tag_unknown"):
        """
        Create a Cypher query to return the specific node TAGUNKNOWN define by all the possible properties (KEYWORD, SYNONYMS)
        :param variable_tagUnknown: default "tag_unknown" to refer to a specific TAGUNKNOWN
        :return: a string - Cypher Query : (tag_unknown:TAG:TAGONEGRAM:TAGUNKNOWN{keyword:"x", synonyms:["x","y"]})
        """
        query = f'({self.cypher_unknownTag_label(variable_tagUnknown)}'
        if self.keyword or self.synonyms is not None:
            query += "{"
            if self.keyword:
                query += f'{self.databaseInfoTag["properties"]["keyword"]}:"{self.keyword}",'
            if self.synonyms:
                query += f'{self.databaseInfoTag["properties"]["synonyms"]}:' + '["' + '","'.join(self.synonyms) + '"],'
            query = query[:-1] + "}"
        return query + ")"

    def cypher_unknownTag_merge(self, variable_tagUnknown="tag_unknown"):
        """
         Create a Cypher query to merge the node TAGUNKNOWN using his property KEYWORD
         and Set the missing properties (SYNONYMS)
         :param variable_tagUnknown: default "tag_unknown" to refer to a specific TAG
         :return: a string - Cypher Query : MERGE (tag_unknown:TAG:TAGONEGRAM:TAGUNKNOWN{keyword:"x"})
                                            SET tag_unknown.synonyms = ["x","y"]
                in the database, SYNONYMS is an array, so we add values to the array if not already in
         """

        if self.cypher_oneGramTag_merge(variable_tagUnknown) == "":
            return ""
        query = self.cypher_oneGramTag_merge(variable_tagUnknown)
        query += f'\nSET {variable_tagUnknown} {self.databaseInfoTag["label"]["unknown"]}'
        return query

    def cypher_unknownTag_whereReturn(self, variable_tagUnknown="tag_unknown"):
        """
        Create 2 arrays used for the WHERE clause and the RETURN clause of the Cypher Query from this TAGUNKNOWN
        Used to filter the database based on specifics properties values

        For this case, the properties of this object might be an array
        If a value in an array is "_" this property will be added to the return statement

        :param variable_tagUnknown: default "tag_unknown" to match a specific TAGUNKNOWN
        :return: a tuple of arrays - where properties, return properties :
            (['tag_unknown.keyword = "bob','tag_unknown.keyword = "3"]['tag_unknown.synonyms'])
        """
        cypherWhere, cypherReturn = self.cypher_oneGramTag_whereReturn(variable_tagUnknown)

        return cypherWhere, cypherReturn

class TagNGram(Tag):
    """
    An TAGNGRAM inherit from TAG
     it defines every information that refer to all the node TAGNGRAM in our database.
     It setup the properties and query to match with every subclass of the Hierarchy in the database
     A TAGNGRAM is define with a property KEYWORD in the database as well as the SYNONYMS that is a list of token
     a TAGNGRAM is composed of two ONEGRAMTAG

     It is instantiate using:
         - keyword : a String or array of string
         - synonyms : array of string
         - similarTo : array of string
         - databaseInfo: the dictionary that describe the database information (name of properties, and Label)

     It contains getter and setter for every properties, it is highly recommend to use the setter
      because it represent the data as a standard way - the way it is store in the database
     It contains a string representation
     It contains a boolean representation
     """

    def __init__(self, keyword=None, synonyms=None, similarTo=None, databaseInfo=None):
        super().__init__(keyword, synonyms, similarTo, databaseInfo)
        self._set_OneGrams(databaseInfo)

    def _get_OneGrams(self):
        return self.composedOf_oneGrams

    def _set_OneGrams(self, databaseInfo):
        charsplit= " "
        if self.keyword and not isinstance(self.keyword, list):
            self.composedOf_oneGrams = []
            for onGram in self.keyword.split(charsplit):
                self.composedOf_oneGrams.append(TagOneGram(keyword=onGram, databaseInfo=databaseInfo))
        else:
            self.composedOf_oneGrams = None

    def __bool__(self):
        return not (
            (self.keyword is None) and
            (self.synonyms is None) and
            (self.composedOf_oneGrams is None)
        )

    def __str__(self):
        return f"OBJECT: {type(self)}\n\t" \
               f"Keyword: {self.keyword}\n\t" \
               f"Synonyms: {self.synonyms}\n\t" \
               f"similarTo: {self.similarTo}\n\t" \

    def cypher_nGramTag_label(self, variable_tagNGram="ngram_tag"):
        """
        Create a Cypher query with the given variable and all label for the node TAGNGRAM
        :param variable_tagNGram: default "ngram_tag" to refer to a special node
        :return: a string - Cypher Query : ngram_tag:TAG:TAGNGRAM
        """
        return f'{self.cypher_tag_label(variable_tagNGram)}{self.databaseInfoTag["label"]["ngram"]}'

    def cypher_nGramTag_keyword(self, variable_tagNGram="ngram_tag"):
        """
         Create a Cypher query to return the specific node TAGNGRAM define by the property KEYWORD
         :param variable_tagNGram: default "ngram_tag" to refer to a special node
         :return: a string - Cypher Query : (ngram_tag:TAG:TAGNGRAM{keyword:"x"})
             OR empty string if the TAGNGRAM has no KEYWORD
         """

        if not self.keyword:
            return ""
        return f'({self.cypher_nGramTag_label(variable_tagNGram)}' + \
               "{" + f'{self.databaseInfoTag["properties"]["keyword"]}:"{self.keyword}"' + "})"

    def cypher_nGramTag_all(self, variable_tagNGram="ngram_tag"):
        """
        Create a Cypher query to return the specific node TAGNGRAM define by all the possible properties (KEYWORD, SYNONYMS)
        :param variable_tagNGram: default "ngram_tag" to refer to a specific TAGNGRAM
        :return: a string - Cypher Query : (ngram_tag:TAG:TAGNGRAM{keyword:"x", synonyms:["x","y"]})
        """
        query = f'({self.cypher_nGramTag_label(variable_tagNGram)}'
        if self.keyword or self.synonyms is not None:
            query += "{"
            if self.keyword:
                query += f'{self.databaseInfoTag["properties"]["keyword"]}:"{self.keyword}",'
            if self.synonyms:
                query += f'{self.databaseInfoTag["properties"]["synonyms"]}:' + '["' + '","'.join(self.synonyms) + '"],'
            query = query[:-1] + "}"
        return query + ")"

    def cypher_nGramTag_merge(self, variable_tagNGram="ngram_tag"):
        """
         Create a Cypher query to merge the node TAGNGRAM using his property KEYWORD
         and Set the missing properties (SYNONYMS)
         :param variable_tagNGram: default "ngram_tag" to refer to a specific TAG
         :return: a string - Cypher Query : MERGE (ngram_tag:TAG:TAGNGRAM{keyword:"x"})
                                            SET ngram_tag.synonyms = ["x","y"]
                in the database, SYNONYMS is an array, so we add values to the array if not already in
         """
        if self.cypher_tag_merge(variable_tagNGram) == "":
            return ""
        query = self.cypher_tag_merge(variable_tagNGram)
        query += f'\nSET {variable_tagNGram} {self.databaseInfoTag["label"]["ngram"]}'
        return query


    def cypher_nGramTag_whereReturn(self, variable_tagNGram="ngram_tag"):
        """
        Create 2 arrays used for the WHERE clause and the RETURN clause of the Cypher Query from this TAGNGRAM
        Used to filter the database based on specifics properties values

        For this case, the properties of this object might be an array
        If a value in an array is "_" this property will be added to the return statement

        :param variable_tagNGram: default "tag_unknown" to match a specific TAGNGRAM
        :return: a tuple of arrays - where properties, return properties :
            (['ngram_tag.keyword = "bob','ngram_tag.keyword = "3"]['ngram_tag.synonyms'])
        """
        cypherWhere, cypherReturn = self.cypher_tag_whereReturn(variable_tagNGram)

        return cypherWhere, cypherReturn



class TagProblemItem(TagNGram):
    """
    An TAGPROBLEMITEM inherit from TAGNGRAM and so from TAG
     it defines every information that refer to all the node TAGPROBLEMITEM in our database.
     A TAGPROBLEMITEM is define with a property KEYWORD in the database as well as the SYNONYMS that is a list of token
     a TAGPROBLEMITEM is composed of two ONEGRAMTAG

     It is instantiate using:
         - keyword : a String or array of string
         - synonyms : array of string
         - similarTo : array of string
         - databaseInfo: the dictionary that describe the database information (name of properties, and Label)

     It contains getter and setter for every properties, it is highly recommend to use the setter
      because it represent the data as a standard way - the way it is store in the database
     It contains a string representation
     It contains a boolean representation
     """

    def __init__(self, keyword=None, synonyms=None, similarTo=None, databaseInfo=None):
        super().__init__(keyword, synonyms, similarTo, databaseInfo)

    def __bool__(self):
        return not (
            (self.keyword is None) and
            (self.synonyms is None) and
            (self.composedOf_oneGrams is None)
        )

    def __str__(self):
        return f"OBJECT: {type(self)}\n\t" \
               f"Keyword: {self.keyword}\n\t" \
               f"Synonyms: {self.synonyms}\n\t" \
               f"similarTo: {self.similarTo}\n\t" \

    def cypher_problemItemTag_label(self, variable_tagProblemItem="problemitem_tag"):
        """
        Create a Cypher query with the given variable and all label for the node TAGPROBLEMITEM
        :param variable_tagProblemItem: default "problemitem_tag" to refer to a special node
        :return: a string - Cypher Query : problemitem_tag:TAG:TAGNGRAM:TAGPROBLEMITEM
        """
        return f'{self.cypher_nGramTag_label(variable_tagProblemItem)}{self.databaseInfoTag["label"]["problem_item"]}'

    def cypher_problemItemTag_keyword(self, variable_tagProblemItem="problemitem_tag"):
        """
         Create a Cypher query to return the specific node TAGPROBLEMITEM define by the property KEYWORD
         :param variable_tagProblemItem: default "problemitem_tag" to refer to a special node
         :return: a string - Cypher Query : (problemitem_tag:TAG:TAGNGRAM:TAGPROBLEMITEM{keyword:"x"})
             OR empty string if the TAGPROBLEMITEM has no KEYWORD
         """

        if not self.keyword:
            return ""
        return f'({self.cypher_problemItemTag_label(variable_tagProblemItem)}' + \
               "{" + f'{self.databaseInfoTag["properties"]["keyword"]}:"{self.keyword}"' + "})"

    def cypher_problemItemTag_all(self, variable_tagProblemItem="problemitem_tag"):
        """
        Create a Cypher query to return the specific node TAGPROBLEMITEM define by all the possible properties (KEYWORD, SYNONYMS)
        :param variable_tagProblemItem: default "problemitem_tag" to refer to a specific TAGPROBLEMITEM
        :return: a string - Cypher Query : (problemitem_tag:TAG:TAGNGRAM:TAGPROBLEMITEM{keyword:"x", synonyms:["x","y"]})
        """
        query = f'({self.cypher_problemItemTag_label(variable_tagProblemItem)}'
        if self.keyword or self.synonyms is not None:
            query += "{"
            if self.keyword:
                query += f'{self.databaseInfoTag["properties"]["keyword"]}:"{self.keyword}",'
            if self.synonyms:
                query += f'{self.databaseInfoTag["properties"]["synonyms"]}:' + '["' + '","'.join(self.synonyms) + '"],'
            query = query[:-1] + "}"
        return query + ")"

    def cypher_problemItemTag_merge(self, variable_tagProblemItem="problemitem_tag"):
        """
         Create a Cypher query to merge the node TAGPROBLEMITEM using his property KEYWORD
         and Set the missing properties (SYNONYMS)
         :param variable_tagProblemItem: default "problemitem_tag" to refer to a specific TAG
         :return: a string - Cypher Query : MERGE (problemitem_tag:TAG:TAGNGRAM:TAGPROBLEMITEM{keyword:"x"})
                                            SET problemitem_tag.synonyms = ["x","y"]
                in the database, SYNONYMS is an array, so we add values to the array if not already in
         """
        if self.cypher_tag_merge(variable_tagProblemItem) == "":
            return ""
        query = self.cypher_nGramTag_merge(variable_tagProblemItem)
        query += f'\nSET {variable_tagProblemItem} {self.databaseInfoTag["label"]["problem_item"]}'
        return query

    def cypher_problemItemTag_whereReturn(self, variable_tagProblemItem="problemitem_tag"):
        """
         Create 2 arrays used for the WHERE clause and the RETURN clause of the Cypher Query from this TAGPROBLEMITEM
         Used to filter the database based on specifics properties values

         For this case, the properties of this object might be an array
         If a value in an array is "_" this property will be added to the return statement

         :param variable_tagProblemItem: default "problemitem_tag" to match a specific TAGPROBLEMITEM
         :return: a tuple of arrays - where properties, return properties :
             (['problemitem_tag.keyword = "bob','problemitem_tag.keyword = "3"]['problemitem_tag.synonyms'])
         """
        cypherWhere, cypherReturn = self.cypher_nGramTag_whereReturn(variable_tagProblemItem)

        return cypherWhere, cypherReturn


class TagSolutionItem(TagNGram):
    """
    An TAGSOLUTIONITEM inherit from TAGNGRAM and so from TAG
     it defines every information that refer to all the node TAGSOLUTIONITEM in our database.
     A TAGSOLUTIONITEM is define with a property KEYWORD in the database as well as the SYNONYMS that is a list of token
     a TAGSOLUTIONITEM is composed of two ONEGRAMTAG

     It is instantiate using:
         - keyword : a String or array of string
         - synonyms : array of string
         - similarTo : array of string
         - databaseInfo: the dictionary that describe the database information (name of properties, and Label)

     It contains getter and setter for every properties, it is highly recommend to use the setter
      because it represent the data as a standard way - the way it is store in the database
     It contains a string representation
     It contains a boolean representation
     """

    def __init__(self, keyword=None, synonyms=None, similarTo=None, databaseInfo=None):
        super().__init__(keyword, synonyms, similarTo, databaseInfo)

    def __bool__(self):
        return not (
            (self.keyword is None) and
            (self.synonyms is None) and
            (self.composedOf_oneGrams is None)
        )

    def __str__(self):
        return f"OBJECT: {type(self)}\n\t" \
               f"Keyword: {self.keyword}\n\t" \
               f"Synonyms: {self.synonyms}\n\t" \
               f"similarTo: {self.similarTo}\n\t" \

    def cypher_solutionItemTag_label(self, variable_tagSolutionItem="solutionitem_tag"):
        """
        Create a Cypher query with the given variable and all label for the node TAGSOLUTIONITEM
        :param variable_tagSolutionItem: default "solutionitem_tag" to refer to a special node
        :return: a string - Cypher Query : solutionitem_tag:TAG:TAGNGRAM::TAGSOLUTIONITEM
        """
        return f'{self.cypher_nGramTag_label(variable_tagSolutionItem)}{self.databaseInfoTag["label"]["solution_item"]}'

    def cypher_solutionItemTag_keyword(self, variable_tagSolutionItem="solutionitem_tag"):
        """
         Create a Cypher query to return the specific node TAGSOLUTIONITEM define by the property KEYWORD
         :param variable_tagSolutionItem: default "solutionitem_tag" to refer to a special node
         :return: a string - Cypher Query : (solutionitem_tag:TAG:TAGNGRAM:TAGSOLUTIONITEM{keyword:"x"})
             OR empty string if the TAGSOLUTIONITEM has no KEYWORD
         """

        if not self.keyword:
            return ""
        return f'({self.cypher_solutionItemTag_label(variable_tagSolutionItem)}' + \
               "{" + f'{self.databaseInfoTag["properties"]["keyword"]}:"{self.keyword}"' + "})"

    def cypher_solutionItemTag_all(self, variable_tagSolutionItem="solutionitem_tag"):
        """
        Create a Cypher query to return the specific node TAGSOLUTIONITEM define by all the possible properties (KEYWORD, SYNONYMS)
        :param variable_tagSolutionItem: default "solutionitem_tag" to refer to a specific TAGSOLUTIONITEM
        :return: a string - Cypher Query : (solutionitem_tag:TAG:TAGNGRAM:TAGSOLUTIONITEM{keyword:"x", synonyms:["x","y"]})
        """
        query = f'({self.cypher_solutionItemTag_label(variable_tagSolutionItem)}'
        if self.keyword or self.synonyms is not None:
            query += "{"
            if self.keyword:
                query += f'{self.databaseInfoTag["properties"]["keyword"]}:"{self.keyword}",'
            if self.synonyms:
                query += f'{self.databaseInfoTag["properties"]["synonyms"]}:' + '["' + '","'.join(self.synonyms) + '"],'
            query = query[:-1] + "}"
        return query + ")"

    def cypher_solutionItemTag_merge(self, variable_tagSolutionItem="solutionitem_tag"):
        """
         Create a Cypher query to merge the node TAGSOLUTIONITEM using his property KEYWORD
         and Set the missing properties (SYNONYMS)
         :param variable_tagSolutionItem: default "solutionitem_tag" to refer to a specific TAG
         :return: a string - Cypher Query : MERGE (solutionitem_tag:TAG:TAGNGRAM:TAGSOLUTIONITEM{keyword:"x"})
                                            SET solutionitem_tag.synonyms = ["x","y"]
                in the database, SYNONYMS is an array, so we add values to the array if not already in
         """
        if self.cypher_tag_merge(variable_tagSolutionItem) == "":
            return ""
        query = self.cypher_nGramTag_merge(variable_tagSolutionItem)
        query += f'\nSET {variable_tagSolutionItem} {self.databaseInfoTag["label"]["solution_item"]}'
        return query

    def cypher_solutionItemTag_whereReturn(self, variable_tagSolutionItem="solutionitem_tag"):
        """
         Create 2 arrays used for the WHERE clause and the RETURN clause of the Cypher Query from this TAGSOLUTIONITEM
         Used to filter the database based on specifics properties values

         For this case, the properties of this object might be an array
         If a value in an array is "_" this property will be added to the return statement

         :param variable_tagSolutionItem: default "solutionitem_tag" to match a specific TAGSOLUTIONITEM
         :return: a tuple of arrays - where properties, return properties :
             (['solutionitem_tag.keyword = "bob','solutionitem_tag.keyword = "3"]['solutionitem_tag.synonyms'])
         """
        cypherWhere, cypherReturn = self.cypher_nGramTag_whereReturn(variable_tagSolutionItem)

        return cypherWhere, cypherReturn
