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

from nestor.store_data.helper import standardizeString

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
        self.label = self.databaseInfoTag['label']['tag']


        self._set_keyword(keyword)
        self._set_synonyms(synonyms)
        self._set_similarTo(similarTo, databaseInfo)


    def _get_keyword(self):
        return self.keyword

    def _set_keyword(self, keyword):
        if isinstance(keyword, str):
            self.keyword = standardizeString(keyword).lower()
        else:
            self.keyword = None

    def _get_synonyms(self):
        return self.synonyms

    def _set_synonyms(self, synonyms):
        if isinstance(synonyms, str):
            self.synonyms = [standardizeString(synonyms).lower()]
        elif isinstance(synonyms, list):
            self.synonyms = [standardizeString(s).lower() for s in synonyms]
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
        return  f'object  =  {type(self)}\n'\
                f'\tlabel  =  {self.label}\n'\
                f'\tkeyword  =  {self.keyword}\n'\
                f'\tsynonyms  =  {self.synonyms}\n'\
                f'\tsimilarTo  =  {self.similarTo}'\

    def cypher_tag_keyword(self, variable_tag="tag"):
        """
         Create a Cypher query to return the specific node TAG define by the property KEYWORD
         :param variable_tag: default "tag" to refer to a special node
         :return: a string - Cypher Query : (tag:TAG{keyword:"x"})
             OR empty string if the TAG has no KEYWORD
         """
        if not self.keyword:
            return ""
        return f'({variable_tag}{self.label}' + \
               "{" + f'{self.databaseInfoTag["properties"]["keyword"]}:\'{self.keyword}\'' + "})"

    def cypher_tag_all(self, variable_tag="tag"):
        """
        Create a Cypher query to return the specific node TAG define by all the possible properties (KEYWORD, SYNONYMS)
        :param variable_tag: default "tag" to refer to a specific TAG
        :return: a string - Cypher Query : (tag:TAG{keyword:"x", synonyms:["x","y"]})
        """
        query = f'({variable_tag}{self.label}'
        if self.keyword or self.synonyms is not None:
            query += "{"
            if self.keyword is not None:
                query += f'{self.databaseInfoTag["properties"]["keyword"]}:\'{self.keyword}\','
            if self.synonyms is not None:
                query += f'{self.databaseInfoTag["properties"]["synonyms"]}:' + '[\'' + '\',\''.join(self.synonyms) + '\'],'
            query = query[:-1] + "}"
        return query + ")"


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
        self.label +=self.databaseInfoTag['label']['onegram']

    def __bool__(self):
        return not (
            (self.keyword is None) and
            (self.synonyms is None)
        )

    def __str__(self):
        return f'{super().__str__()}'

    def cypher_oneGramTag_keyword(self, variable_tagOnGram="onegram_tag"):
        """
         Create a Cypher query to return the specific node TAGONEGRAM define by the property KEYWORD
         :param variable_tagOnGram: default "onegram_tag" to refer to a special node
         :return: a string - Cypher Query : (onegram_tag:TAG:TAGONEGRAM{keyword:"x"})
             OR empty string if the TAGONEGRAM has no KEYWORD
         """

        if not self.keyword:
            return ""
        return f'({variable_tagOnGram}{self.label}' + \
               "{" + f'{self.databaseInfoTag["properties"]["keyword"]}:\'{self.keyword}\'' + "})"

    def cypher_oneGramTag_all(self, variable_tagOnGram="onegram_tag"):
        """
        Create a Cypher query to return the specific node TAGONEGRAM define by all the possible properties (KEYWORD, SYNONYMS)
        :param variable_tagOnGram: default "onegram_tag" to refer to a specific TAGONEGRAM
        :return: a string - Cypher Query : (onegram_tag:TAG:TAGONEGRAM{keyword:"x", synonyms:["x","y"]})
        """

        query = f'({variable_tagOnGram}{self.label}'
        if self.keyword or self.synonyms is not None:
            query += "{"
            if self.keyword:
                query += f'{self.databaseInfoTag["properties"]["keyword"]}:\'{self.keyword}\','
            if self.synonyms:
                query += f'{self.databaseInfoTag["properties"]["synonyms"]}:' + '[\'' + '\',\''.join(self.synonyms) + '\'],'
            query = query[:-1] + "}"
        return query + ")"


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
        self.label += self.databaseInfoTag['label']['item']

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
        return f'{super().__str__()}\n'\
               f'\tchildren  =  {self.children}'

    def cypher_itemTag_keyword(self, variable_tagItem="tag_item"):
        """
         Create a Cypher query to return the specific node TAGITEM define by the property KEYWORD
         :param variable_tagItem: default "tag_item" to refer to a special node
         :return: a string - Cypher Query : (tag_item:TAG:TAGONEGRAM:TAGITEM{keyword:"x"})
             OR empty string if the TAGITEM has no KEYWORD
         """

        if not self.keyword:
            return ""
        return f'({variable_tagItem}{self.label}' + \
               "{" + f'{self.databaseInfoTag["properties"]["keyword"]}:\'{self.keyword}\'' + "})"

    def cypher_itemTag_all(self, variable_tagItem="tag_item"):
        """
        Create a Cypher query to return the specific node TAGITEM define by all the possible properties (KEYWORD, SYNONYMS)
        :param variable_tagItem: default "tag_item" to refer to a specific TAGITEM
        :return: a string - Cypher Query : (tag_item:TAG:TAGONEGRAM:TAGITEM{keyword:"x", synonyms:["x","y"]})
        """
        query = f'({variable_tagItem}{self.label}'
        if self.keyword or self.synonyms is not None:
            query += "{"
            if self.keyword:
                query += f'{self.databaseInfoTag["properties"]["keyword"]}:\'{self.keyword}\','
            if self.synonyms:
                query += f'{self.databaseInfoTag["properties"]["synonyms"]}:' + '[\'' + '\',\''.join(self.synonyms) + '\'],'
            query = query[:-1] + "}"
        return query + ")"


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
        self.label += self.databaseInfoTag['label']['problem']

    def __bool__(self):
        return not (
            (self.keyword is None) and
            (self.synonyms is None)
        )

    def __str__(self):
        return f'{super().__str__()}'

    def cypher_problemTag_keyword(self, variable_tagProblem="tag_problem"):
        """
         Create a Cypher query to return the specific node TAGPROBLEM define by the property KEYWORD
         :param variable_tagProblem: default "tag_problem" to refer to a special node
         :return: a string - Cypher Query : (tag_problem:TAG:TAGONEGRAM:TAGPROBLEM{keyword:"x"})
             OR empty string if the TAGPROBLEM has no KEYWORD
         """

        if not self.keyword:
            return ""
        return f'({variable_tagProblem}{self.label}' + \
               "{" + f'{self.databaseInfoTag["properties"]["keyword"]}:\'{self.keyword}\'' + "})"

    def cypher_problemTag_all(self, variable_tagProblem="tag_problem"):
        """
        Create a Cypher query to return the specific node TAGPROBLEM define by all the possible properties (KEYWORD, SYNONYMS)
        :param variable_tagProblem: default "tag_problem" to refer to a specific TAGPROBLEM
        :return: a string - Cypher Query : (tag_problem:TAG:TAGONEGRAM:TAGPROBLEM{keyword:"x", synonyms:["x","y"]})
        """
        query = f'({variable_tagProblem}{self.label}'
        if self.keyword or self.synonyms is not None:
            query += "{"
            if self.keyword:
                query += f'{self.databaseInfoTag["properties"]["keyword"]}:\'{self.keyword}\','
            if self.synonyms:
                query += f'{self.databaseInfoTag["properties"]["synonyms"]}:' + '[\'' + '\',\''.join(self.synonyms) + '\'],'
            query = query[:-1] + "}"
        return query + ")"


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
        self.label += self.databaseInfoTag['label']['solution']

    def __bool__(self):
        return not (
            (self.keyword is None) and
            (self.synonyms is None)
        )

    def __str__(self):
        return f'{super().__str__()}'

    def cypher_solutionTag_keyword(self, variable_tagSolution="tag_solution"):
        """
         Create a Cypher query to return the specific node TAGSOLUTION define by the property KEYWORD
         :param variable_tagSolution: default "tag_solution" to refer to a special node
         :return: a string - Cypher Query : (tag_solution:TAG:TAGONEGRAM:TAGSOLUTION{keyword:"x"})
             OR empty string if the TAGSOLUTION has no KEYWORD
         """

        if not self.keyword:
            return ""
        return f'({variable_tagSolution}{self.label}' + \
               "{" + f'{self.databaseInfoTag["properties"]["keyword"]}:\'{self.keyword}\'' + "})"

    def cypher_solutionTag_all(self, variable_tagSolution="tag_solution"):
        """
        Create a Cypher query to return the specific node TAGSOLUTION define by all the possible properties (KEYWORD, SYNONYMS)
        :param variable_tagSolution: default "tag_solution" to refer to a specific TAGSOLUTION
        :return: a string - Cypher Query : (tag_solution:TAG:TAGONEGRAM:TAGSOLUTION{keyword:"x", synonyms:["x","y"]})
        """
        query = f'({variable_tagSolution}{self.label}'
        if self.keyword or self.synonyms is not None:
            query += "{"
            if self.keyword:
                query += f'{self.databaseInfoTag["properties"]["keyword"]}:\'{self.keyword}\','
            if self.synonyms:
                query += f'{self.databaseInfoTag["properties"]["synonyms"]}:' + '[\'' + '\',\''.join(self.synonyms) + '\'],'
            query = query[:-1] + "}"
        return query + ")"


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
        self.label += self.databaseInfoTag['label']['unknown']

    def __bool__(self):
        return not (
            (self.keyword is None) and
            (self.synonyms is None)
        )

    def __str__(self):
        return f'{super().__str__()}'

    def cypher_unknownTag_keyword(self, variable_tagUnknown="tag_unknown"):
        """
         Create a Cypher query to return the specific node TAGUNKNOWN define by the property KEYWORD
         :param variable_tagUnknown: default "tag_unknown" to refer to a special node
         :return: a string - Cypher Query : (tag_unknown:TAG:TAGONEGRAM:TAGUNKNOWN{keyword:"x"})
             OR empty string if the TAGUNKNOWN has no KEYWORD
         """

        if not self.keyword:
            return ""
        return f'({variable_tagUnknown}{self.label}'+ \
               "{" + f'{self.databaseInfoTag["properties"]["keyword"]}:\'{self.keyword}\'' + "})"

    def cypher_unknownTag_all(self, variable_tagUnknown="tag_unknown"):
        """
        Create a Cypher query to return the specific node TAGUNKNOWN define by all the possible properties (KEYWORD, SYNONYMS)
        :param variable_tagUnknown: default "tag_unknown" to refer to a specific TAGUNKNOWN
        :return: a string - Cypher Query : (tag_unknown:TAG:TAGONEGRAM:TAGUNKNOWN{keyword:"x", synonyms:["x","y"]})
        """
        query = f'({variable_tagUnknown}{self.label}'
        if self.keyword or self.synonyms is not None:
            query += "{"
            if self.keyword:
                query += f'{self.databaseInfoTag["properties"]["keyword"]}:\'{self.keyword}\','
            if self.synonyms:
                query += f'{self.databaseInfoTag["properties"]["synonyms"]}:' + '[\'' + '\',\''.join(self.synonyms) + '\'],'
            query = query[:-1] + "}"
        return query + ")"


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
        self.label += self.databaseInfoTag['label']['ngram']
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
        str = f'{super().__str__()}\n'\
                f'\tcomposedOf  =  \n'
        if self.composedOf_oneGrams:
            for tag in self.composedOf_oneGrams:
                str += f'\t{tag.__str__()}\n'
        else:
            str += "\tNO COMPOSEDOF"
        return str

    def cypher_nGramTag_keyword(self, variable_tagNGram="ngram_tag"):
        """
         Create a Cypher query to return the specific node TAGNGRAM define by the property KEYWORD
         :param variable_tagNGram: default "ngram_tag" to refer to a special node
         :return: a string - Cypher Query : (ngram_tag:TAG:TAGNGRAM{keyword:"x"})
             OR empty string if the TAGNGRAM has no KEYWORD
         """

        if not self.keyword:
            return ""
        return f'({variable_tagNGram}{self.label}' + \
               "{" + f'{self.databaseInfoTag["properties"]["keyword"]}:\'{self.keyword}\'' + "})"

    def cypher_nGramTag_all(self, variable_tagNGram="ngram_tag"):
        """
        Create a Cypher query to return the specific node TAGNGRAM define by all the possible properties (KEYWORD, SYNONYMS)
        :param variable_tagNGram: default "ngram_tag" to refer to a specific TAGNGRAM
        :return: a string - Cypher Query : (ngram_tag:TAG:TAGNGRAM{keyword:"x", synonyms:["x","y"]})
        """
        query = f'({variable_tagNGram}{self.label}'
        if self.keyword or self.synonyms is not None:
            query += "{"
            if self.keyword:
                query += f'{self.databaseInfoTag["properties"]["keyword"]}:\'{self.keyword}\','
            if self.synonyms:
                query += f'{self.databaseInfoTag["properties"]["synonyms"]}:' + '[\'' + '\',\''.join(self.synonyms) + '\'],'
            query = query[:-1] + "}"
        return query + ")"


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
        self.label += self.databaseInfoTag['label']['problem_item']

    def __bool__(self):
        return not (
            (self.keyword is None) and
            (self.synonyms is None) and
            (self.composedOf_oneGrams is None)
        )

    def __str__(self):
        return f'{super().__str__()}'

    def cypher_problemItemTag_keyword(self, variable_tagProblemItem="problemitem_tag"):
        """
         Create a Cypher query to return the specific node TAGPROBLEMITEM define by the property KEYWORD
         :param variable_tagProblemItem: default "problemitem_tag" to refer to a special node
         :return: a string - Cypher Query : (problemitem_tag:TAG:TAGNGRAM:TAGPROBLEMITEM{keyword:"x"})
             OR empty string if the TAGPROBLEMITEM has no KEYWORD
         """

        if not self.keyword:
            return ""
        return f'({variable_tagProblemItem}{self.label}' + \
               "{" + f'{self.databaseInfoTag["properties"]["keyword"]}:\'{self.keyword}\'' + "})"

    def cypher_problemItemTag_all(self, variable_tagProblemItem="problemitem_tag"):
        """
        Create a Cypher query to return the specific node TAGPROBLEMITEM define by all the possible properties (KEYWORD, SYNONYMS)
        :param variable_tagProblemItem: default "problemitem_tag" to refer to a specific TAGPROBLEMITEM
        :return: a string - Cypher Query : (problemitem_tag:TAG:TAGNGRAM:TAGPROBLEMITEM{keyword:"x", synonyms:["x","y"]})
        """
        query =f'({variable_tagProblemItem}{self.label}'
        if self.keyword or self.synonyms is not None:
            query += "{"
            if self.keyword:
                query += f'{self.databaseInfoTag["properties"]["keyword"]}:\'{self.keyword}\','
            if self.synonyms:
                query += f'{self.databaseInfoTag["properties"]["synonyms"]}:' + '[\'' + '\',\''.join(self.synonyms) + '\'],'
            query = query[:-1] + "}"
        return query + ")"



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
        self.label += self.databaseInfoTag['label']['solution_item']

    def __bool__(self):
        return not (
            (self.keyword is None) and
            (self.synonyms is None) and
            (self.composedOf_oneGrams is None)
        )

    def __str__(self):
        return f'{super().__str__()}'

    def cypher_solutionItemTag_keyword(self, variable_tagSolutionItem="solutionitem_tag"):
        """
         Create a Cypher query to return the specific node TAGSOLUTIONITEM define by the property KEYWORD
         :param variable_tagSolutionItem: default "solutionitem_tag" to refer to a special node
         :return: a string - Cypher Query : (solutionitem_tag:TAG:TAGNGRAM:TAGSOLUTIONITEM{keyword:"x"})
             OR empty string if the TAGSOLUTIONITEM has no KEYWORD
         """

        if not self.keyword:
            return ""
        return f'({variable_tagSolutionItem}{self.label}' + \
               "{" + f'{self.databaseInfoTag["properties"]["keyword"]}:"{self.keyword}"' + "})"

    def cypher_solutionItemTag_all(self, variable_tagSolutionItem="solutionitem_tag"):
        """
        Create a Cypher query to return the specific node TAGSOLUTIONITEM define by all the possible properties (KEYWORD, SYNONYMS)
        :param variable_tagSolutionItem: default "solutionitem_tag" to refer to a specific TAGSOLUTIONITEM
        :return: a string - Cypher Query : (solutionitem_tag:TAG:TAGNGRAM:TAGSOLUTIONITEM{keyword:"x", synonyms:["x","y"]})
        """
        query = f'({variable_tagSolutionItem}{self.label}'
        if self.keyword or self.synonyms is not None:
            query += "{"
            if self.keyword:
                query += f'{self.databaseInfoTag["properties"]["keyword"]}:\'{self.keyword}\','
            if self.synonyms:
                query += f'{self.databaseInfoTag["properties"]["synonyms"]}:' + '[\'' + '\',\''.join(self.synonyms) + '\'],'
            query = query[:-1] + "}"
        return query + ")"


