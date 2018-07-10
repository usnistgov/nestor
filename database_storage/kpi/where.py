
class Where:

    def __init__(self, variable, property=None, operator=None, value=None, edge=None, variable2=None, edgeLabel=None ):
        self._set_variable(variable)
        self._set_property(property)
        self._set_operator(operator)
        self._set_value(value)

        self._set_edgeLabel(edgeLabel)
        self._set_edge(edge)
        self._set_variable2(variable2)



    def _get_variable(self):
        return self.variable

    def _set_variable(self, variable):
        self.variable = variable

    def _get_variable2(self):
        return self.variable2

    def _set_variable2(self, variable2):
        self.variable2 = variable2

    def _get_property(self):
        return self.property

    def _set_property(self, property):
        self.property = property

    def _get_operator(self):
        return self.operator

    def _set_operator(self, operator):
        self.operator = operator

    def _get_value(self):
        return self.value

    def _set_value(self, value):
        self.value = value

    def _get_edge(self):
        return self.edge

    def _set_edge(self, edge):
        if self.edgeLabel:
            edge = self.edgeLabel.join(edge.split(" "))
        self.edge = edge

    def _get_edgeLabel(self):
        return self.edgeLabel

    def _set_edgeLabel(self, edgeLabel):
        self.edgeLabel = edgeLabel


    def cypher_query(self):
        if self.variable and self.property and self.operator and self.value:
            return f'{self.variable}.{self.property} {self.operator} "{self.value}"'
        elif self.variable and self.edge and self.variable2:
            return f'({self.variable}){self.edge}({self.variable2})'
