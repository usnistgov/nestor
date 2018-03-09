import sys
from PyQt5.QtCore import QCoreApplication, Qt, QSize
from PyQt5 import QtGui
import PyQt5.QtWidgets as Qw

class QTableWidget_token(Qw.QTableWidget):

    def __init__(self):
        Qw.QTableWidget.__init__(self)
        #TODO set the resiz of the collumn and line to false
        #TODO set the original collunm size based on the header size

    def set_dataframe(self, dataframe):
        """
        set the dataframe
        :param dataframe:
        :return:
        """
        #TODO THURSTON why test_app->mywindow->setDataframe Do we need all the mask and stuff ?
        self.dataframe=dataframe

    def printDataframe_tableView(self, vocab_limit):
        """
        print the dataframe into the table view
        :return:
        """
        if self.dataframe is not None:
            temp_df = self.dataframe.reset_index()
            temp_df.fillna('', inplace=True)
            nrows, ncols = temp_df.shape
            self.setColumnCount(ncols - 1)  # ignore score column
            self.setRowCount(min([nrows, vocab_limit]))

            for i in range(self.rowCount()):
                for j in range(ncols - 1):  # ignore score column
                    self.setItem(i, j, Qw.QTableWidgetItem(str(temp_df.iat[i, j])))

            self.resizeColumnsToContents()
            self.resizeRowsToContents()
            self.setHorizontalHeaderLabels(temp_df.columns.tolist()[:-1])  # ignore score column
            self.setSelectionBehavior(Qw.QTableWidget.SelectRows)

class QButtonGroup_similarityPattern(Qw.QButtonGroup):

    def __init__(self, layout):
        Qw.QButtonGroup.__init__(self)
        self.setExclusive(False)
        self.layout = layout
        self.spacer=None

    def set_checkBoxes(self, token_list, autoMatch_score):
        """
        create and print the checkboxes
        :param token_list:
        :param autoMatch_score:
        :return:
        """
        self.clean_checkboxes()

        for token, score in token_list:
            btn = Qw.QCheckBox(token)
            if score >= autoMatch_score:
                btn.toggle()
            self.addButton(btn)
            self.layout.addWidget(btn)

        self.spacer = Qw.QSpacerItem(20, 40, Qw.QSizePolicy.Minimum, Qw.QSizePolicy.Expanding)
        self.layout.addSpacerItem(self.spacer)

    def clean_checkboxes(self):
        """
        remove all from the layout
        :return:
        """
        for widg in self.buttons():
            self.removeButton(widg)
            self.layout.removeWidget(widg)
            widg.deleteLater()
        self.layout.removeItem(self.spacer)

