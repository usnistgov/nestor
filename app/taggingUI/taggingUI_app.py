import sys
from PyQt5.QtCore import QCoreApplication, Qt, QSize
from PyQt5 import QtGui
import PyQt5.QtWidgets as Qw

from app.taggingUI.taggingUI_skeleton import Ui_MainWindow_taggingTool


class MyTaggingToolWindow(Qw.QMainWindow, Ui_MainWindow_taggingTool):

    def __init__(self):
        Qw.QMainWindow.__init__(self)
        self.setupUi(self)
        # self.dataframe_OriginalCSV = None
        # self.scores = None
        # self.alias_lookup = None
        #
        # self.vocab_limit = 1000
        #
        # value_SimilarityThreshold = 10
        # self.horizontalSlider_1gram_FindingThreshold.setValue()



if __name__ == "__main__":
    app = Qw.QApplication(sys.argv)
    window = MyTaggingToolWindow()
    window.show()
    sys.exit(app.exec_())