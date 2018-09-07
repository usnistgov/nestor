from pathlib import Path
from PyQt5 import QtGui, uic
import PyQt5.QtWidgets as Qw

import pyaml, yaml

#from nestor.ui.taggingUI_app import openYAMLConfig_File



script_dir = Path(__file__).parent

fname_newproject = 'dialogmenu_newproject.ui'
qtDesignerFile_newproject = script_dir/fname_newproject
Ui_MainWindow_newproject, QtBaseClass_newproject = uic.loadUiType(qtDesignerFile_newproject)

class DialogMenu_newProject(Qw.QDialog, Ui_MainWindow_newproject):
    """
    Class used to create a new project
    """
    def __init__(self, iconPath=None):
        Qw.QDialog.__init__(self)
        Ui_MainWindow_newproject.__init__(self)
        self.setupUi(self)

        if iconPath:
            self.setWindowIcon(QtGui.QIcon(iconPath))

        self.pushButton_NewProject_LoadCSV.clicked.connect(self.onClick_loadCSV)
        self.buttonBox__NewProject.rejected.connect(self.close)
        self.show()


    def get_data(self):
        """
        return the needed data from the dialog
        :return:
        """
        return  self.lineEdit_NewProject_ProjectName.text(),\
                self.lineEdit_NewProject_ProjectAuthor.text(),\
                self.textEdit_NewProject_ProjectDescription.toPlainText(),\
                self.lineEdit_NewProject_Project1gVocabName.text(),\
                self.lineEdit_NewProject_ProjectNgVocabName.text(),\
                self.lineEdit_NewProject_LoadCSV.text()


    def onClick_loadCSV(self):
        """
        open a dialog to search a csv file
        :return:
        """
        options = Qw.QFileDialog.Options()
        fileName, _ = Qw.QFileDialog.getOpenFileName(self, None, "Open CSV file",
                                                     "CSV File (*.csv)", options=options)
        if fileName:
            self.lineEdit_NewProject_LoadCSV.setText(fileName)



fname_loadproject = 'dialogmenu_loadproject.ui'
qtDesignerFile_loadproject = script_dir / fname_loadproject
Ui_MainWindow_loadproject, QtBaseClass_loadproject = uic.loadUiType(qtDesignerFile_loadproject)

class DialogMenu_loadProject(Qw.QDialog, Ui_MainWindow_loadproject):
    """
    Class use to load an existing project
    """
    def __init__(self, iconPath=None, projectPath=None, existingProject=None):
        Qw.QDialog.__init__(self)
        Ui_MainWindow_loadproject.__init__(self)
        self.setupUi(self)

        self.projectPath = projectPath
        self.comboBox_LoadProject_ProjectName.addItems(existingProject)
        self.set_values()

        if iconPath:
            self.setWindowIcon(QtGui.QIcon(iconPath))

        self.buttonBox_LoadProject.rejected.connect(self.close)
        self.comboBox_LoadProject_ProjectName.currentTextChanged.connect(self.set_values)

        self.show()

    def get_data(self):
        """
        return the needed data
        :return:
        """
        return self.generalConfig.get(self.comboBox_LoadProject_ProjectName.currentText())


    def set_values(self):
        """
        set the data when selecting a project in the combobox
        :return:
        """
        currentProject = self.comboBox_LoadProject_ProjectName.currentText()

        tmpConf = openYAMLConfig_File( self.projectPath / currentProject / "config.yaml")

        self.lineEdit_LoadProject_ProjectAuthor.setText(tmpConf.get('author',''))
        self.textEdit_LoadProject_ProjectDescription.setText(tmpConf.get('description',''))


fname_settings = 'dialogmenu_settings.ui'
qtDesignerFile_settings = script_dir / fname_settings
Ui_MainWindow_settings, QtBaseClass_settings = uic.loadUiType(qtDesignerFile_settings)

