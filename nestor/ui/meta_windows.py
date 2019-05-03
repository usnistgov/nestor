__author__ = 'Sascha Moccozet'

from pathlib import Path
from PyQt5 import uic
import PyQt5.QtGui as Qg
import PyQt5.QtWidgets as Qw
from PyQt5.QtCore import Qt
from nestor.store_data import integration as cypherQuery

import pyaml, yaml

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
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        if iconPath:
            self.setWindowIcon(Qg.QIcon(iconPath))

        self.pushButton_NewProject_LoadCSV.clicked.connect(self.onClick_loadCSV)
        self.buttonBox__NewProject.rejected.connect(self.close)
        self.show()

    def get_data(self):
        """
        return the needed data from the dialog
        :return:
        """
        return self.lineEdit_NewProject_ProjectName.text(),\
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


fname_openproject = 'dialogmenu_openproject.ui'
qtDesignerFile_openproject = script_dir / fname_openproject
Ui_MainWindow_openproject, QtBaseClass_openproject = uic.loadUiType(qtDesignerFile_openproject)


class DialogMenu_openProject(Qw.QDialog, Ui_MainWindow_openproject):
    """
    Class use to load an existing project
    """
    def __init__(self, iconPath=None, projectPath=None, existingProject=None):
        Qw.QDialog.__init__(self)
        Ui_MainWindow_openproject.__init__(self)
        self.setupUi(self)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.projectPath = projectPath
        self.comboBox_OpenProject_ProjectName.addItems(existingProject)
        self.set_values()

        if iconPath:
            self.setWindowIcon(Qg.QIcon(iconPath))

        self.buttonBox_OpenProject.rejected.connect(self.close)
        self.comboBox_OpenProject_ProjectName.currentTextChanged.connect(self.set_values)

        self.show()

    def get_data(self):
        """
        return the needed data
        :return:
        """
        yaml_path = self.projectPath / self.comboBox_OpenProject_ProjectName.currentText() /'config.yaml'
        return openYAMLConfig_File(yaml_path)

    def set_values(self):
        """
        set the data when selecting a project in the combobox
        :return:
        """
        currentProject = self.comboBox_OpenProject_ProjectName.currentText()

        if currentProject:
            tmpConf = openYAMLConfig_File( self.projectPath / currentProject / "config.yaml")
            self.lineEdit_OpenProject_CSVName.setText(tmpConf.get('original',''))
            self.lineEdit_OpenProject_ProjectAuthor.setText(tmpConf.get('author',''))
            self.textEdit_OpenProject_ProjectDescription.setText(tmpConf.get('description',''))


fname_settings = 'dialogmenu_settings.ui'
qtDesignerFile_settings = script_dir / fname_settings
Ui_MainWindow_settings, QtBaseClass_settings = uic.loadUiType(qtDesignerFile_settings)

class DialogMenu_settings(Qw.QDialog, Ui_MainWindow_settings):
    """
    Class used to change the settings
    """
    def __init__(self, iconPath=None, name=None, author=None, description=None, vocab1g=None, vocabNg=None,
                 configSettings = None):
        Qw.QDialog.__init__(self)
        Ui_MainWindow_settings.__init__(self)
        self.setupUi(self)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.lineEdit_Setup_NumberToken.setInputMask("9999")
        self.lineEdit_Setup_TokenChecked.setInputMask("99")
        self.lineEdit_Setup_TokenShow.setInputMask("99")

        self.lineEdit_Settings_ProjectName.setText(name)
        self.lineEdit_Settings_ProjectAuthor.setText(author)
        self.textEdit_Settings_ProjectDescription.setPlainText(description)
        self.lineEdit_Settings_Project1gVocabName.setText(vocab1g)
        self.lineEdit_Settings_ProjectNgVocabName.setText(vocabNg)


        if configSettings:
            self.lineEdit_Setup_NumberToken.setText(str(configSettings.get('numberTokens','1000')))
            self.lineEdit_Setup_TokenChecked.setText(str(configSettings.get('alreadyChecked_threshold','99')))
            self.lineEdit_Setup_TokenShow.setText(str(configSettings.get('showCkeckBox_threshold','50')))
        else:
            self.lineEdit_Setup_NumberToken.setText('1000')
            self.lineEdit_Setup_TokenChecked.setText('99')
            self.lineEdit_Setup_TokenShow.setText('50')



        if iconPath:
            self.setWindowIcon(Qg.QIcon(iconPath))

        self.buttonBox_Setup.rejected.connect(self.close)

        self.show()

    def get_data(self):
        """
        Return the needed data
        :return:
        """

        return  self.lineEdit_Settings_ProjectName.text(),\
                self.lineEdit_Settings_ProjectAuthor.text(),\
                self.textEdit_Settings_ProjectDescription.toPlainText(), \
                self.lineEdit_Settings_Project1gVocabName.text(), \
                self.lineEdit_Settings_ProjectNgVocabName.text(),\
                int(self.lineEdit_Setup_NumberToken.text()) if self.lineEdit_Setup_NumberToken.text() else 1000,\
                int(self.lineEdit_Setup_TokenChecked.text()) if self.lineEdit_Setup_TokenChecked.text() else 99,\
                int(self.lineEdit_Setup_TokenShow.text()) if self.lineEdit_Setup_TokenShow.text() else 50

