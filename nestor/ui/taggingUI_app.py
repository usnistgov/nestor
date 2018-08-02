from .helper_objects import CompositionNGramItem, MyMplCanvas, QButtonGroup_similarityPattern, QTableWidget_token
import nestor.keyword as kex

from pathlib import Path
import pandas as pd
import numpy as np
import fuzzywuzzy.process as zz

from PyQt5.QtCore import Qt
from PyQt5 import QtGui, uic
import PyQt5.QtWidgets as Qw



fname = 'taggingUI.ui'
script_dir = Path(__file__).parent
Ui_MainWindow_taggingTool, QtBaseClass_taggingTool = uic.loadUiType(script_dir/fname)


class MyTaggingToolWindow(Qw.QMainWindow, Ui_MainWindow_taggingTool):

    def __init__(self, iconPath=None, closeFunction=None, changeTag=None):
        Qw.QMainWindow.__init__(self)
        Ui_MainWindow_taggingTool.__init__(self)
        self.setupUi(self)
        self.closeFunction = closeFunction
        self.setGeometry(20, 20, 648, 705)
        #TODO make the "areyoysure" exit action
        #self.actionExit.triggered.connect(self.close_application)

        if iconPath:
            self.setWindowIcon(QtGui.QIcon(iconPath))

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
            'P': self.radioButton_Ngram_ProblemEditor,
            'S': self.radioButton_Ngram_SolutionEditor,
            '': self.radioButton_Ngram_NotClassifiedEditor
        }

        self.buttonDictionary_NGram = {
            'Item': 'I',
            'Problem Item': 'P I',
            'Solution Item': 'S I',
            'Ambiguous (Unknown)': 'U',
            'Stop-word': 'X',
            'Problem': 'P',
            'Solution': 'S',
            'not yet classified': ''
        }
        self.dataframe_Original=None
        self.dataframe_1Gram = None
        self.dataframe_NGram = None
        self.tokenExtractor_nGram = None
        self.tokenExtractor_1Gram = None
        self.clean_rawText_1Gram=None
        self.dataframe_1Gram=None
        self.tag_df = None
        self.tag_readable = None

        self.dataframe_completeness=None
        #self.alias_lookup = None
        self.similarityThreshold_alreadyChecked = 99

        self.buttonGroup_1Gram_similarityPattern = QButtonGroup_similarityPattern(self.verticalLayout_1gram_SimilarityPattern)
        self.tableWidget_1gram_TagContainer.__class__ = QTableWidget_token
        self.tableWidget_Ngram_TagContainer.__class__ = QTableWidget_token
        self.middleLayout_Ngram_Composition = CompositionNGramItem(self.verticalLayout_Ngram_CompositionDisplay)
        self.tabWidget.setCurrentIndex(0)

        self.tableWidget_1gram_TagContainer.itemSelectionChanged.connect(self.onSelectedItem_table1Gram)
        self.tableWidget_Ngram_TagContainer.itemSelectionChanged.connect(self.onSelectedItem_tableNGram)
        self.horizontalSlider_1gram_FindingThreshold.sliderMoved.connect(self.onSliderMoved_similarityPattern)
        self.horizontalSlider_1gram_FindingThreshold.sliderReleased.connect(self.onSliderMoved_similarityPattern)
        self.pushButton_1gram_UpdateTokenProperty.clicked.connect(self.onClick_updateButton_1Gram)
        self.pushButton_Ngram_UpdateTokenProperty.clicked.connect(self.onClick_updateButton_NGram)
        self.pushButton_1gram_SaveTableView.clicked.connect(lambda: self.onClick_saveButton(self.dataframe_1Gram, self.config['file']['filePath_1GrammCSV']['path']))
        self.pushButton_Ngram_SaveTableView.clicked.connect(lambda: self.onClick_saveButton(self.dataframe_NGram, self.config['file']['filePath_nGrammCSV']['path']))

        self.pushButton_report_saveTrack.clicked.connect(self.onClick_saveTrack)
        self.pushButton_report_saveNewCsv.clicked.connect(self.onClick_saveNewCsv)
        self.pushButton_report_saveBinnaryCsv.clicked.connect(self.onClick_saveTagsHDFS)

        self.completenessPlot= MyMplCanvas(self.gridLayout_report_progressPlot, self.tabWidget, self. dataframe_completeness)

        self.buttonGroup_NGram_Classification.buttonClicked.connect(self.onClick_changeClassification)


        # Load up the terms of service class/window
        self.terms_of_use = TermsOfServiceDialog(iconPath=iconPath) # doesn't need a close button, just "x" out
        self.actionAbout_TagTool.triggered.connect(self.terms_of_use.show)  # in the `about` menu>about TagTool

        self.tabWidget.currentChanged.connect(changeTag)


    def onClick_changeClassification(self, btn):
        new_clf = self.buttonDictionary_NGram.get(btn.text())
        items = self.tableWidget_Ngram_TagContainer.selectedItems()  # selected row
        tokens, classification, alias, notes = (str(i.text()) for i in items)

        if not alias:
            if new_clf in ['I','S','P']:
                labels = tokens.split(' ')  # the ngram component 1-gram parts
                #self.lineEdit_Ngram_AliasEditor.setStyleSheet("QLineEdit{background: red;}")

                self.lineEdit_Ngram_AliasEditor.setText("_".join(labels))


    def onClick_saveTrack(self):
        """save the current completness of the token in a dataframe
        :return:

        Parameters
        ----------

        Returns
        -------

        """
        print("progress saving; calculating the extracted tags and statistics...")
        # do 1-grams
        print('\n ONE GRAMS...')
        tags_df = kex.tag_extractor(self.tokenExtractor_1Gram,
                                         self.clean_rawText,
                                         vocab_df=self.dataframe_1Gram)
        # self.tags_read = kex._get_readable_tag_df(self.tags_df)

        # do 2-grams
        print('\n TWO GRAMS...')
        tags2_df = kex.tag_extractor(self.tokenExtractor_nGram,
                                          self.clean_rawText_1Gram,
                                          vocab_df=self.dataframe_NGram[self.dataframe_NGram.alias.notna()])

        # merge 1 and 2-grams.
        tag_df = tags_df.join(tags2_df.drop(axis='columns', labels=tags_df.columns.levels[1].tolist(), level=1))
        self.tag_readable = kex._get_readable_tag_df(tag_df)

        self.relation_df = tag_df.loc[:, ['P I', 'S I']]
        self.tag_df = tag_df.loc[:, ['I', 'P', 'S', 'U', 'X', 'NA']]
        # tag_readable.head(10)

        # do statistics
        tag_pct, tag_comp, tag_empt = kex.get_tag_completeness(self.tag_df)

        self.label_report_tagCompleteness.setText(f'Tag PPV: {tag_pct.mean():.2%} +/- {tag_pct.std():.2%}')
        self.label_report_completeDocs.setText(f'Complete Docs: {tag_comp} of {len(self.tag_df)}, or {tag_comp/len(tag_df):.2%}')
        self.label_report_emptyDocs.setText(f'Empty Docs: {tag_empt} of {len(self.tag_df)}, or {tag_empt/len(self.tag_df):.2%}')

        self.completenessPlot._set_dataframe(tag_pct)
        nbins = int(np.percentile(tag_df.sum(axis=1), 90))
        print(f'Docs have at most {nbins} tokens (90th percentile)')
        self.completenessPlot.plot_it(nbins)

        self.dataframe_completeness = tag_pct
        # return tag_readable, tag_df

    def onClick_saveNewCsv(self):
        """generate a new csv with the original csv and the generated token for the document
        :return:

        Parameters
        ----------

        Returns
        -------

        """
        # tag_readable, tag_df = self.onClick_saveTrack()
        #TODO add this stuff to the original csv data
        if self.tag_readable is None:
            self.onClick_saveTrack()
        fname = Path('.')/'READABLE_TAGS.csv'
        print("Saving a Readable csv with tagged documents. ", str(fname))
        self.dataframe_Original.join(self.tag_readable).to_csv(fname)
        print('DONE!')


    def onClick_saveTagsHDFS(self):
        """generate a new csv with the document and the tag occurences (0 if not 1 if )
        :return:

        Parameters
        ----------

        Returns
        -------

        """
        # tag_readable, tag_df = self.onClick_saveTrack()

        if self.tag_df is None:
            self.onClick_saveTrack()
        # fname = Path('.')
        fname, _ = Qw.QFileDialog.getSaveFileName(self, 'Save File')
        if fname[-3:] != '.h5':
            fname += '.h5'
        # print(self.dataframe_Original.shape, self.tag_df.shape, self.relation_df.shape)

        print(f"Saving {fname} as HDF5...")

        self.dataframe_Original.to_hdf(fname, key='df')
        self.tag_df.to_hdf(fname, key='tags')
        self.relation_df.to_hdf(fname, key='rels')
        print('DONE')
        #TODO add fname to config.yml as pre-loaded "update tag extraction"



    def onSelectedItem_table1Gram(self):
        """action when we select an item from the 1Gram table view
        :return:

        Parameters
        ----------

        Returns
        -------

        """
        items = self.tableWidget_1gram_TagContainer.selectedItems()  # selected row
        token, classification, alias, notes = (str(i.text()) for i in items)

        self._set_editorValue_1Gram(alias, token, notes, classification)
        matches = self._get_similarityMatches(token)

        self.buttonGroup_1Gram_similarityPattern.set_checkBoxes_initial(matches, self.similarityThreshold_alreadyChecked,self.dataframe_1Gram, alias)
        #self.buttonGroup_1Gram_similarityPattern.autoChecked(self.dataframe_1Gram, alias)

    def onSelectedItem_tableNGram(self):
        """action when we select an item from the NGram table view
        :return:

        Parameters
        ----------

        Returns
        -------

        """
        items = self.tableWidget_Ngram_TagContainer.selectedItems()  # selected row
        tokens, classification, alias, notes = (str(i.text()) for i in items)

        self.middleLayout_Ngram_Composition.printView(self.dataframe_1Gram, tokens)

        if not alias:
            if classification in ['P','S','I']:
                labels = tokens.split(' ')
                alias = '_'.join(labels)

        self._set_editorValue_NGram(alias, tokens, notes, classification)

    def onClick_saveButton(self, dataframe, path):
        """save the dataframe to the CSV file
        :return:

        Parameters
        ----------
        dataframe :
            
        path :
            

        Returns
        -------

        """
        dataframe.to_csv(path)

    def onClick_updateButton_1Gram(self):
        """Triggers with update button. Saves user annotation to the dataframe"""
        try:
            items = self.tableWidget_1gram_TagContainer.selectedItems()  # selected row
            token, classification, alias, notes = (str(i.text()) for i in items)

            new_alias = self.lineEdit_1gram_AliasEditor.text()
            new_notes = self.textEdit_1gram_NoteEditor.toPlainText()
            new_clf = self.buttonDictionary_1Gram.get(self.buttonGroup_1Gram_Classification.checkedButton().text(), pd.np.nan)
            self.dataframe_1Gram = self._set_dataframeItemValue(self.dataframe_1Gram, token, new_alias, new_clf, new_notes)
            self.tableWidget_1gram_TagContainer.set_dataframe(self.dataframe_1Gram)

            for btn in self.buttonGroup_1Gram_similarityPattern.buttons():
                if btn in self.buttonGroup_1Gram_similarityPattern.checkedButtons():
                    self.dataframe_1Gram = self._set_dataframeItemValue(self.dataframe_1Gram, btn.text(), new_alias, new_clf,
                                                                        new_notes)

                elif self.dataframe_1Gram.loc[btn.text()]['alias'] == alias:
                    self.dataframe_1Gram = self._set_dataframeItemValue(self.dataframe_1Gram, btn.text(), '',
                                                                       '', '')

            self.tableWidget_1gram_TagContainer.printDataframe_tableView()

            self.update_progress_bar(self.progressBar_1gram_TagComplete, self.dataframe_1Gram)
            self.tableWidget_1gram_TagContainer.selectRow(self.tableWidget_1gram_TagContainer.currentRow() + 1)


        except (IndexError, ValueError):
            Qw.QMessageBox.about(self, 'Can\'t select', "You should select a row first")

    def onClick_updateButton_NGram(self):
        """Triggers with update button. Saves user annotation to the dataframe"""
        try :
            items = self.tableWidget_Ngram_TagContainer.selectedItems()  # selected row
            token, classification, alias, notes = (str(i.text()) for i in items)


            new_alias = self.lineEdit_Ngram_AliasEditor.text()
            new_notes = self.textEdit_Ngram_NoteEditor.toPlainText()
            new_clf = self.buttonDictionary_NGram.get(self.buttonGroup_NGram_Classification.checkedButton().text(),
                                                      pd.np.nan)

            self.dataframe_NGram = self._set_dataframeItemValue(self.dataframe_NGram, token, new_alias, new_clf, new_notes)
            self.tableWidget_Ngram_TagContainer.set_dataframe(self.dataframe_NGram)

            self.tableWidget_Ngram_TagContainer.printDataframe_tableView()
            self.update_progress_bar(self.progressBar_Ngram_TagComplete, self.dataframe_NGram)
            self.tableWidget_Ngram_TagContainer.selectRow(self.tableWidget_Ngram_TagContainer.currentRow() + 1)

        except (IndexError, ValueError):
            Qw.QMessageBox.about(self, 'Can\'t select', "You should select a row first")
        pass

    def onSliderMoved_similarityPattern(self):
        """when the slider change, print the good groupboxes
        :return:

        Parameters
        ----------

        Returns
        -------

        """
        btn_checked = []
        for btn in self.buttonGroup_1Gram_similarityPattern.checkedButtons():
            btn_checked.append(btn.text())

        try:
            token = self.tableWidget_1gram_TagContainer.selectedItems()[0].text()
            matches = self._get_similarityMatches(token)
            self.buttonGroup_1Gram_similarityPattern.set_checkBoxes_rechecked(matches, btn_checked)

        except IndexError:
            Qw.QMessageBox.about(self, 'Can\'t select', "You should select a row first")

    def _set_dataframeItemValue(self, dataframe, token, alias, classification, notes):
        """update the value of the dataframe

        Parameters
        ----------
        dataframe :
            param token:
        alias :
            param classification:
        notes :
            return:
        token :
            
        classification :
            

        Returns
        -------

        """
        dataframe.loc[token,"alias"] = alias
        dataframe.loc[token,"notes"] = notes
        dataframe.loc[token,"NE"] = classification
        return dataframe

    def _set_dataframes(self, dataframe_1Gram = None, dataframe_NGram = None, dataframe_Original=None):
        """set the dataframe for the window

        Parameters
        ----------
        dataframe_1Gram :
            param dataframe_NGram: (Default value = None)
        dataframe_NGram :
             (Default value = None)
        dataframe_Original :
             (Default value = None)

        Returns
        -------

        """
        if dataframe_Original is not None:
            self.dataframe_Original= dataframe_Original
        # print('NEW TEST ALERT')
        # print(dataframe_1Gram)
        if dataframe_1Gram is not None:
            self.dataframe_1Gram=dataframe_1Gram
            self.tableWidget_1gram_TagContainer.set_dataframe(self.dataframe_1Gram)
            self.tableWidget_1gram_TagContainer.printDataframe_tableView()
            self.update_progress_bar(self.progressBar_1gram_TagComplete, self.dataframe_1Gram)

        if dataframe_NGram is not None:
            self.dataframe_NGram=dataframe_NGram
            self.tableWidget_Ngram_TagContainer.set_dataframe(self.dataframe_NGram)
            self.tableWidget_Ngram_TagContainer.printDataframe_tableView()
            self.update_progress_bar(self.progressBar_Ngram_TagComplete, self.dataframe_NGram)

    def _set_tokenExtractor(self, tokenExtractor_1Gram = None, tokenExtractor_nGram=None):
        """set both token extractore
        Needed for the report tab

        Parameters
        ----------
        tokenExtractor_1Gram :
             (Default value = None)
        tokenExtractor_nGram :
             (Default value = None)

        Returns
        -------

        """
        if tokenExtractor_1Gram is not None:
            self.tokenExtractor_1Gram = tokenExtractor_1Gram
        if tokenExtractor_nGram is not None:
            self.tokenExtractor_nGram = tokenExtractor_nGram

    def _set_cleanRawText(self, clean_rawText=None, clean_rawText_1Gram=None):
        """set the clean raw text
        Needed for the report tab

        Parameters
        ----------
        clean_rawText :
            param clean_rawText_1Gram: (Default value = None)
        clean_rawText_1Gram :
             (Default value = None)

        Returns
        -------

        """
        if clean_rawText is not None:
            self.clean_rawText= clean_rawText
        if clean_rawText_1Gram is not None:
            self.clean_rawText_1Gram=clean_rawText_1Gram

    def update_progress_bar(self, progressBar, dataframe):
        """set the value of the progress bar based on the dataframe score

        Parameters
        ----------
        progressBar :
            
        dataframe :
            

        Returns
        -------

        """
        scores = dataframe['score']
        matched = scores[dataframe['NE'] != '']
        #TODO THURSTON which one?
        #completed_pct = pd.np.log(matched+1).sum()/pd.np.log(self.scores+1).sum()
        completed_pct = matched.sum()/scores.sum()
        progressBar.setValue(100*completed_pct)

    def _set_editorValue_1Gram(self, alias, token, notes, classification):
        """print all the information from the token to the right layout 1Gram
        (alias, button, notes)

        Parameters
        ----------
        alias :
            param token:
        notes :
            param classification:
        token :
            
        classification :
            

        Returns
        -------

        """

        #alias
        if alias is '':
            self.lineEdit_1gram_AliasEditor.setText(token)
        else:
            self.lineEdit_1gram_AliasEditor.setText(alias)

        #notes
        self.textEdit_1gram_NoteEditor.setText(notes)

        #classification
        btn = self.classificationDictionary_1Gram.get(classification)
        try:
            btn.toggle()  # toggle that button
        except AttributeError:
            self.radioButton_1gram_NotClassifiedEditor.toggle()

    def _set_editorValue_NGram(self, alias, token, notes, classification):
        """print all the information from the token to the right layout NGram
        (alias, button, notes)

        Parameters
        ----------
        alias :
            
        token :
            
        notes :
            
        classification :
            

        Returns
        -------

        """
        # alias
        if alias is '':
            self.lineEdit_Ngram_AliasEditor.setText(token)
        else:
            self.lineEdit_Ngram_AliasEditor.setText(alias)

        # notes
        self.textEdit_Ngram_NoteEditor.setText(notes)

        # classification
        btn = self.classificationDictionary_NGram.get(classification)
        try:
            btn.toggle()  # toggle that button
        except AttributeError:
            self.radioButton_Ngram_NotClassifiedEditor.toggle()


    def _get_similarityMatches(self, token):
        """get the list of token similar to the given token

        Parameters
        ----------
        token :
            return:

        Returns
        -------

        """

        # TODO THURSTON which one should we keep
        # method 1: only find related terms with same 1st letter (way, way less computation)
        mask = self.dataframe_1Gram.index.str[0] == token[0]
        matches = zz.extractBests(token, self.dataframe_1Gram.index[mask],
                                  limit=20)[:int(self.horizontalSlider_1gram_FindingThreshold.value() * 20 / 100)]

        # # method 2: find all matching terms
        # matches = self.alias_lookup[token][:int(self.horizontalSlider_1gram_FindingThreshold.value()*1/10)]

        return matches

    def keyPressEvent(self, event):
        """listenr on the keyboard

        Parameters
        ----------
        e :
            return:
        event :
            

        Returns
        -------

        """

        if event.key() == Qt.Key_Return:
            if self.tabWidget.currentIndex() == 0:
                self.onClick_updateButton_1Gram()
            elif self.tabWidget.currentIndex() ==1:
                self.onClick_updateButton_NGram()


    def _set_config(self, config):
        """add to the window the values from the config dict

        Parameters
        ----------
        config :
            return:

        Returns
        -------

        """
        self.config=config
        self.tableWidget_1gram_TagContainer.set_vocabLimit(int(self.config['value']['numberToken_show']))
        self.tableWidget_Ngram_TagContainer.set_vocabLimit(int(self.config['value']['numberToken_show']))
        self.similarityThreshold_alreadyChecked = config['value']['similarityMatrix_alreadyChecked']

        self.horizontalSlider_1gram_FindingThreshold.setValue(config['value']['similarityMatrix_threshold'])



    def _get_config(self, config):
        """replace the given config dict with a new one based on the window values
        
        it is call when we save the view

        Parameters
        ----------
        config :
            return:

        Returns
        -------

        """
        pass

    def closeEvent(self, event):
        """trigger when we close the window

        Parameters
        ----------
        event :
            return:

        Returns
        -------

        """
        self.closeFunction(event)


# Now the ToS dialog .ui file
fname2 = 'termsOfUse.ui'
qtDesignerFile_tosDialog = script_dir/fname2
Ui_MainWindow_tosDialog, QtBaseClass_tos_Dialog = uic.loadUiType(qtDesignerFile_tosDialog)


class TermsOfServiceDialog(Qw.QDialog, Ui_MainWindow_tosDialog):
    """Class to instantiate window showing NIST license. FUTURE: any other versioning information."""
    def __init__(self, iconPath=None, closeFunction=None):
        Qw.QDialog.__init__(self)
        Ui_MainWindow_tosDialog.__init__(self)
        self.setupUi(self)
        self.closeFunction = closeFunction

        if iconPath:
            self.setWindowIcon(QtGui.QIcon(iconPath))

