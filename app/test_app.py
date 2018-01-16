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


class MyQButtonGroup(qw.QButtonGroup):

    def __init__(self, layout, btn_checks=None):
        qw.QButtonGroup.__init__(self)
        self.setExclusive(False)
        self.layout = layout
        self.btn_checks=btn_checks

    def update_checkboxes(self, tok, matches, df):
        self.clean_checkboxes()
        self.create_checkboxes(tok, matches, df)
        self.set_shortcut()

    def clean_checkboxes(self):
        for widg in self.buttons():
            self.removeButton(widg)
            self.layout.removeWidget(widg)
            widg.deleteLater()

    def create_checkboxes(self, tok, matches, df):
        nbr_widget = self.layout.count()
        for n, (match, score) in enumerate(matches):
            btn = qw.QCheckBox(f'{n} - ' + match)
            cond = (df.loc[match, 'alias'] == df.loc[tok, 'alias']) \
                   and (df.loc[match, 'alias'] != '')
            if (match == tok) or cond:
                btn.toggle()
            self.addButton(btn)
            self.layout.insertWidget(self.layout.count() - nbr_widget, btn)

    def set_shortcut(self):
        for n, btn in enumerate(self.buttons()):
            btn.setShortcut(f'Alt+{n}')


class MyWindow(qw.QMainWindow, Ui_MainWindow):

    def __init__(self):
        qw.QMainWindow.__init__(self)
        self.setupUi(self)
        # self.model = QStandardItemModel(self)
        # self.vocabTableView.setModel(self.model)
        # self.vocabTableView.horizontalHeader().setStretchLastSection(True)
        # self.vocabTableView.selectionChang
        self.openFile = self.actionOpen
        self.openFile.setStatusTip('Open File')
        self.openFile.triggered.connect(self.file_open)
        self.saveFile = self.actionSave
        self.saveFile.setStatusTip('Save File')
        self.saveFile.triggered.connect(self.file_save)

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

        self.vertCheckButtonGroup = MyQButtonGroup(self.vertCheckBoxLayout)

        self.set_shortcut()

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
                                       limit=10, score_cutoff=self.thres)

        self.vertCheckButtonGroup.update_checkboxes(tok, matches, self.df)

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

        #TODO see doc QAbstractButton *QButtonGroup::checkedButton()
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

    def set_shortcut(self):
        self.openFile.setShortcut("Ctrl+O")
        self.saveFile.setShortcut("Ctrl+S")
        self.itemButton.setShortcut(QCoreApplication.translate("MainWindow", "Alt+I"))
        self.probButton.setShortcut(QCoreApplication.translate("MainWindow", "Alt+P"))
        self.unknButton.setShortcut(QCoreApplication.translate("MainWindow", "Alt+U"))
        self.sltnButton.setShortcut(QCoreApplication.translate("MainWindow", "Alt+S"))
        self.stpwButton.setShortcut(QCoreApplication.translate("MainWindow", "Alt+X"))
        self.unsetButton.setShortcut(QCoreApplication.translate("MainWindow", "Alt+Shift+X"))

        notesShortCut = qw.QShortcut(QKeySequence("Alt+N"), self)
        notesShortCut.activated.connect(lambda: self.editing_mode(self.notesTextEdit))

        aliasShortCut = qw.QShortcut(QKeySequence("Alt+A"), self)
        aliasShortCut.activated.connect(lambda: self.editing_mode(self.aliasEdit))

    def editing_mode(self, field):
        field.setFocus()
        field.selectAll()


if __name__ == "__main__":
    app = qw.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())

