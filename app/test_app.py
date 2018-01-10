import sys
from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtGui import *
import PyQt5.QtWidgets as qw
import csv
import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)
import pandas as pd
from test_skeleton import Ui_MainWindow
from fuzzywuzzy import process as zz

class MyWindow(qw.QMainWindow, Ui_MainWindow):
    def __init__(self):
        qw.QMainWindow.__init__(self)
        self.setupUi(self)
        # self.model = QStandardItemModel(self)
        # self.vocabTableView.setModel(self.model)
        # self.vocabTableView.horizontalHeader().setStretchLastSection(True)
        # self.vocabTableView.selectionChang
        openFile = self.actionOpen
        openFile.setShortcut("Ctrl+O")
        openFile.setStatusTip('Open File')
        openFile.triggered.connect(self.file_open)

        self.vocabTableWidget.itemSelectionChanged.connect(self.extract_row_info)
        self.df = None
        self.vocab_limit = 1000

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

        self.actionExit.triggered.connect(self.close_application)

        self.updateButton.clicked.connect(self.update_from_input)

    def close_application(self):
        # this running means somewhere, an option to leave has been clicked
        choice = qw.QMessageBox.question(self, 'Shut it Down',
                                      'Are you sure?',
                                      qw.QMessageBox.Yes | qw.QMessageBox.No)
        if choice == qw.QMessageBox.Yes:
            print('exiting program...')
            sys.exit()
        else:
            pass



    def file_open(self):
        """
        GUI file picker wrapper on pandas-to-tab method
        """
        # fileName, _ = qw.QFileDialog.getOpenFileName(self, 'Open File')
        fileName = 'app_vocab.csv'
        self.csv_to_tab(fileName)

    def file_save(self):
        fileName, _ = qw.QFileDialog.getOpenFileName(self, 'Save File')


    def extract_row_info(self):
        items = self.vocabTableWidget.selectedItems()  # selected row
        tok, clf, alias, notes = (str(i.text()) for i in items)
        # print(tok)
        # if clf in self.clf_mapper.keys():
        self.aliasEdit.setText(alias)  # preferred alias
        # btn = self.clf_mapper[clf]  # which button?
        btn = self.clf_mapper.get(clf, self.unsetButton)
        btn.toggle()  # toggle that button
        self.notesTextEdit.setText(notes)  # show any notes

        matches = zip(*zz.extractBests(tok, self.df.index.tolist(), limit=10,score_cutoff=75))
        print(list(matches)[0])


        #TODO Add dynamic check-boxes based on fuzzywuzzy

    def update_from_input(self):
        items = self.vocabTableWidget.selectedItems()  # selected row
        tok, clf, alias, notes = (str(i.text()) for i in items)

        # print(self.clfButtonGroup.checkedId())
        new_alias = self.aliasEdit.text()
        new_notes = self.notesTextEdit.text()
        new_clf = self.btn_mapper.get(self.clfButtonGroup.checkedButton().text(), pd.np.nan)

        self.df.loc[tok] = [new_clf, new_alias, new_notes]
        self.refresh_pd_tab()

        row = self.vocabTableWidget.currentRow()
        self.vocabTableWidget.selectRow(row+1)
        print(new_clf, new_alias, new_notes)

    def csv_to_tab(self, filename):
        self.df = pd.read_csv(filename, header=0, index_col=0)  # read file and set header row
        mask = self.df['NE'].notna()
        print(self.df.shape, self.df[mask].shape)
        self.df.loc[mask, 'alias'].fillna(self.df[mask].index.to_series(), inplace=True)

        self.refresh_pd_tab()

    def refresh_pd_tab(self):
        temp_df = self.df.reset_index()
        nrows, ncols = temp_df.shape
        self.vocabTableWidget.setColumnCount(ncols)
        self.vocabTableWidget.setRowCount(min([nrows, self.vocab_limit]))

        for i in range(min([nrows, self.vocab_limit])):
            for j in range(ncols):
                self.vocabTableWidget.setItem(i, j, qw.QTableWidgetItem(str(temp_df.iat[i, j])))

        self.vocabTableWidget.resizeColumnsToContents()
        self.vocabTableWidget.resizeRowsToContents()
        self.vocabTableWidget.setHorizontalHeaderLabels(temp_df.columns.tolist())
        self.vocabTableWidget.setSelectionBehavior(qw.QTableWidget.SelectRows)

        completed_pct = int(100 * self.df[self.df['NE'].notna()].shape[0] / self.df.shape[0])
        self.progressBar.setValue(completed_pct)


if __name__ == "__main__":
    app = qw.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())