class TagOther(Tag):
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
        self.label += self.databaseInfoTag['label']['other']

    def __bool__(self):
        return not (
            (self.keyword is None) and
            (self.synonyms is None)
        )

    def __str__(self):
        return f'{super().__str__()}'

    def cypher_otherTag_keyword(self, variable_tagOther="other_tag"):
        """
         Create a Cypher query to return the specific node TAGONEGRAM define by the property KEYWORD
         :param variable_tagOnGram: default "onegram_tag" to refer to a special node
         :return: a string - Cypher Query : (onegram_tag:TAG:TAGONEGRAM{keyword:"x"})
             OR empty string if the TAGONEGRAM has no KEYWORD
         """

        if not self.keyword:
            return ""
        return f'({variable_tagOther}{self.label}' + \
               "{" + f'{self.databaseInfoTag["properties"]["keyword"]}:\'{self.keyword}\'' + "})"

    def cypher_otherTag_all(self, variable_tagOther="other_tag"):
        """
        Create a Cypher query to return the specific node TAGONEGRAM define by all the possible properties (KEYWORD, SYNONYMS)
        :param variable_tagOnGram: default "onegram_tag" to refer to a specific TAGONEGRAM
        :return: a string - Cypher Query : (onegram_tag:TAG:TAGONEGRAM{keyword:"x", synonyms:["x","y"]})
        """

        query = f'({variable_tagOther}{self.label}'
        if self.keyword or self.synonyms is not None:
            query += "{"
            if self.keyword:
                query += f'{self.databaseInfoTag["properties"]["keyword"]}:\'{self.keyword}\','
            if self.synonyms:
                query += f'{self.databaseInfoTag["properties"]["synonyms"]}:' + '[\'' + '\',\''.join(self.synonyms) + '\'],'
            query = query[:-1] + "}"
        return query + ")"


