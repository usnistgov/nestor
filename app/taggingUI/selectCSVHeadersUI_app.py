import sys
import csv
import PyQt5.QtWidgets as Qw
from PyQt5 import QtCore as Qc
from app.taggingUI.selectCSVHeadersUI_skeleton import Ui_MainWindow_selectCSVHeaders


class MySelectCsvHeadersWindow(Qw.QMainWindow, Ui_MainWindow_selectCSVHeaders):

    def __init__(self, filePath_OriginalCSV= None):
        Qw.QMainWindow.__init__(self)
        self.setupUi(self)
        self.csvHeader = self.set_CSVHeader(filePath_OriginalCSV)

        self.buttonGroup_CSVHeaders = Qw.QButtonGroup()
        self.buttonGroup_CSVHeaders.setExclusive(False)

        self.pushButton_selectCSVHeaders_uncheckAll.clicked.connect(
            lambda: self.onClick_check(False))
        self.pushButton_selectCSVHeaders_checkAll.clicked.connect(
            lambda: self.onClick_check(True))

        #self.init_selectHeaderView()


    def set_CSVHeader(self, filePath_OriginalCSV):
        """
        read the header of the CSV
        Set to the class a list with the header of it
        This list is used in the method init_selectHeaderView to create the checkboxes
        :param filePath_OriginalCSV:
        :return:
        """
        if filePath_OriginalCSV:
            with open(filePath_OriginalCSV, "rt") as csvfile:
                reader = csv.reader(csvfile)
                self.headers = next(reader)


    def init_selectHeaderView(self):
        """
        create the list of checkbox based on the header attribute
        the header is created using the method set_CSVHeader
        :return:
        """

        y_headerColumn = 0
        x = 0

        self.label_selectCSVHeaders_headerColumn = Qw.QLabel(self.centralwidget)
        self.label_selectCSVHeaders_headerColumn.setObjectName("label_selectCSVHeaders_headerColumn")
        self.label_selectCSVHeaders_headerColumn.setText("Your CSV header\n(check if you want to tag it)")
        self.gridLayout_selectCSVHeaders_editor.addWidget(self.label_selectCSVHeaders_headerColumn, x,y_headerColumn,1,1 )

        x += 1

        self.line1 = Qw.QFrame(self.centralwidget)
        self.line1.setFrameShape(Qw.QFrame.HLine)
        self.line1.setFrameShadow(Qw.QFrame.Sunken)
        self.line1.setObjectName("line1")
        self.gridLayout_selectCSVHeaders_editor.addWidget(self.line1, x,y_headerColumn , 1, 1)


        for header in self.headers:
            x += 1

            checkBox = Qw.QCheckBox(self.centralwidget)
            checkBox.setObjectName(f'checkBox_{header}')
            checkBox.setText(header)
            self.gridLayout_selectCSVHeaders_editor.addWidget(checkBox, x, y_headerColumn, 1, 1)
            self.buttonGroup_CSVHeaders.addButton(checkBox)

    def onClick_check(self, check):
        """
        called when we want to set the checkbox to check:True of uncheck:False
        :param check: True: check/ False:uncheck
        :return:
        """
        for button in self.buttonGroup_CSVHeaders.buttons():
            button.setChecked(check)

    def get_buttonChecked(self):
        """
        Action when saving the check box information
        if none are selected it create a messageBox
        after saving we open the tagging UI
        :return:
        """
        self.list_header_rawText= []
        for button in self.buttonGroup_CSVHeaders.buttons():
            if button.isChecked():
                self.list_header_rawText.append(button.text())

        if self.list_header_rawText:
            return True, self.list_header_rawText
        else:
            Qw.QMessageBox.about(self, 'Can\'t save', "You might want to select at least 1 value")
            return False, None




if __name__ == "__main__":
    app = Qw.QApplication(sys.argv)
    window = MySelectCsvHeadersWindow("/Users/sam11/Git/ml-py/app/taggingUI/csv/app_vocab.csv")
    window.show()
    sys.exit(app.exec_())