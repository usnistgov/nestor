import sys
from PyQt5.QtCore import QCoreApplication, Qt, QSize
from PyQt5 import QtGui
import PyQt5.QtWidgets as Qw

class QTableWidget_token(Qw.QTableWidget):

    def __init__(self):
        Qw.QTableWidget.__init__(self)
        #self.setFocus()

    def set_dataframe(self, dataframe):
        self.dataframe=dataframe

    def print_tableData(self):
        pass