class TagNA(TagOther):
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
        self.label += self.databaseInfoTag['label']['na']

    def __bool__(self):
        return not (
            (self.keyword is None) and
            (self.synonyms is None)
        )

    def __str__(self):
        return f'{super().__str__()}'

    def cypher_naTag_keyword(self, variable_tagNA="na_tag"):
        """
         Create a Cypher query to return the specific node TAGSOLUTIONITEM define by the property KEYWORD
         :param variable_tagSolutionItem: default "solutionitem_tag" to refer to a special node
         :return: a string - Cypher Query : (solutionitem_tag:TAG:TAGNGRAM:TAGSOLUTIONITEM{keyword:"x"})
             OR empty string if the TAGSOLUTIONITEM has no KEYWORD
         """

        if not self.keyword:
            return ""
        return f'({variable_tagNA}{self.label}' + \
               "{" + f'{self.databaseInfoTag["properties"]["keyword"]}:"{self.keyword}"' + "})"

    def cypher_naTag_all(self, variable_tagNA="na_tag"):
        """
        Create a Cypher query to return the specific node TAGSOLUTIONITEM define by all the possible properties (KEYWORD, SYNONYMS)
        :param variable_tagSolutionItem: default "solutionitem_tag" to refer to a specific TAGSOLUTIONITEM
        :return: a string - Cypher Query : (solutionitem_tag:TAG:TAGNGRAM:TAGSOLUTIONITEM{keyword:"x", synonyms:["x","y"]})
        """
        query = f'({variable_tagNA}{self.label}'
        if self.keyword or self.synonyms is not None:
            query += "{"
            if self.keyword:
                query += f'{self.databaseInfoTag["properties"]["keyword"]}:\'{self.keyword}\','
            if self.synonyms:
                query += f'{self.databaseInfoTag["properties"]["synonyms"]}:' + '[\'' + '\',\''.join(self.synonyms) + '\'],'
            query = query[:-1] + "}"
        return query + ")"


