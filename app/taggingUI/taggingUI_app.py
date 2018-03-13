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

        #TODO make the "areyoysure" exit action
        #self.actionExit.triggered.connect(self.close_application)

        if iconPath:
            self.setWindowIcon(QIcon(iconPath))

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
            'not yet classified': ''
        }

        self.classificationDictionary_NGram = {
            'S I': self.radioButton_Ngram_SolutionItemEditor,
            'P I': self.radioButton_Ngram_ProblemItemEditor,
            'I': self.radioButton_Ngram_ItemEditor,
            'U': self.radioButton_Ngram_UnknownEditor,
            'X': self.radioButton_Ngram_StopWordEditor,
            '': self.radioButton_Ngram_NotClassifiedEditor
        }

        self.buttonDictionary_NGram = {
            'Item': 'I',
            'Problem Item': 'P I',
            'Solution Item': 'S I',
            'Unknown': 'U',
            'Stop-word': 'X',
            'not yet classified': ''
        }

        self.dataframe_1Gram = None
        self.dataframe_NGram = None
        #self.alias_lookup = None

        self.buttonGroup_1Gram_similarityPattern = myObjects.QButtonGroup_similarityPattern(self.verticalLayout_1gram_SimilarityPattern)
        self.tableWidget_1gram_TagContainer.__class__ = myObjects.QTableWidget_token
        self.tableWidget_Ngram_TagContainer.__class__ = myObjects.QTableWidget_token
        self.middleLayout_Ngram_Composition = myObjects.CompositionNGramItem(self.verticalLayout_Ngram_CompositionDisplay)
        self.tabWidget.setCurrentIndex(0)

        self.tableWidget_1gram_TagContainer.itemSelectionChanged.connect(self.onSelectedItem_table1Gram)
        self.tableWidget_Ngram_TagContainer.itemSelectionChanged.connect(self.onSelectedItem_tableNGram)
        self.horizontalSlider_1gram_FindingThreshold.sliderMoved.connect(self.onSliderMoved_similarityPattern)
        self.horizontalSlider_1gram_FindingThreshold.sliderReleased.connect(self.onSliderMoved_similarityPattern)
        self.pushButton_1gram_UpdateTokenProperty.clicked.connect(self.onClick_updateButton_1Gram)
        self.pushButton_Ngram_UpdateTokenProperty.clicked.connect(self.onClick_updateButton_NGram)
        self.pushButton_1gram_SaveTableView.clicked.connect(lambda: self.onClick_saveButton(self.dataframe_1Gram, self.config['file']['filePath_1GrammCSV']['path']))
        self.pushButton_Ngram_SaveTableView.clicked.connect(lambda: self.onClick_saveButton(self.dataframe_NGram, self.config['file']['filePath_nGrammCSV']['path']))
        self.tabWidget.currentChanged.connect(self.onClick_selectTab)

    def onClick_selectTab(self, index):
        """
        when click on refrech button in the Ngram view
        It refrech the Ngram Dataframe based on the 1Gram
        :return:
        """
        if index == 1:
            print(index)


        #TODO THURSTON i do not understand your logic about the tokenExtractor object


    def onSelectedItem_table1Gram(self):
        """
        action when we select an item from the 1Gram table view
        :return:
        """
        items = self.tableWidget_1gram_TagContainer.selectedItems()  # selected row
        token, classification, alias, notes = (str(i.text()) for i in items)

        self.set_editorValue_1Gram(alias, token, notes, classification)
        matches = self.get_similarityMatches(token)

        self.buttonGroup_1Gram_similarityPattern.set_checkBoxes_initial(matches, self.similarityThreshold_alreadyChecked)
        self.buttonGroup_1Gram_similarityPattern.set_checkedBoxes(self.dataframe_1Gram, alias)

    def onSelectedItem_tableNGram(self):
        """
        action when we select an item from the NGram table view
        :return:
        """
        items = self.tableWidget_Ngram_TagContainer.selectedItems()  # selected row
        token, classification, alias, notes = (str(i.text()) for i in items)

        self.set_editorValue_NGram(alias, token, notes, classification)
        self.middleLayout_Ngram_Composition.printView(self.dataframe_1Gram, token)



    def onClick_saveButton(self, dataframe, path):
        """
        save the dataframe to the CSV file
        :return:
        """
        dataframe.to_csv(path)


    def onClick_updateButton_1Gram(self):
        """
        Triggers with update button. Saves user annotation to the dataframe
        """
        try:
            items = self.tableWidget_1gram_TagContainer.selectedItems()  # selected row
            token, classification, alias, notes = (str(i.text()) for i in items)

            new_alias = self.lineEdit_1gram_AliasEditor.text()
            new_notes = self.textEdit_1gram_NoteEditor.toPlainText()
            new_clf = self.buttonDictionary_1Gram.get(self.buttonGroup_1Gram_Classification.checkedButton().text(), pd.np.nan)
            self.dataframe_1Gram = self.set_dataframeItemValue(self.dataframe_1Gram, token, new_alias, new_clf, new_notes)
            self.tableWidget_1gram_TagContainer.set_dataframe(self.dataframe_1Gram)

            for btn in self.buttonGroup_1Gram_similarityPattern.buttons():
                if btn in self.buttonGroup_1Gram_similarityPattern.checkedButtons():
                    self.dataframe_1Gram = self.set_dataframeItemValue(self.dataframe_1Gram, btn.text(), new_alias, new_clf,
                                                                   new_notes)

                elif self.dataframe_1Gram.loc[btn.text()]['alias'] == alias:
                    self.dataframe_1Gram = self.set_dataframeItemValue(self.dataframe_1Gram, btn.text(), '',
                                                                       '', '')

            self.tableWidget_1gram_TagContainer.printDataframe_tableView()

            self.update_progress_bar(self.progressBar_1gram_TagComplete, self.dataframe_1Gram)
            self.tableWidget_1gram_TagContainer.selectRow(self.tableWidget_1gram_TagContainer.currentRow() + 1)


        except (IndexError, ValueError):
            Qw.QMessageBox.about(self, 'Can\'t select', "You should select a row first")

    def onClick_updateButton_NGram(self):
        """
        Triggers with update button. Saves user annotation to the dataframe
        """
        #TODO
        try :
            items = self.tableWidget_Ngram_TagContainer.selectedItems()  # selected row
            token, classification, alias, notes = (str(i.text()) for i in items)

            new_alias = self.lineEdit_Ngram_AliasEditor.text()
            new_notes = self.textEdit_Ngram_NoteEditor.toPlainText()
            new_clf = self.buttonDictionary_NGram.get(self.buttonGroup_NGram_Classification.checkedButton().text(),
                                                      pd.np.nan)
            self.dataframe_NGram = self.set_dataframeItemValue(self.dataframe_NGram, token, new_alias, new_clf, new_notes)
            self.tableWidget_Ngram_TagContainer.set_dataframe(self.dataframe_NGram)

            self.tableWidget_Ngram_TagContainer.printDataframe_tableView()
            self.update_progress_bar(self.progressBar_Ngram_TagComplete, self.dataframe_NGram)
            self.tableWidget_Ngram_TagContainer.selectRow(self.tableWidget_Ngram_TagContainer.currentRow() + 1)

        except (IndexError, ValueError):
            Qw.QMessageBox.about(self, 'Can\'t select', "You should select a row first")
        pass


    def onSliderMoved_similarityPattern(self):
        """
        when the slider change, print the good groupboxes
        :return:
        """
        btn_checked = []
        for btn in self.buttonGroup_1Gram_similarityPattern.checkedButtons():
            btn_checked.append(btn.text())

        try:
            token = self.tableWidget_1gram_TagContainer.selectedItems()[0].text()
            matches = self.get_similarityMatches(token)
            self.buttonGroup_1Gram_similarityPattern.set_checkBoxes_rechecked(matches, btn_checked)

        except IndexError:
            Qw.QMessageBox.about(self, 'Can\'t select', "You should select a row first")

    def set_dataframeItemValue(self, dataframe, token, alias, classification, notes):
        """
        update the value of the dataframe
        :param dataframe:
        :param token:
        :param alias:
        :param classification:
        :param notes:
        :return:
        """
        dataframe.loc[token,"alias"] = alias
        dataframe.loc[token,"notes"] = notes
        dataframe.loc[token,"NE"] = classification
        return dataframe

    def set_dataframes(self, dataframe_1Gram = None, dataframe_NGram = None):
        """
        set the dataframe for the window
        :param dataframe_1Gram:
        :param dataframe_NGram:
        :return:
        """
        # print('NEW TEST ALERT')
        # print(dataframe_1Gram)
        self.dataframe_1Gram=dataframe_1Gram
        self.tableWidget_1gram_TagContainer.set_dataframe(self.dataframe_1Gram)
        self.tableWidget_1gram_TagContainer.printDataframe_tableView()

        self.dataframe_NGram=dataframe_NGram
        self.tableWidget_Ngram_TagContainer.set_dataframe(self.dataframe_NGram)
        self.tableWidget_Ngram_TagContainer.printDataframe_tableView()

        self.update_progress_bar(self.progressBar_1gram_TagComplete, self.dataframe_1Gram)
        self.update_progress_bar(self.progressBar_Ngram_TagComplete, self.dataframe_NGram)

    def update_progress_bar(self, progressBar, dataframe):
        """
        set the value of the progress bar based on the dataframe score
        """
        scores = dataframe['score']
        matched = scores[dataframe['NE'] != '']
        #TODO THURSTON which one?
        #completed_pct = pd.np.log(matched+1).sum()/pd.np.log(self.scores+1).sum()
        completed_pct = matched.sum()/scores.sum()
        progressBar.setValue(100*completed_pct)

    def set_editorValue_1Gram(self, alias, token, notes, classification):
        """
        print all the information from the token to the right layout 1Gram
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

    def set_editorValue_NGram(self, alias, token, notes, classification):
        """
        print all the information from the token to the right layout NGram
        (alias, button, notes)
        """
        # alias
        if alias is None:
            self.lineEdit_Ngram_AliasEditor.setText(alias)
        else:
            self.lineEdit_Ngram_AliasEditor.setText(token)

        # notes
        self.textEdit_Ngram_NoteEditor.setText(notes)

        # classification
        btn = self.classificationDictionary_NGram.get(classification)
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
        self.tableWidget_1gram_TagContainer.set_vocabLimit(int(self.config['value']['numberToken_show']))
        self.tableWidget_Ngram_TagContainer.set_vocabLimit(int(self.config['value']['numberToken_show']))
        self.similarityThreshold_alreadyChecked = config['value']['similarityMatrix_alreadyChecked']

        self.horizontalSlider_1gram_FindingThreshold.setValue(config['value']['similarityMatrix_threshold'])



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