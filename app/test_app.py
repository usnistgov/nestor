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

        self.clf_mapper = {
            'S': self.sltnButton,
            'P': self.probButton,
            'I': self.itemButton,
            'X': self.stpwButton,
            'U': self.unknButton
        }

    # def loadCsv(self, fileName):
    #     with open(fileName, "rt") as fileInput:
    #         for row in csv.reader(fileInput):
    #             items = [
    #                 QStandardItem(field)
    #                 for field in row
    #             ]
    #             self.model.appendRow(items)


    def file_open(self):
        fileName, _ = qw.QFileDialog.getOpenFileName(self, 'Open File')
        self.csv_to_tab(fileName)
        # self.loadCsv(fileName)


    # def writeCsv(self, fileName):
    #     with open(fileName, "wt") as fileOutput:
    #         writer = csv.writer(fileOutput)
    #         for rowNumber in range(self.model.rowCount()):
    #             fields = [
    #                 self.model.data(
    #                     self.model.index(rowNumber, columnNumber),
    #                     Qt.DisplayRole
    #                 )
    #                 for columnNumber in range(self.model.columnCount())
    #             ]
    #             writer.writerow(fields)

    def file_save(self):
        fileName, _ = qw.QFileDialog.getOpenFileName(self, 'Save File')


        # self.writeCsv(fileName)

    def extract_row_info(self):
        items = self.vocabTableWidget.selectedItems()
        tok, clf, alias, notes = (str(i.text()) for i in items)
        print(tok)

        if clf in self.clf_mapper.keys():

            self.aliasEdit.setText(alias)

            # print([])
            # self.aliasEdit.setText(items[0])

            btn = self.clf_mapper[clf]
            btn.toggle()
            self.notesTextEdit.setText(notes)

    def csv_to_tab(self, filename):
        df = pd.read_csv(filename, header=0)  # read file and set header row
        df[df['NE'].notna()]['alias'].fillna(df[df['NE'].notna()]['token'])

        self.vocabTableWidget.setColumnCount(len(df.columns))
        self.vocabTableWidget.setRowCount(len(df.index))

        for i in range(len(df.index)):
            for j in range(len(df.columns)):
                self.vocabTableWidget.setItem(i, j, qw.QTableWidgetItem(str(df.iat[i, j])))

        self.vocabTableWidget.resizeColumnsToContents()
        self.vocabTableWidget.resizeRowsToContents()
        self.vocabTableWidget.setHorizontalHeaderLabels(df.columns.tolist())
        self.vocabTableWidget.setSelectionBehavior(qw.QTableWidget.SelectRows)

        completed_pct = int(100*df[df['NE'].notna()].shape[0]/df.shape[0])
        self.progressBar.setValue(completed_pct)


if __name__ == "__main__":
    app = qw.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())