fname_tou = 'dialogmenu_termsofuse.ui'
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
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        if iconPath:
            self.setWindowIcon(Qg.QIcon(iconPath))


fname_csvHeader = 'dialogmenu_csvheadermapping.ui'
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
        self.setWindowFlags(Qt.WindowStaysOnTopHint)


        self.mappingContent = mappingContent
        self.csvHeaderContent = csvHeaderContent
        self.configMapping = configMapping
        self.configCsvHeader = configCsvHeader

        if iconPath:
            self.setWindowIcon(Qg.QIcon(iconPath))

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
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        if iconPath:
            self.setWindowIcon(Qg.QIcon(iconPath))

        self.lineEdit_DialogDatabaseConnection_Username.setText(configDatabase.get("username",""))
        self.lineEdit_DialogDatabaseConnection_OpenSchema.setText(configDatabase.get("schema",""))
        self.lineEdit_DialogDatabaseConnection_ServerName.setText(configDatabase.get("server",""))
        self.lineEdit_DialogDatabaseConnection_ServerPortNumber.setText(str(configDatabase.get("serverport","")))
        self.lineEdit_DialogDatabaseConnection_BrowserPortNumber.setText(str(configDatabase.get("browserport","")))

        self.pushButton_DialogDatabaseConnection_OpenSchema.clicked.connect(self.onclick_openSchema)
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

    def onclick_openSchema(self):

        options = Qw.QFileDialog.Options()
        fileName, _ = Qw.QFileDialog.getOpenFileName(self, None, "Open database Header file",
                                                     "YAML File (*.yaml)", options=options)
        if fileName:
            self.lineEdit_DialogDatabaseConnection_OpenSchema.setText(fileName)


            # fname3 = 'dialog_wait.ui'


fname_dbrunquery = 'dialogmenu_databaserunqueries.ui'
qtDesignerFile_dbrunquery = script_dir / fname_dbrunquery
Ui_MainWindow_dbrunquery, QtBaseClass_dbrunquery = uic.loadUiType(qtDesignerFile_dbrunquery)


