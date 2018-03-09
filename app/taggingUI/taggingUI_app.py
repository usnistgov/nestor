import sys
from PyQt5.QtCore import QCoreApplication, Qt, QSize
from PyQt5 import QtGui
import PyQt5.QtWidgets as Qw
from PyQt5.QtGui import QIcon
from fuzzywuzzy import process as zz
import pandas as pd


from app.taggingUI import helper_objects as myObjects
from app.taggingUI.taggingUI_skeleton import Ui_MainWindow_taggingTool


class MyTaggingToolWindow(Qw.QMainWindow, Ui_MainWindow_taggingTool):

    def __init__(self,iconPath=None):
        Qw.QMainWindow.__init__(self)
        self.setupUi(self)
        if iconPath:
            self.setWindowIcon(QIcon(iconPath))

        #TODO add this to the yaml file
        self.similarityThreshold_alreadyChecked = 100

        self.classificationDictionary_1Gram = {
            'S': self.radioButton_1gram_SolutionEditor,
            'P': self.radioButton_1gram_ProblemEditor,
            'I': self.radioButton_1gram_ItemEditor,
            'X': self.radioButton_1gram_StopWordEditor,
            'U': self.radioButton_1gram_UnknownEditor,
            '' : self.radioButton_1gram_NotClassifiedEditor
        }
        self.buttonDictionary_1Gram = {
            'Item': 'I',
            'Problem': 'P',
            'Solution': 'S',
            'Ambiguous (Unknown)': 'U',
            'Stop-word': 'X',
            'not yet classified': pd.np.nan
        }

        self.dataframe_1Gram = None
        self.dataframe_NGram = None
        self.score = None
        #self.alias_lookup = None

        self.buttonGroup_1Gram_similarityPattern = myObjects.QButtonGroup_similarityPattern(self.verticalLayout_1gram_SimilarityPattern)
        self.tableWidget_1gram_TagContainer.__class__ = myObjects.QTableWidget_token
        self.tableWidget_Ngram_TagContainer.__class__ = myObjects.QTableWidget_token
        self.tabWidget.setCurrentIndex(0)

        self.tableWidget_1gram_TagContainer.itemSelectionChanged.connect(self.onSelectedItem_table1Gram)
        self.horizontalSlider_1gram_FindingThreshold.sliderMoved.connect(self.onSliderMoved_similarityPattern)
        self.horizontalSlider_1gram_FindingThreshold.sliderReleased.connect(self.onSliderMoved_similarityPattern)
        self.pushButton_1gram_UpdateTokenProperty.clicked.connect(self.onClick_updateButton)


    def onSelectedItem_table1Gram(self):
        """
        action when we select an item from the table view
        :return:
        """
        items = self.tableWidget_1gram_TagContainer.selectedItems()  # selected row
        token, classification, alias, notes = (str(i.text()) for i in items)

        self.set_editor_value(alias, token, notes, classification)
        matches = self.get_similarityMatches(token)

        self.buttonGroup_1Gram_similarityPattern.set_checkBoxes(matches, self.similarityThreshold_alreadyChecked)
        self.update_progress_bar()


    def onClick_updateButton(self):
        """
        Triggers with update button. Saves user annotation to self.df
        """
        try:
            items = self.tableWidget_1gram_TagContainer.selectedItems()  # selected row
            token, classification, alias, notes = (str(i.text()) for i in items)

            new_alias = self.lineEdit_1gram_AliasEditor.text()
            new_notes = self.textEdit_1gram_NoteEditor.toPlainText()
            new_clf = self.buttonDictionary_1Gram.get(self.buttonGroup_1Gram_Classification.checkedButton().text(), pd.np.nan)

            #for btn in self.buttonGroup_1Gram_similarityPattern.checkedButtons():

        except IndexError:
            Qw.QMessageBox.about(self, 'Can\'t select', "You should select a row first")


        #
        # tok_list = [tok]
        #
        # for btn in self.vertCheckButtonGroup.buttons():
        #     s = btn.text()
        #     if btn.isChecked():
        #         tok_list += [s]
        #     else:
        #         if new_alias == self.df.loc[s, 'alias']:
        #             self.df.loc[s, 'NE'] = ''
        #             self.df.loc[s, 'alias'] = ''
        #             self.df.loc[s, 'notes'] = ''
        #
        # self.df.loc[tok_list, 'NE'] = new_clf
        # self.df.loc[tok_list, 'alias'] = new_alias
        # self.df.loc[tok_list, 'notes'] = new_notes
        # self.vocabTableWidget.print_table(self.df, self.vocab_limit)
        # self.vocabTableWidget.setFocus()
        #
        # row = self.vocabTableWidget.currentRow()
        # self.vocabTableWidget.selectRow(row+1)
        # #print(new_clf, new_alias, new_notes)
        #
        # self.update_progress_bar()


    def onSliderMoved_similarityPattern(self):
        """
        when the slider change, print the good groupboxes
        :return:
        """
        #TODO get the checkbox already checked and rechecked it
        threshold = self.horizontalSlider_1gram_FindingThreshold.value()

        try:
            token = self.tableWidget_1gram_TagContainer.selectedItems()[0].text()
            matches = self.get_similarityMatches(token)

            self.buttonGroup_1Gram_similarityPattern.set_checkBoxes(matches, self.similarityThreshold_alreadyChecked)

        except IndexError:
            Qw.QMessageBox.about(self, 'Can\'t select', "You should select a row first")

    def set_dataframeItemValue(self, dataframe, item, alias, classification, notes):
        dataframe[item]["alias"] = alias
        dataframe[item]["notes"] = notes
        dataframe[item]["NE"] = classification

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

        self.scores = self.dataframe_1Gram['score']
        self.update_progress_bar()

    def update_progress_bar(self):
        """
        set the value of the progress bar based on the dataframe score
        """
        matched = self.scores[self.dataframe_1Gram['NE'].notna()]
        #TODO THURSTON which one?
        #completed_pct = pd.np.log(matched+1).sum()/pd.np.log(self.scores+1).sum()
        completed_pct = matched.sum()/self.scores.sum()
        self.progressBar_1gram_TagComplete.setValue(100*completed_pct)

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

    def get_similarityMatches(self, token):
        """
        get the list of token similar to the given token
        :param token:
        :return:
        """

        # TODO THURSTON which one should we keep
        mask = self.dataframe_1Gram.index.str[0] == token[0]
        matches = zz.extractBests(token, self.dataframe_1Gram.index[mask],
                                  limit=20)[:int(self.horizontalSlider_1gram_FindingThreshold.value() * 20 / 100)]
        #matches = self.alias_lookup[token][:int(self.horizontalSlider_1gram_FindingThreshold.value()*1/10)]

        return matches


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
        pass


if __name__ == "__main__":
    app = Qw.QApplication(sys.argv)
    window = MyTaggingToolWindow()
    window.show()
    sys.exit(app.exec_())