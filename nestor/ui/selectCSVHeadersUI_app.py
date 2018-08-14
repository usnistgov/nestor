
import sys
from pathlib import Path
from PyQt5.QtCore import QCoreApplication, Qt, QSize
from PyQt5 import QtGui, uic
import PyQt5.QtWidgets as Qw

import collections

# from sympy.core.tests.test_arit import same_and_same_prec

fname = 'selectCSVHeadersUI.ui'
script_dir = Path(__file__).parent
# qtDesignerFile_selectCSVHeaders = Path('nestor/_ui')/fname
Ui_MainWindow_selectCSVHeaders, QtBaseClass_selectCSVHeaders = uic.loadUiType(script_dir/fname)


class MySelectCsvHeadersWindow(Qw.QMainWindow, Ui_MainWindow_selectCSVHeaders):

    def __init__(self, iconPath= None, closeFunction=None, nextWindow=None):
        Qw.QMainWindow.__init__(self)
        Ui_MainWindow_selectCSVHeaders.__init__(self)
        self.setupUi(self)
        self.setGeometry(20, 20, 300, 350)
        self.closeFunction = closeFunction
        self.nextWindowFunction = nextWindow

        if iconPath:
            self.setWindowIcon(QtGui.QIcon(iconPath))

        self.buttonGroup_CSVHeaders_Checkbox = Qw.QButtonGroup()
        self.buttonGroup_CSVHeaders_Checkbox.setExclusive(False)

        self.list_Combobox = []
        self.defaultCBValue = "Not Applicable"
        self.csvHeaderMapping = None

        self.config_csvHeader={}

        self.pushButton_selectCSVHeaders_uncheckAll.clicked.connect(
            lambda: self.onClick_check(False))
        self.pushButton_selectCSVHeaders_checkAll.clicked.connect(
            lambda: self.onClick_check(True))

        self.pushButton_selectCSVHeaders_save.clicked.connect(self.nextWindowFunction)

    def set_checkBoxesValues(self, headers):
        """create the list of checkbox based on the header attribute
        the header is created using the method set_CSVHeader
        :return:

        Parameters
        ----------
        headers :
            

        Returns
        -------

        """
        self.headers = headers
        y_headerColumn = 0
        x = 0

        self.line1 = Qw.QFrame(self.centralwidget)
        self.line1.setFrameShape(Qw.QFrame.HLine)
        self.line1.setFrameShadow(Qw.QFrame.Sunken)
        self.line1.setObjectName("line1")
        self.gridLayout_selectCSVHeaders_editor.addWidget(self.line1, x,y_headerColumn , 1, 1)

        for header in self.headers:
            x += 1

            #create the checkboxes
            checkBox = Qw.QCheckBox(self.centralwidget)
            checkBox.setObjectName(f'checkBox_{header}')
            checkBox.setText(header)
            self.gridLayout_selectCSVHeaders_editor.addWidget(checkBox, x, y_headerColumn, 1, 1)
            self.buttonGroup_CSVHeaders_Checkbox.addButton(checkBox)

            #reate the dropdownmenu
            comboBox = Qw.QComboBox(self.centralwidget)
            comboBox.setObjectName(f'{header}')
            self.gridLayout_selectCSVHeaders_editor.addWidget(comboBox, x, y_headerColumn +1, 1, 1)
            self.list_Combobox.append(comboBox)

    def onClick_check(self, check):
        """called when we want to set the checkbox to check:True of uncheck:False

        Parameters
        ----------
        check :
            True: check/ False:uncheck

        Returns
        -------

        """
        for button in self.buttonGroup_CSVHeaders_Checkbox.buttons():
            button.setChecked(check)


    def get_checkedButton(self):
        """

        Parameters
        ----------

        Returns
        -------
        type
            :return:

        """
        checked = []
        for button in self.buttonGroup_CSVHeaders_Checkbox.buttons():
            if button.isChecked():
                checked.append(button.text())
        return checked

    def get_csvheader(self):
        """
            update the csvHeaderMapping based on the dropdown menu on the right of the app

        Parameters
        ----------

        Returns
        -------

        """

        dict = {}

        for button in self.list_Combobox:

            if button.currentText() != self.defaultCBValue:

                dict[button.objectName()] = button.currentText()

        return dict



    def set_config(self, config, csvHeaderMapping):
        """add to the window the values from the config dict

        Parameters
        ----------
        config :
            return:

        Returns
        -------

        """
        list_combobox=[self.defaultCBValue]
        for k,values in csvHeaderMapping.items():
            for k2,value2 in values.items():
                list_combobox.append(value2)


        if config['file']['filePath_OriginalCSV']['headers'] is not None:
            for button in self.buttonGroup_CSVHeaders_Checkbox.buttons():
                if button.text() in config['file']['filePath_OriginalCSV']['headers']:
                    button.setChecked(True)

        config_csvHeader =  config.get("csvheader_mapping", None)
        for comboBox in self.list_Combobox:
            comboBox.addItems(list_combobox)

            if config_csvHeader:
                comboBox.setCurrentText(config_csvHeader.get(comboBox.objectName(), self.defaultCBValue))


    def get_config(self, config):
        """replace the given config dict with a new one based on the window values
        
        it is call when we save the view

        Parameters
        ----------
        config :
            return:

        Returns
        -------

        """


        checked = []
        for button in self.buttonGroup_CSVHeaders_Checkbox.buttons():
            if button.isChecked():
                checked.append(button.text())

        if checked:
            config['file']['filePath_OriginalCSV']['headers'] = checked

            # update the config to contains the mapping between the csv header and the data type
            dict = self.get_csvheader()
            config["csvheader_mapping"] = dict


            return True, config
        else:
            Qw.QMessageBox.about(self, 'Can\'t save', "You might want to select at least 1 value")
            return False, None

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
            self.nextWindowFunction()