class DialogMenu_settings(Qw.QDialog, Ui_MainWindow_settings):
    """
    Class used to change the settings
    """
    def __init__(self, iconPath=None, configSettings = None, untracked= ""):
        Qw.QDialog.__init__(self)
        Ui_MainWindow_settings.__init__(self)
        self.setupUi(self)

        self.lineEdit_Setup_NumberToken.setInputMask("9999")
        self.lineEdit_Setup_TokenChecked.setInputMask("99")
        self.lineEdit_Setup_TokenShow.setInputMask("99")

        if configSettings:
            self.lineEdit_Setup_NumberToken.setText(str(configSettings.get('numberTokens','1000')))
            self.lineEdit_Setup_TokenChecked.setText(str(configSettings.get('alreadyChecked_threshold','99')))
            self.lineEdit_Setup_TokenShow.setText(str(configSettings.get('showCkeckBox_threshold','50')))
        else:
            self.lineEdit_Setup_NumberToken.setText('1000')
            self.lineEdit_Setup_TokenChecked.setText('99')
            self.lineEdit_Setup_TokenShow.setText('50')

        self.textEdit_Setup_UntrackedToken.setPlainText(untracked)

        if iconPath:
            self.setWindowIcon(QtGui.QIcon(iconPath))

        self.buttonBox_Setup.rejected.connect(self.close)

        self.show()

    def get_data(self):
        """
        Return the needed data
        :return:
        """
        return  int(self.lineEdit_Setup_NumberToken.text()),\
                int(self.lineEdit_Setup_TokenChecked.text()),\
                int(self.lineEdit_Setup_TokenShow.text()), \
                [word.lstrip() for word in self.textEdit_Setup_UntrackedToken.toPlainText().split(";")]


fname_tou = 'termsOfUse.ui'
qtDesignerFile_tou = script_dir/fname_tou
Ui_MainWindow_tou, QtBaseClass_tou = uic.loadUiType(qtDesignerFile_tou)

class DialogMenu_TermsOfUse(Qw.QDialog, Ui_MainWindow_tou):
    """
    class used to print the Term of Use
    """

    def __init__(self, iconPath=None):
        Qw.QDialog.__init__(self)
        Ui_MainWindow_tou.__init__(self)
        self.setupUi(self)

        if iconPath:
            self.setWindowIcon(QtGui.QIcon(iconPath))


fname_csvHeader = 'dialogMenu_csvheadermapping.ui'
qtDesignerFile_csvHeader = script_dir / fname_csvHeader
Ui_MainWindow_csvHeader, QtBaseClass_csvHeader = uic.loadUiType(qtDesignerFile_csvHeader)

class DialogMenu_csvHeaderMapping(Qw.QDialog, Ui_MainWindow_csvHeader):
    """
    Class use when mapping the Csv and settup thoses csv information
    """

    def __init__(self, iconPath=None, csvHeaderContent=[], mappingContent=[], configCsvHeader=[] , configMapping={}):
        Qw.QDialog.__init__(self)
        Ui_MainWindow_csvHeader.__init__(self)
        self.setupUi(self)

        self.mappingContent = mappingContent
        self.csvHeaderContent = csvHeaderContent
        self.configMapping=configMapping
        self.configCsvHeader = configCsvHeader

        if iconPath:
            self.setWindowIcon(QtGui.QIcon(iconPath))

        self.buttonGroup_CSVHeaders_Checkbox = Qw.QButtonGroup()
        self.buttonGroup_CSVHeaders_Checkbox.setExclusive(False)

        self.list_Combobox = []
        self.defaultCBValue = "Not Applicable"
        self.mappingContent.insert(0, self.defaultCBValue)
        self.buttonBox_csvHeaderMapping.rejected.connect(self.close)

        self.set_interface()
        self.set_content()

        self.show()


    def set_interface(self):
        """
        set the interface check and comboBox
        :return:
        """
        currentPos = 0
        boxPos = 0
        mapPos = boxPos + 1


        for header in self.csvHeaderContent:

            checkBox = Qw.QCheckBox(self.scrollAreaWidgetContents)
            checkBox.setObjectName(f'checkBox_{header}')
            checkBox.setText(header)
            self.gridLayout__csvHeaderMapping_content.addWidget(checkBox, currentPos, boxPos, 1, 1)
            self.buttonGroup_CSVHeaders_Checkbox.addButton(checkBox)

            comboBox = Qw.QComboBox(self.scrollAreaWidgetContents)
            comboBox.setObjectName(f'{header}')
            comboBox.addItems(self.mappingContent)
            self.gridLayout__csvHeaderMapping_content.addWidget(comboBox, currentPos, mapPos, 1, 1)
            self.list_Combobox.append(comboBox)

            currentPos +=1

    def set_content(self):
        """
        trigger the check and combo box based on the config file
        :return:
        """

        for boxChecked in self.buttonGroup_CSVHeaders_Checkbox.buttons():

            if boxChecked.text() in self.configCsvHeader:
                boxChecked.setChecked(True)

        for comboBox in self.list_Combobox:
            comboBox.setCurrentText(self.configMapping.get(comboBox.objectName(), self.defaultCBValue))

    def get_data(self):
        """
        return the needed data
        :return:
        """

        listBoxChecked = []
        map = {}

        for boxChecked in self.buttonGroup_CSVHeaders_Checkbox.buttons():

            #get list of button checked
            if boxChecked.isChecked():
                listBoxChecked.append(boxChecked.text())

            for comboButton in self.list_Combobox:
                if comboButton.objectName() == boxChecked.text() and comboButton.currentText() != self.defaultCBValue:
                    map[boxChecked.text()] = comboButton.currentText()

        return listBoxChecked, map

