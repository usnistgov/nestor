import sys
from PyQt5.QtCore import QCoreApplication, Qt, QSize
from PyQt5.QtGui import *
import PyQt5.QtWidgets as Qw
import csv
import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)
import pandas as pd
from test_skeleton import Ui_MainWindow
from fuzzywuzzy import process as zz


class MyQButtonGroup(Qw.QButtonGroup):

    def __init__(self, layout):
        super(MyQButtonGroup, self).__init__()
        self.setExclusive(False)
        self.layout = layout

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
            btn = Qw.QCheckBox(f'{n} - ' + match)
            cond = (df.loc[match, 'alias'] == df.loc[tok, 'alias']) \
                   and (df.loc[match, 'alias'] != '')
            if (match == tok) or cond:
                btn.toggle()
            self.addButton(btn)
            self.layout.insertWidget(self.layout.count() - nbr_widget, btn)

    def set_shortcut(self):
        """
        Create the shorcut for all the checkbox
        """

        for n, btn in enumerate(self.buttons()):
            btn.setShortcut(f'Alt+{n}')

class MyQTableWidget(Qw.QTableWidget):

    def __init__(self, Qwidget, window):
        super(MyQTableWidget, self).__init__(Qwidget)

        sizePolicy = Qw.QSizePolicy(Qw.QSizePolicy.Expanding, Qw.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())

        self.setSizePolicy(sizePolicy)
        self.setMaximumSize(QSize(16777215, 16777215))
        self.setEditTriggers(Qw.QAbstractItemView.EditKeyPressed)
        self.setTabKeyNavigation(False)
        self.setDragDropOverwriteMode(False)
        self.setSelectionMode(Qw.QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(Qw.QAbstractItemView.SelectRows)
        self.setObjectName("vocabTableWidget")
        self.setColumnCount(0)
        self.setRowCount(0)
        self.setFocus()

    def print_table(self, df, vocab_limit=1000):
        temp_df = df.reset_index()
        nrows, ncols = temp_df.shape
        self.setColumnCount(ncols)
        self.setRowCount(min([nrows, vocab_limit]))

        for i in range(self.rowCount()):
            for j in range(ncols):
                self.setItem(i, j, Qw.QTableWidgetItem(str(temp_df.iat[i, j])))

        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        self.setHorizontalHeaderLabels(temp_df.columns.tolist())
        self.setSelectionBehavior(Qw.QTableWidget.SelectRows)


    # def extract_row_info(self, window):
    #     items = self.selectedItems()  # selected row
    #     tok, clf, alias, notes = (str(i.text()) for i in items)
    #     if alias is not '':
    #         window.aliasEdit.setText(alias)  # preferred alias
    #     else:
    #         window.aliasEdit.setText(tok)  # Default to tok
    #     # btn = self.clf_mapper[clf]  # which button?
    #     btn = window.clf_mapper.get(clf, window.unsetButton)
    #     btn.toggle()  # toggle that button
    #     window.notesTextEdit.setText(notes)  # show any notes
    #
    #     matches = zz.extractBests(tok, window.df.index.tolist(),
    #                               limit=10, score_cutoff=window.thres)
    #
    #     window.vertCheckButtonGroup.update_checkboxes(tok, matches, window.df)


class MyWindow(Qw.QMainWindow, Ui_MainWindow):

    def __init__(self):
        Qw.QMainWindow.__init__(self)
        self.setupUi(self)
        self.set_menu()

        self.actionExit.triggered.connect(self.close_application)

        self.vocabTableWidget = MyQTableWidget(self.centralwidget, self)
        self.gridLayout.addWidget(self.vocabTableWidget, 1, 2, 1, 1)
        self.vocabTableWidget.itemSelectionChanged.connect(self.table_item_selected)

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

        self.updateButton.clicked.connect(self.update_from_input)

        self.vertCheckButtonGroup = MyQButtonGroup(self.vertCheckBoxLayout)

        self.set_shortcut()

    def set_dataframe(self, filename):
        self.df = pd.read_csv(filename, header=0, index_col=0)  # read file and set header row
        mask = self.df['NE'].notna()
        print(self.df.shape, self.df[mask].shape)
        self.df.loc[mask, 'alias'].fillna(self.df[mask].index.to_series(), inplace=True)
        self.df.fillna('', inplace=True)
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

        matches = zz.extractBests(tok, self.df.index.tolist(),
                                  limit=10, score_cutoff=self.thres)

        self.vertCheckButtonGroup.update_checkboxes(tok, matches, window.df)

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
            s = btn.text()[4:]
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
        print(new_clf, new_alias, new_notes)

        self.update_progress_bar()

    def update_progress_bar(self):
         completed_pct = int(100 * self.df[self.df['NE'] != ''].shape[0] / self.df.shape[0])
         self.progressBar.setValue(completed_pct)

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

