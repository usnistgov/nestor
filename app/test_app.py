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

        saveFile = self.actionSave
        saveFile.setShortcut("Ctrl+S")
        saveFile.setStatusTip('Save File')
        saveFile.triggered.connect(self.file_save)

        aliasShortCut = qw.QShortcut(QKeySequence("Alt+A"), self)
        aliasShortCut.activated.connect(lambda: self.editing_mode(self.aliasEdit))

        notesShortCut = qw.QShortcut(QKeySequence("Alt+N"), self)

        notesShortCut.activated.connect(lambda: self.editing_mode(self.notesTextEdit))

        self.vocabTableWidget.itemSelectionChanged.connect(self.extract_row_info)
        # self.vocabTableWidget.itemClicked.connect(self.extract_row_info)
        # self.vocabTableWidget.keyReleaseEvent(QKeyEvent(Qt.Key_Up)).connect(self.extract_row_info)

        # self.keyReleaseEvent()

        self.vocabTableWidget.setFocus()
        self.simthresSlider.sliderReleased.connect(self.fuzz_thres)
        self.df = None
        self.vocab_limit = 1000
        self.thres = 75

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

        self.vertCheckButtonGroup = qw.QButtonGroup()
        self.vertCheckButtonGroup.setExclusive(False)
        # self.vertCheckButtonGroup)

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
        try:
            fileName, _ = qw.QFileDialog.getOpenFileName(self, 'Open File')
            # fileName = 'app_vocab.csv'
            self.csv_to_tab(fileName)
        except FileNotFoundError:
            pass

    def file_save(self):
        fileName, _ = qw.QFileDialog.getSaveFileName(self, 'Save File')
        self.df.reset_index().to_csv(fileName, index=False)

    def editing_mode(self, field):
        # self.alias
        field.setFocus()
        field.selectAll()

    def extract_row_info(self):
        items = self.vocabTableWidget.selectedItems()  # selected row
        tok, clf, alias, notes = (str(i.text()) for i in items)
        # print(tok)
        # if clf in self.clf_mapper.keys():
        if alias is not '':
            self.aliasEdit.setText(alias)  # preferred alias
        else:
            self.aliasEdit.setText(tok)  # Default to tok
        # btn = self.clf_mapper[clf]  # which button?
        btn = self.clf_mapper.get(clf, self.unsetButton)
        btn.toggle()  # toggle that button
        self.notesTextEdit.setText(notes)  # show any notes

        matches = zz.extractBests(tok, self.df.index.tolist(),
                                       limit=10, score_cutoff=self.thres)[::-1]


        # print(list(list(matches)[0]))
        self.update_checkboxes(tok, matches)

    def update_checkboxes(self, tok, matches):

        for widg in self.vertCheckButtonGroup.buttons():
            self.vertCheckButtonGroup.removeButton(widg)
            self.vertCheckBoxLayout.removeWidget(widg)
            widg.deleteLater()

        for n, (match, score) in enumerate(matches):
            # print(match)
            btn = qw.QCheckBox(f'{len(matches)-n-1} - '+match, self)
            btn.setShortcut(f'Alt+{len(matches)-n-1}')
            cond = (self.df.loc[match, 'alias'] == self.df.loc[tok, 'alias']) \
                   and (self.df.loc[match, 'alias'] != '')
            if (match == tok) or cond:
                btn.toggle()
            self.vertCheckButtonGroup.addButton(btn)
            self.vertCheckBoxLayout.insertWidget(0, btn)

    def update_from_input(self):
        """
        Triggers with update button. Saves user annotation to self.df
        """
        items = self.vocabTableWidget.selectedItems()  # selected row
        tok, clf, alias, notes = (str(i.text()) for i in items)

        # print(self.clfButtonGroup.checkedId())
        new_alias = self.aliasEdit.text()
        new_notes = self.notesTextEdit.text()
        new_clf = self.btn_mapper.get(self.clfButtonGroup.checkedButton().text(), pd.np.nan)

        tok_list = [tok]
        rmv_list = []
        for btn in self.vertCheckButtonGroup.buttons():
            s = btn.text()[4:]
            if btn.isChecked():
                tok_list += [s]
            else:
                if new_alias == self.df.loc[s, 'alias']:
                    self.df.loc[s, 'NE'] = ''
                    self.df.loc[s, 'alias'] = ''
                    self.df.loc[s, 'notes'] = ''

        print([new_clf, new_alias, new_notes])
        self.df.loc[tok_list, 'NE'] = new_clf
        self.df.loc[tok_list, 'alias'] = new_alias
        self.df.loc[tok_list, 'notes'] = new_notes
        self.refresh_pd_tab()
        self.vocabTableWidget.setFocus()

        row = self.vocabTableWidget.currentRow()
        self.vocabTableWidget.selectRow(row+1)
        print(new_clf, new_alias, new_notes)

    def csv_to_tab(self, filename):
        self.df = pd.read_csv(filename, header=0, index_col=0)  # read file and set header row
        mask = self.df['NE'].notna()
        print(self.df.shape, self.df[mask].shape)
        self.df.loc[mask, 'alias'].fillna(self.df[mask].index.to_series(), inplace=True)
        self.df.fillna('', inplace=True)
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

        completed_pct = int(100 * self.df[self.df['NE'] != ''].shape[0] / self.df.shape[0])
        self.progressBar.setValue(completed_pct)

    def fuzz_thres(self):
        val = self.simthresSlider.value()
        self.thres = val
        self.extract_row_info()

if __name__ == "__main__":
    app = qw.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())