class TagStopWord(TagOther):
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
        self.label += self.databaseInfoTag['label']['stopword']

    def __bool__(self):
        return not (
            (self.keyword is None) and
            (self.synonyms is None)
        )

    def __str__(self):
        return f'{super().__str__()}'

    def cypher_stopWordTag_keyword(self, variable_tagStopWord="stopword_tag"):
        """
         Create a Cypher query to return the specific node TAGSOLUTIONITEM define by the property KEYWORD
         :param variable_tagSolutionItem: default "solutionitem_tag" to refer to a special node
         :return: a string - Cypher Query : (solutionitem_tag:TAG:TAGNGRAM:TAGSOLUTIONITEM{keyword:"x"})
             OR empty string if the TAGSOLUTIONITEM has no KEYWORD
         """

        if not self.keyword:
            return ""
        return f'({variable_tagStopWord}{self.label}' + \
               "{" + f'{self.databaseInfoTag["properties"]["keyword"]}:"{self.keyword}"' + "})"

    def cypher_stopWordTag_all(self, variable_tagStopWord="stopword_tag"):
        """
        Create a Cypher query to return the specific node TAGSOLUTIONITEM define by all the possible properties (KEYWORD, SYNONYMS)
        :param variable_tagSolutionItem: default "solutionitem_tag" to refer to a specific TAGSOLUTIONITEM
        :return: a string - Cypher Query : (solutionitem_tag:TAG:TAGNGRAM:TAGSOLUTIONITEM{keyword:"x", synonyms:["x","y"]})
        """
        query = f'({variable_tagStopWord}{self.label}'
        if self.keyword or self.synonyms is not None:
            query += "{"
            if self.keyword:
                query += f'{self.databaseInfoTag["properties"]["keyword"]}:\'{self.keyword}\','
            if self.synonyms:
                query += f'{self.databaseInfoTag["properties"]["synonyms"]}:' + '[\'' + '\',\''.join(self.synonyms) + '\'],'
            query = query[:-1] + "}"
        return query + ")"
