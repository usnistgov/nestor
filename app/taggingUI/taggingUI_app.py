import sys
from PyQt5.QtCore import QCoreApplication, Qt, QSize
from PyQt5 import QtGui
import PyQt5.QtWidgets as Qw
from fuzzywuzzy import process as zz


from app.taggingUI import helper_objects as myObjects
from app.taggingUI.taggingUI_skeleton import Ui_MainWindow_taggingTool


class MyTaggingToolWindow(Qw.QMainWindow, Ui_MainWindow_taggingTool):

    def __init__(self):
        Qw.QMainWindow.__init__(self)
        self.setupUi(self)

        self.classificationDictionary_1Gram = {
            'S': self.radioButton_1gram_SolutionEditor,
            'P': self.radioButton_1gram_ProblemEditor,
            'I': self.radioButton_1gram_ItemEditor,
            'X': self.radioButton_1gram_StopWordEditor,
            'U': self.radioButton_1gram_UnknownEditor,
            '' : self.radioButton_1gram_NotClassifiedEditor
        }
        self.dataframe_1Gram = None
        self.dataframe_NGram = None
        #self.alias_lookup = None

        self.buttonGroup_1Gram_similarityPattern = myObjects.QButtonGroup_similarityPattern(self.verticalLayout_1gram_SimilarityPattern)
        self.tableWidget_1gram_TagContainer.__class__ = myObjects.QTableWidget_token
        self.tableWidget_Ngram_TagContainer.__class__ = myObjects.QTableWidget_token
        self.tabWidget.setCurrentIndex(0)

        self.tableWidget_1gram_TagContainer.itemSelectionChanged.connect(self.onSelectedItem_table1Gram)

        #self.numberToken_show = config['value']['numberToken_show']

        # self.scores = None
        # self.alias_lookup = None
        #
        #
        # self.similarityMatrix_threshold = config['value']['similarityMatrix_threshold']
        #


    def set_dataframes(self, dataframe_1Gram = None, dataframe_NGram = None):
        """
        set the dataframe for the window
        :param dataframe_1Gram:
        :param dataframe_NGram:
        :return:
        """
        self.dataframe_1Gram=dataframe_1Gram
        self.tableWidget_1gram_TagContainer.set_dataframe(self.dataframe_1Gram)
        self.tableWidget_1gram_TagContainer.printDataframe_tableView(int(self.config['value']['numberToken_show']))
        self.dataframe_NGram=dataframe_NGram
        self.tableWidget_Ngram_TagContainer.set_dataframe(self.dataframe_NGram)
        self.tableWidget_Ngram_TagContainer.printDataframe_tableView(int(self.config['value']['numberToken_show']))

    def onSelectedItem_table1Gram(self):
        """
        action when we select an item from the table view
        :return:
        """
        items = self.tableWidget_1gram_TagContainer.selectedItems()  # selected row
        token, classification, alias, notes = (str(i.text()) for i in items)

        self.set_editor_value(alias, token, notes, classification)


        mask = self.dataframe_1Gram.index.str[0] == token[0]

        #TODO THURSTON which one should we keep
        matches = zz.extractBests(token, self.dataframe_1Gram.index[mask],
                                  limit=20)[:int(self.horizontalSlider_1gram_FindingThreshold.value()*20/100)]
        #matches = self.alias_lookup[token][:int(self.horizontalSlider_1gram_FindingThreshold.value()*1/10)]

        self.buttonGroup_1Gram_similarityPattern.set_checkBoxes(matches, 100)

    def set_editor_value(self, alias, token, notes, classification):
        """
        print all the information from the token to the right layout
        (alias, button, notes)
        :param alias:
        :param token:
        :param notes:
        :param classification:
        :return:
        """

        #alias
        if alias is None:
            self.lineEdit_1gram_AliasEditor.setText(alias)
        else:
            self.lineEdit_1gram_AliasEditor.setText(token)

        #notes
        self.textEdit_1gram_NoteEditor.setText(notes)

        #classification
        btn = self.classificationDictionary_1Gram.get(classification)
        btn.toggle()  # toggle that button

    def set_config(self, config):
        """
        add to the window the values from the config dict
        :param config
        :return:
        """
        self.config=config
        self.horizontalSlider_1gram_FindingThreshold.setValue(config['value']['similarityMatrix_threshold'])

        pass


    def get_config(self, config):
        """
        replace the given config dict with a new one based on the window values

        it is call when we save the view
        :param config:
        :return:
        """
        #config['value']['similarityMatrix_threshold'] =


        pass
        # if checked:
        #     config['file']['filePath_OriginalCSV']['headers'] = checked
        #     return True, config
        # else:
        #     Qw.QMessageBox.about(self, 'Can\'t save', "You might want to select at least 1 value")
        #     return False, None



if __name__ == "__main__":
    app = Qw.QApplication(sys.argv)
    window = MyTaggingToolWindow()
    window.show()
    sys.exit(app.exec_())