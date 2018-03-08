import sys
from PyQt5.QtCore import QCoreApplication, Qt, QSize
from PyQt5 import QtGui
import PyQt5.QtWidgets as Qw

from app.taggingUI.helper_objects import QTableWidget_token
from app.taggingUI.taggingUI_skeleton import Ui_MainWindow_taggingTool


class MyTaggingToolWindow(Qw.QMainWindow, Ui_MainWindow_taggingTool):

    def __init__(self, config):
        Qw.QMainWindow.__init__(self)
        self.setupUi(self)

        self.tableWidget_Ngram_TagContainer.__class__ = QTableWidget_token
        self.tableWidget_1gram_TagContainer.__class__ = QTableWidget_token

        self.numberToken_show = config['value']['numberToken_show']

        # self.dataframe_OriginalCSV = None
        # self.scores = None
        # self.alias_lookup = None
        #

        self.similarityMatrix_threshold = config['value']['similarityMatrix_threshold']

        self.horizontalSlider_1gram_FindingThreshold.setValue(self.similarityMatrix_threshold)
        self.horizontalSlider_Ngram_FindingThreshold.setValue(self.similarityMatrix_threshold)



if __name__ == "__main__":
    app = Qw.QApplication(sys.argv)
    window = MyTaggingToolWindow()
    window.show()
    sys.exit(app.exec_())