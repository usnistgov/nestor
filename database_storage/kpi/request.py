
class Request:

    def __init__(self, variable, property):

        self._set_variable(variable)
        self._set_property(property)


    def _get_variable(self):
        return self.variable

    def _set_variable(self, variable):
        self.variable = variable

    def _get_property(self):
        return self.property

    def _set_property(self, property):
        self.property = property

    def cypher_query(self):
        return f'{self.variable}.{self.property}'