class DialogMenu_DatabaseRunQueries(Qw.QDialog, Ui_MainWindow_dbrunquery):
    """
    class used to print the Term of Use
    """

    def __init__(self, iconPath=None, database=None, dataframe_Original=None, dataframe_vocab1Gram=None,
                 dataframe_vocabNGram= None, bin1g_df=None, binNg_df=None, vocab1g_df=None, vocabNg_df=None,
                 csvHeaderMapping=None, databaseToCsv_mapping=None):
        Qw.QDialog.__init__(self)
        Ui_MainWindow_dbrunquery.__init__(self)
        self.setupUi(self)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.database = database
        self.dataframe_Original = dataframe_Original
        self.dataframe_vocab1Gram = dataframe_vocab1Gram
        self.dataframe_vocabNGram = dataframe_vocabNGram
        self.bin1g_df = bin1g_df
        self.binNg_df = binNg_df
        self.vocab1g_df = vocab1g_df
        self.vocabNg_df = vocabNg_df

        self.iconPath = iconPath
        if iconPath:
            self.setWindowIcon(Qg.QIcon(iconPath))

        if csvHeaderMapping :
            # change the csvHeaderOriginal to match with the given csv header
            for key1, value1 in databaseToCsv_mapping.items():
                for key2, value2 in value1.items():
                    for keyO, valueO in csvHeaderMapping.items():
                        if valueO == value2:
                            databaseToCsv_mapping[key1][key2] = keyO

            self.csv_header = databaseToCsv_mapping
        else:
            self.csv_header = None

        self.button_DialogDatabaseRunQuery.rejected.connect(self.close)
        self.pushButton_DialogDatabaseRunQuery_RemoveData.clicked.connect(self.onClick_removeData)

        self.checkBox_DialogDatabaseRunQuery_OriginalData.clicked.connect(self.check_checkBoxGroup)
        self.checkBox_DialogDatabaseRunQuery_Tag1g.clicked.connect(self.check_checkBoxGroup)
        self.checkBox_DialogDatabaseRunQuery_TagNg.clicked.connect(self.check_checkBoxGroup)
        self.checkBox_DialogDatabaseRunQuery_1gToNg.clicked.connect(self.check_checkBoxGroup)
        self.checkBox_DialogDatabaseRunQuery_IssueToItem.clicked.connect(self.check_checkBoxGroup)
        self.checkBox_DialogDatabaseRunQuery_ItemToItem.clicked.connect(self.check_checkBoxGroup)

        self.check_checkBoxGroup()

        self.show()

    def runQueries(self):

        self.setEnabled(False)


        window_DialogWait = DialogWait(iconPath=self.iconPath)
        rect = self.geometry()
        rect.setHeight(300)
        rect.setWidth(200)
        window_DialogWait.setGeometry(rect)

        window_DialogWait.show()
        window_DialogWait.setProgress(0)


        self.database.dropConstraints()
        self.database.dropIndexes()
        self.database.createIndexes()
        self.database.createConstraints()

        df_original = self.dataframe_Original.fillna("")

        if self.checkBox_DialogDatabaseRunQuery_OriginalData.isChecked():
            self.database.runQueries(cypherQuery.cypherCreate_historicalMaintenanceWorkOrder(
                schema=self.database.schema,
                originalDataframe=df_original,
                propertyToHeader_dict=self.csv_header
            ))
            print("DONE -----> Data from Original CSV Work Order stored !!")

        window_DialogWait.setProgress(30)

        if self.checkBox_DialogDatabaseRunQuery_Tag1g.isChecked():
            self.database.runQueries(cypherQuery.cypherCreate_tag(
                schema=self.database.schema,
                dataframe=self.bin1g_df,
                vocab1g=self.vocab1g_df,
                vocabNg=self.vocabNg_df
            ))
            print("\nDONE -----> Data from Tag1g Stored!!")
        window_DialogWait.setProgress(60)

        if self.checkBox_DialogDatabaseRunQuery_TagNg.isChecked():
            self.database.runQueries(cypherQuery.cypherCreate_tag(
                schema=self.database.schema,
                dataframe=self.binNg_df,
                vocab1g=self.vocab1g_df,
                vocabNg=self.vocabNg_df
            ))
            print("\nDONE ----->  Data from TagNg stored !!")
        window_DialogWait.setProgress(90)

        if self.checkBox_DialogDatabaseRunQuery_1gToNg.isChecked():
            self.database.runQueries(cypherQuery.cypherLink_Ngram1gram(
                schema=self.database.schema
            ))
            print("\nDONE ----->  TagNg --> Tag1g link created !!")

        if self.checkBox_DialogDatabaseRunQuery_IssueToItem.isChecked():
            self.database.runQueries(cypherQuery.cypherLink_itemIssue(
                schema=self.database.schema
            ))
            print("\nDONE ----->  item -> issue link upated !!")

        if self.checkBox_DialogDatabaseRunQuery_ItemToItem.isChecked():
            # self.database.runQueries(cypherQuery.cypherCreate_itemsTree(
            #     schema=self.database.schema
            # ))
            print("DONE ----->  Item hierarchy created !!")
        window_DialogWait.setProgress(99)
        window_DialogWait.close()
        self.setEnabled(True)
        self.close()

    def onClick_removeData(self):
        """
        remove all the data from the database
        :return:
        """
        dialog_sure = Qw.QMessageBox.question(self, 'Dalate Data', "Are you sure you want to remove your data??",
                                           Qw.QMessageBox.Yes | Qw.QMessageBox.No, Qw.QMessageBox.No)
        if dialog_sure == Qw.QMessageBox.Yes:
            self.database.deleteData()
            print('DONE --> your data have been removed from you database')
        else:
            print('We do NOT remove your data.')

    def check_checkBoxGroup(self):
        """
        Make available the different checkbox from one to another
        :return:
        """

        if self.csv_header:

            if self.database is not None and self.dataframe_Original is not None and self.csv_header is not None:
                self.checkBox_DialogDatabaseRunQuery_OriginalData.setEnabled(True)
            else:
                self.checkBox_DialogDatabaseRunQuery_OriginalData.setEnabled(False)
                self.checkBox_DialogDatabaseRunQuery_OriginalData.setChecked(False)

            if self.checkBox_DialogDatabaseRunQuery_OriginalData.isChecked() and self.dataframe_vocab1Gram is not None and self.dataframe_vocabNGram is not None:
                if self.bin1g_df is not None:
                    self.checkBox_DialogDatabaseRunQuery_Tag1g.setEnabled(True)
                else:
                    self.checkBox_DialogDatabaseRunQuery_Tag1g.setEnabled(False)
                    self.checkBox_DialogDatabaseRunQuery_Tag1g.setChecked(False)

                if self.binNg_df is not None:
                    self.checkBox_DialogDatabaseRunQuery_TagNg.setEnabled(True)
                else:
                    self.checkBox_DialogDatabaseRunQuery_TagNg.setEnabled(False)
                    self.checkBox_DialogDatabaseRunQuery_TagNg.setChecked(False)
            else:
                self.checkBox_DialogDatabaseRunQuery_Tag1g.setEnabled(False)
                self.checkBox_DialogDatabaseRunQuery_Tag1g.setChecked(False)
                self.checkBox_DialogDatabaseRunQuery_TagNg.setEnabled(False)
                self.checkBox_DialogDatabaseRunQuery_TagNg.setChecked(False)

            if self.checkBox_DialogDatabaseRunQuery_Tag1g.isChecked() and self.checkBox_DialogDatabaseRunQuery_TagNg.isChecked():
                self.checkBox_DialogDatabaseRunQuery_1gToNg.setEnabled(True)
            else:
                self.checkBox_DialogDatabaseRunQuery_1gToNg.setEnabled(False)
                self.checkBox_DialogDatabaseRunQuery_1gToNg.setChecked(False)

            if self.checkBox_DialogDatabaseRunQuery_1gToNg.isChecked():
                self.checkBox_DialogDatabaseRunQuery_IssueToItem.setEnabled(True)
            else:
                self.checkBox_DialogDatabaseRunQuery_IssueToItem.setEnabled(False)
                self.checkBox_DialogDatabaseRunQuery_IssueToItem.setChecked(False)

            if self.checkBox_DialogDatabaseRunQuery_Tag1g.isChecked():
                self.checkBox_DialogDatabaseRunQuery_ItemToItem.setEnabled(True)
            else:
                self.checkBox_DialogDatabaseRunQuery_ItemToItem.setEnabled(False)
                self.checkBox_DialogDatabaseRunQuery_ItemToItem.setChecked(False)
        else:
            self.checkBox_DialogDatabaseRunQuery_OriginalData.setEnabled(False)
            self.checkBox_DialogDatabaseRunQuery_Tag1g.setEnabled(False)
            self.checkBox_DialogDatabaseRunQuery_TagNg.setEnabled(False)
            self.checkBox_DialogDatabaseRunQuery_1gToNg.setEnabled(False)
            self.checkBox_DialogDatabaseRunQuery_IssueToItem.setEnabled(False)
            self.checkBox_DialogDatabaseRunQuery_ItemToItem.setEnabled(False)