fname_dbconnect = 'dialogmenu_databaseconnect.ui'
qtDesignerFile_dbconnect = script_dir / fname_dbconnect
Ui_MainWindow_dbconnect, QtBaseClass_dbconnect = uic.loadUiType(qtDesignerFile_dbconnect)

class DialogMenu_DatabaseConnect(Qw.QDialog, Ui_MainWindow_dbconnect):
    """
    class used to print the Term of Use
    """

    def __init__(self, iconPath=None, configDatabase={}):
        Qw.QDialog.__init__(self)
        Ui_MainWindow_dbconnect.__init__(self)
        self.setupUi(self)

        if iconPath:
            self.setWindowIcon(QtGui.QIcon(iconPath))

        self.lineEdit_DialogDatabaseConnection_Username.setText(configDatabase.get("username",""))
        self.lineEdit_DialogDatabaseConnection_OpenSchema.setText(configDatabase.get("schema",""))
        self.lineEdit_DialogDatabaseConnection_ServerName.setText(configDatabase.get("server",""))
        self.lineEdit_DialogDatabaseConnection_ServerPortNumber.setText(configDatabase.get("serverport",""))
        self.lineEdit_DialogDatabaseConnection_BrowserPortNumber.setText(configDatabase.get("browserport",""))

        self.buttonBox_DialogDatabaseConnection.rejected.connect(self.close)

        self.show()

    def get_data(self):
        """
        return the needed data
        :return:
        """
        return self.lineEdit_DialogDatabaseConnection_Username.text(), \
               self.lineEdit_DialogDatabaseConnection_OpenSchema.text(),\
               self.lineEdit_DialogDatabaseConnection_ServerName.text(), \
               self.lineEdit_DialogDatabaseConnection_ServerPortNumber.text(), \
               self.lineEdit_DialogDatabaseConnection_BrowserPortNumber.text(), \
               self.lineEdit_DialogDatabaseConnection_Password.text()

            # fname3 = 'dialogWait.ui'
# Ui_MainWindow_DialogWait, QtBaseClass_DialogWait = uic.loadUiType(script_dir/fname3)
# class DialogWait(Qw.QDialog, Ui_MainWindow_DialogWait):
#
#     def __init__(self, iconPath=None):
#         Qw.QDialog.__init__(self)
#         Ui_MainWindow_DialogWait.__init__(self)
#         self.setupUi(self)
#         self.progressBar_DialogWait.setValue(0)
#         self.setWindowFlags(Qt.WindowStaysOnTopHint)
#
#         if iconPath:
#             self.setWindowIcon(QtGui.QIcon(iconPath))
#
#     def setProgress(self, value):
#         self.progressBar_DialogWait.setValue(value)



def openYAMLConfig_File(yaml_path, dict={}):
    """open a Yaml file based on the given path
    :return: a dictionary

    Parameters
    ----------
    yaml_path :

    dict :
         (Default value = None)

    Returns
    -------

    """
    if yaml_path.is_file():
        with open(yaml_path, 'r') as yamlfile:
            config = yaml.load(yamlfile)
            print("OPEN --> YAML file at: ", yaml_path)
            if not config:
                config = {}
    else:
        config = dict
        with open(yaml_path, 'w') as yamlfile:
            pyaml.dump(config, yamlfile)
            print("CREATE --> YAML file at: ", yaml_path)
    return config