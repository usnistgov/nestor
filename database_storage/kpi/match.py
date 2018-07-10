
class Match:

    def __init__(self, variable, label):

        self._set_variable(variable)
        self._set_label(label)

    def _get_variable(self):
        return self.variable

    def _set_variable(self, variable):
        self.variable = variable

    def _get_label(self):
        return self.label

    def _set_label(self, label):
        self.label = label


    def cypher_query(self):
        return f'({self.variable}{self.label})'