fname_dialogWait = 'dialog_wait.ui'
qtDesignerFile_dialogWait = script_dir / fname_dialogWait
Ui_MainWindow_dialogWait, QtBaseClass_dialogWait = uic.loadUiType(qtDesignerFile_dialogWait)


class DialogWait(Qw.QDialog, Ui_MainWindow_dialogWait):

    def __init__(self, iconPath=None):
        Qw.QDialog.__init__(self)
        Ui_MainWindow_dialogWait.__init__(self)
        self.setupUi(self)
        self.progressBar_DialogWait.setValue(0)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        if iconPath:
            self.setWindowIcon(Qg.QIcon(iconPath))

    def setProgress(self, value):
        self.progressBar_DialogWait.setValue(value)
        Qw.QApplication.processEvents()


fname_researchWindow = 'dialogmenu_researchwindow.ui'
qtDesignerFile_researchWindow = script_dir / fname_researchWindow
Ui_MainWindow_researchWindow, QtBaseClass_researchWindow = uic.loadUiType(qtDesignerFile_researchWindow)


class DialogMenu_ResearchWindow(Qw.QDialog, Ui_MainWindow_researchWindow):

    def __init__(self, iconPath=None):
        Qw.QDialog.__init__(self)
        Ui_MainWindow_researchWindow.__init__(self)
        self.setupUi(self)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        if iconPath:
            self.setWindowIcon(Qg.QIcon(iconPath))

        self.buttonBox_ResearchWindows.rejected.connect(self.close)

        self.setEnabledSaveList()
        self.checkBox_ResearchWindows_saveVocab_percentage.clicked.connect(self.setEnabledSaveList)
        self.checkBox_ResearchWindows_saveVocab_time.clicked.connect(self.setEnabledSaveList)
        self.checkBox_ResearchWindows_saveVocab_nbtoken.clicked.connect(self.setEnabledSaveList)
        self.checkBox_ResearchWindows_saveVocab_nbUpdate.clicked.connect(self.setEnabledSaveList)

        self.show()

    def get_data(self):
        """
        return a list that represen the list to add in the configfile
        it needs a mapping based on the objectName properties of the button to the value you want to add in the configfile
        :return:
        """
        saveTime = []
        savePercentage = []
        numberToken = []
        numberUpdate = []

        saveType = []
        for btn in self.buttonGroup_ResearchWindows_recordType.buttons():
            if btn.isChecked():
                if btn.objectName() == "checkBox_ResearchWindows_saveVocab_percentage":
                    saveType.append('percentage')
                    savePercentage = [x.lstrip() for x in self.lineEdit_ResearchWindows_saveVocab_percentage.text().split(",")]
                if btn.objectName() == "checkBox_ResearchWindows_saveVocab_time":
                    saveType.append('time')
                    saveTime = [x.lstrip() for x in self.lineEdit_ResearchWindows_saveVocab_time.text().split(",")]
                if btn.objectName() == "checkBox_ResearchWindows_saveVocab_nbtoken":
                    saveType.append('numbertoken')
                    numberToken = [x.lstrip() for x in self.lineEdit_ResearchWindows_saveVocab_nbtoken.text().split(",")]
                if btn.objectName() == "checkBox_ResearchWindows_saveVocab_nbUpdate":
                    saveType.append('numberupdate')
                    numberUpdate = [x.lstrip() for x in self.lineEdit_ResearchWindows_saveVocab_nbUpdate.text().split(",")]

        print(saveTime)

        return saveType, \
               self.comboBox_ResearchWindows_projectName.currentText(), \
               self.lineEdit_ResearchWindows_projectAuthor.text(), \
               self.textEdit_ResearchWindows_projectDescription.toPlainText(), \
               saveTime, \
               savePercentage, \
               numberToken, \
               numberUpdate

    def setEnabledSaveList(self):
        """
        setEnabled True or False the list based on the checkbox
        :return:
        """
        if self.checkBox_ResearchWindows_saveVocab_percentage.isChecked():
            self.lineEdit_ResearchWindows_saveVocab_percentage.setEnabled(True)
        else:
            self.lineEdit_ResearchWindows_saveVocab_percentage.setEnabled(False)

        if self.checkBox_ResearchWindows_saveVocab_time.isChecked():
            self.lineEdit_ResearchWindows_saveVocab_time.setEnabled(True)
        else:
            self.lineEdit_ResearchWindows_saveVocab_time.setEnabled(False)

        if self.checkBox_ResearchWindows_saveVocab_nbtoken.isChecked():
            self.lineEdit_ResearchWindows_saveVocab_nbtoken.setEnabled(True)
        else:
            self.lineEdit_ResearchWindows_saveVocab_nbtoken.setEnabled(False)

        if self.checkBox_ResearchWindows_saveVocab_nbUpdate.isChecked():
            self.lineEdit_ResearchWindows_saveVocab_nbUpdate.setEnabled(True)
        else:
            self.lineEdit_ResearchWindows_saveVocab_nbUpdate.setEnabled(False)


