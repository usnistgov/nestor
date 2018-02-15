import sys
from PyQt5.QtCore import QCoreApplication, Qt, QSize
from PyQt5.QtGui import *
import PyQt5.QtWidgets as Qw
import csv
import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)
import pandas as pd
from app.test_skeleton import Ui_MainWindow
from fuzzywuzzy import process as zz

from app.helper_objects import MyQButtonGroup
from app.helper_objects import MyQTableWidget
import tqdm


class MyWindow(Qw.QMainWindow, Ui_MainWindow):

    def __init__(self, vocab_filename=None):
        Qw.QMainWindow.__init__(self)
        self.setupUi(self)
        self.set_menu()

        self.actionExit.triggered.connect(self.close_application)

        self.vocabTableWidget = MyQTableWidget(self.centralwidget, self)
        self.gridLayout.addWidget(self.vocabTableWidget, 1, 2, 1, 1)
        self.vocabTableWidget.itemSelectionChanged.connect(self.table_item_selected)
        self.simthresSlider.sliderReleased.connect(self.fuzz_thres)
        self.df = None
        self.scores = None
        self.alias_lookup = None
        self.vocab_limit = 1000
        val = self.simthresSlider.value()
        self.thres = val
        self.vocab_filename = vocab_filename

        self.clf_mapper = {
            'S': self.sltnButton,
            'P': self.probButton,
            'I': self.itemButton,
            'X': self.stpwButton,
            'U': self.unknButton
        }

        self.btn_mapper = {
            'Item': 'I',
            'Problem': 'P',
            'Solution': 'S',
            'Unknown': 'U',
            'Stop-word': 'X',
            'not yet classified': pd.np.nan
        }

        self.updateButton.clicked.connect(self.update_from_input)

        self.vertCheckButtonGroup = MyQButtonGroup(self.vertCheckBoxLayout)

        self.set_shortcut()
        if self.vocab_filename is not None:
            self.set_dataframe(self.vocab_filename)

    def set_dataframe(self, filename):
        self.df = pd.read_csv(filename, header=0, index_col=0)  # read file and set header row
        self.df = self.df[~self.df.index.duplicated(keep='first')]
        mask = self.df['NE'].notna()
        #print(self.df.shape, self.df[mask].shape)
        self.df.loc[mask, 'alias'].fillna(self.df[mask].index.to_series(), inplace=True)
        self.df.fillna('', inplace=True)
        # self.df.index = self.df.index.astype(str)
        # print(self.df.head())
        self.scores = self.df['score']

        # initialize alias matcher
        # self.alias_lookup = {}
        # for i in tqdm.tqdm(self.df.index[:self.vocab_limit]):
        #     mask = self.df.index.str[0] == i[0]
        #     self.alias_lookup[i] = zz.extractBests(i, self.df.index[mask], limit=20)

        self.vocabTableWidget.print_table(self.df, self.vocab_limit)

    def table_item_selected(self):
        items = self.vocabTableWidget.selectedItems()  # selected row
        tok, clf, alias, notes = (str(i.text()) for i in items)
        if alias is not '':
            self.aliasEdit.setText(alias)  # preferred alias
        else:
            self.aliasEdit.setText(tok)  # Default to tok
        btn = self.clf_mapper.get(clf, self.unsetButton)
        btn.toggle()  # toggle that button
        self.notesTextEdit.setText(notes)  # show any notes
        mask = self.df.index.str[0] == tok[0]
        # print(mask.sum())
        matches = zz.extractBests(tok, self.df.index[mask],
                                  limit=20)[:int(self.thres*20/100)]
        # matches = self.alias_lookup[tok][:int(self.thres*1/10)]
        self.vertCheckButtonGroup.update_checkboxes(tok, matches, self.df)

    def update_from_input(self):
        """
        Triggers with update button. Saves user annotation to self.df
        """
        items = self.vocabTableWidget.selectedItems()  # selected row
        tok, clf, alias, notes = (str(i.text()) for i in items)

        new_alias = self.aliasEdit.text()
        new_notes = self.notesTextEdit.text()
        new_clf = self.btn_mapper.get(self.clfButtonGroup.checkedButton().text(), pd.np.nan)

        tok_list = [tok]

        for btn in self.vertCheckButtonGroup.buttons():
            s = btn.text()
            if btn.isChecked():
                tok_list += [s]
            else:
                if new_alias == self.df.loc[s, 'alias']:
                    self.df.loc[s, 'NE'] = ''
                    self.df.loc[s, 'alias'] = ''
                    self.df.loc[s, 'notes'] = ''

        self.df.loc[tok_list, 'NE'] = new_clf
        self.df.loc[tok_list, 'alias'] = new_alias
        self.df.loc[tok_list, 'notes'] = new_notes
        self.vocabTableWidget.print_table(self.df, self.vocab_limit)
        self.vocabTableWidget.setFocus()

        row = self.vocabTableWidget.currentRow()
        self.vocabTableWidget.selectRow(row+1)
        #print(new_clf, new_alias, new_notes)

        self.update_progress_bar()

    def update_progress_bar(self):
        matched = self.scores[self.df['NE'] != '']
        # log-"usefulness" proxy by tf-idf
        completed_pct = pd.np.log(matched+1).sum()/pd.np.log(self.scores+1).sum()
        completed_pct = matched.sum()/self.scores.sum()
        # print(completed_pct)
        self.progressBar.setValue(100*completed_pct)

    def fuzz_thres(self):
        val = self.simthresSlider.value()
        self.thres = val
        self.table_item_selected()

    def file_open(self):
        """
        Open the csv file and save it as a dataframe using set_dataframe
        """
        try:
            fileName, _ = Qw.QFileDialog.getOpenFileName(self, 'Open File')
            # fileName = 'app_vocab.csv'
            self.set_dataframe(fileName)
            self.update_progress_bar()
            #self.csv_to_tab(fileName)
        except FileNotFoundError:
            pass

    def file_save(self):
        fileName, _ = Qw.QFileDialog.getSaveFileName(self, 'Save File')
        self.df.reset_index().to_csv(fileName, index=False)

    def set_menu(self):
        self.openFile = self.actionOpen
        self.openFile.setStatusTip('Open File')
        self.openFile.triggered.connect(self.file_open)
        self.saveFile = self.actionSave
        self.saveFile.setStatusTip('Save File')
        self.saveFile.triggered.connect(self.file_save)

    def set_shortcut(self):
        self.openFile.setShortcut("Ctrl+O")
        self.saveFile.setShortcut("Ctrl+S")
        self.itemButton.setShortcut(QCoreApplication.translate("MainWindow", "Alt+I"))
        self.probButton.setShortcut(QCoreApplication.translate("MainWindow", "Alt+P"))
        self.unknButton.setShortcut(QCoreApplication.translate("MainWindow", "Alt+U"))
        self.sltnButton.setShortcut(QCoreApplication.translate("MainWindow", "Alt+S"))
        self.stpwButton.setShortcut(QCoreApplication.translate("MainWindow", "Alt+X"))
        self.unsetButton.setShortcut(QCoreApplication.translate("MainWindow", "Alt+Shift+X"))

        notesShortCut = Qw.QShortcut(QKeySequence("Alt+N"), self)
        notesShortCut.activated.connect(lambda: self.editing_mode(self.notesTextEdit))

        aliasShortCut = Qw.QShortcut(QKeySequence("Alt+A"), self)
        aliasShortCut.activated.connect(lambda: self.editing_mode(self.aliasEdit))

    def editing_mode(self, field):
        field.setFocus()
        field.selectAll()

    def close_application(self):
        # this running means somewhere, an option to leave has been clicked
        choice = Qw.QMessageBox.question(self, 'Shut it Down',
                                      'Are you sure?',
                                         Qw.QMessageBox.Yes | Qw.QMessageBox.No)
        if choice == Qw.QMessageBox.Yes:
            print('exiting program...')
            sys.exit()
        else:
            pass

if __name__ == "__main__":
    app = Qw.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())