fname_dialogspecialreplace = 'dialogmenu_specialreplace.ui'
qtDesignerFile_dialogspecialreplace = script_dir / fname_dialogspecialreplace
Ui_MainWindow_dialogspecialreplace, QtBaseClass_dialogspecialreplace = uic.loadUiType(qtDesignerFile_dialogspecialreplace)


class DialogMenu_SpecialReplace(Qw.QDialog, Ui_MainWindow_dialogspecialreplace):

    def __init__(self, iconPath=None, specialReplace={}):
        Qw.QDialog.__init__(self)
        Ui_MainWindow_dialogspecialreplace.__init__(self)
        self.setupUi(self)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        if iconPath:
            self.setWindowIcon(Qg.QIcon(iconPath))

        self.specialReplace = specialReplace
        self.setSpecialReplace()

        self.pushButton_specialReplace_newAdd.clicked.connect(self.onClick_add)

        self.buttonBox_specialReplace.rejected.connect(self.close)
        self.buttonBox_specialReplace.button(Qw.QDialogButtonBox.Reset).clicked.connect(self.onClick_reset)


    def setSpecialReplace(self):
        """
        init the window by adding the special replace that was already in the config file
        :return:
        """
        for untrack, replace in self.specialReplace.items():

            hBoxLayout = self.create_SpecialReplace_layout(untrack, replace)
            self.verticalLayout_specialReplace_replacement.addLayout(hBoxLayout)



    def onClick_add(self):
        """
        when click on the add button chekc the input
        :return:
        """
        untrack = self.lineEdit_specialReplace_newUntrack.text()
        replace = self.lineEdit_specialReplace_newReaplce.text()

        if untrack and "#" not in untrack:

            hBoxLayout = self.create_SpecialReplace_layout(untrack, replace)
            self.verticalLayout_specialReplace_replacement.addLayout(hBoxLayout)

            self.lineEdit_specialReplace_newUntrack.setText("")
            self.lineEdit_specialReplace_newReaplce.setText("")

        else:
            self.lineEdit_specialReplace_newUntrack.setStyleSheet('background-color: rgb(255, 51, 0);')


    def create_SpecialReplace_layout(self, untrack, replace=""):
        """
        return a layout that contains 2 line edit for the untacked and replace as well as the button to remove the layout
        :param untrack:
        :param replace:
        :return:
        """
        self.lineEdit_specialReplace_newUntrack.setStyleSheet('background-color: None;')
        linedit_untrack = Qw.QLineEdit(self)
        linedit_untrack.setText(untrack)
        linedit_untrack.setObjectName("untrack="+untrack)
        linedit_untrack.setEnabled(False)

        labelArrow = Qw.QLabel()
        labelArrow.setText('-->')
        labelArrow.setObjectName('arrow')

        linedit_replace = Qw.QLineEdit(self)
        linedit_replace.setText(replace)
        linedit_replace.setObjectName("replace="+replace)
        linedit_replace.setEnabled(False)

        button_remove = Qw.QPushButton("--", self)

        hBoxLayout = Qw.QHBoxLayout()
        hBoxLayout.addWidget(linedit_untrack)
        hBoxLayout.addWidget(labelArrow)
        hBoxLayout.addWidget(linedit_replace)
        hBoxLayout.addWidget(button_remove)

        button_remove.clicked.connect(lambda: self.onClick_removeReplacement(hBoxLayout))

        return hBoxLayout

    def onClick_removeReplacement(self, hBoxLayout):
        """
        remove widjet in the given layout and remove itself from the scrolarealayout
        :param localisation:
        :return:
        """
        for w in reversed(range(hBoxLayout.count())):
            hBoxLayout.itemAt(w).widget().deleteLater()

        self.verticalLayout_specialReplace_replacement.removeItem(hBoxLayout)

    def onClick_reset(self):
        """
        remove all the layout and widjet from the scollarea
        :return:
        """
        for i in reversed(range(self.verticalLayout_specialReplace_replacement.count())):
            l = self.verticalLayout_specialReplace_replacement.itemAt(i)
            for w in reversed(range(l.count())):
                l.itemAt(w).widget().deleteLater()

            self.verticalLayout_specialReplace_replacement.removeItem(l)

    def get_data(self):
        """
        Implement a wierd logic by using the name of the object which contains the needed information
        :return:
        """
        specialReplace_dict = {}

        # for layout in layour
        for i in range(self.verticalLayout_specialReplace_replacement.count()):
            l = self.verticalLayout_specialReplace_replacement.itemAt(i)

            # for widjet in layout


            for j in range(l.count()):
                w = l.itemAt(j).widget()
                texts = w.objectName().split("=")

                # if widjetname is interesting for us
                if len(texts) > 1:
                    print(w.objectName())
                    if texts[0] == "untrack":
                        untrack = texts[1]
                    elif texts[0] == "replace":
                        replace = texts[1]

            specialReplace_dict[untrack] = replace

        return specialReplace_dict


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
            config = yaml.safe_load(yamlfile)
            print("OPEN --> YAML file at: ", yaml_path)
            if not config:
                config = {}
    else:
        config = dict
        with open(yaml_path, 'w') as yamlfile:
            pyaml.dump(config, yamlfile)
            print("CREATE --> YAML file at: ", yaml_path)
    return config
