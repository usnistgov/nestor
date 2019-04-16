import importlib

import pandas as pd
import numpy as np
import fuzzywuzzy.process as zz
import shutil
import time

import chardet
import webbrowser

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import seaborn as sns

import PyQt5.QtGui as Qg
import PyQt5.QtWidgets as Qw
from PyQt5.QtCore import Qt


import nestor.keyword as kex
from nestor.ui.meta_windows import *
import nestor

import warnings
warnings.filterwarnings("ignore", 'This pattern has match groups')

neo4j_spec = importlib.util.find_spec("neo4j")
simplecrypt_spec = importlib.util.find_spec("simplecrypt")

dbModule_exists = (neo4j_spec is not None) and (simplecrypt_spec is not None)
#dbModule_exists = False

if dbModule_exists:
    from nestor.store_data.database import DatabaseNeo4J
    import neo4j

    #from nestor.ui.menu_app import DialogDatabaseRunQuery
    from nestor.store_data.helper import resultToObservationDataframe

nestorParams = nestor.CFG

fname = 'taggingUI.ui'
script_dir = Path(__file__).parent
Ui_MainWindow_taggingTool, QtBaseClass_taggingTool = uic.loadUiType(script_dir/fname)
class MyTaggingToolWindow(Qw.QMainWindow, Ui_MainWindow_taggingTool):

    def __init__(self, projectsPath, databaseToCsv_mapping=None, iconPath=None):

        Qw.QMainWindow.__init__(self)
        Ui_MainWindow_taggingTool.__init__(self)

        """
        Instantiate  values
        """
        self.helpTutorialLink = "https://nestor.readthedocs.io/en/latest/how_to_guide/tutorial.html"


        self.projectsPath = projectsPath

        self.iconPath = iconPath
        if self.iconPath:
            self.setWindowIcon(Qg.QIcon(self.iconPath))

        self.existingProject =set([folder.name for folder in projectsPath.iterdir() if folder.is_dir()])

        self.config_default = {
            'settings': {
                'numberTokens': 1000,
                'alreadyChecked_threshold': 99,
                'showCkeckBox_threshold': 50
            },
            'csvinfo': {},
            'database': {
                'schema' : str(script_dir.parent / 'store_data' / 'DatabaseSchema.yaml')
            },
            'classification':{
                'mapping':{
                    'I I': 'I',
                    'I P': 'P I',
                    'I S': 'S I',
                    'P I': 'P I',
                    'P P': 'X',
                    'P S': 'X',
                    'S I': 'S I',
                    'S P': 'X',
                    'S S': 'X'
                },
                'type': 'IPSUX'
            }

        }
        self.config = self.config_default.copy()

        self.databaseToCsv_mapping = databaseToCsv_mapping


        """
        Default values
         """
        self.dataframe_Original = None
        self.dataframe_vocab1Gram = None
        self.dataframe_vocabNGram = None

        self.dataframe_completeness = None

        self.database = None

        self.tokenExtractor_1Gram = kex.TokenExtractor()  # sklearn-style TF-IDF calc
        self.tokenExtractor_nGram = kex.TokenExtractor(ngram_range=(2, 2))

        self.tfidf_ng = None
        self.tfidf_1g = None
        self.clean_rawText_1Gram = None
        self.clean_rawText = None

        self.tag_df = None
        self.relation_df = None
        self.tag_readable = None

        self.dataframe_completeness = None

        """
        UI objects
        """
        self.setupUi(self)
        # self.setGeometry(20, 20, 648, 705)

        self.center()
        self.enableFeature(existDatabase=False, existProject=False, existTagExtracted=False)

        self.tokenUpdate1g_user = set()
        self.tokenUpdate1g_vocab = set()
        self.tokenUpdate1g_database = set()
        self.tokenUpdateNg_user = set()
        self.tokenUpdateNg_vocab = set()
        self.tokenUpdateNg_database = set()

        self.changeColor = {
            'default': 'background-color: None;',
            'wrongInput' : 'background-color: rgb(255, 51, 0);',
            'updateToken_user' : Qg.QColor(0, 179, 89),
            'updateToken_vocab' : Qg.QColor(0, 102, 102),
            'updateToken_database' : Qg.QColor(0, 102, 51)
        }

        self.completenessPlot = MyMplCanvas(self.gridLayout_report_progressPlot, self.tabWidget, self.dataframe_completeness)
        self.horizontalSlider_1gram_FindingThreshold.setValue(self.config['settings'].get('showCkeckBox_threshold',50))

        """"""


        self.classificationDictionary_1Gram = {
            'S': self.radioButton_1gram_SolutionEditor,
            'P': self.radioButton_1gram_ProblemEditor,
            'I': self.radioButton_1gram_ItemEditor,
            'X': self.radioButton_1gram_StopWordEditor,
            'U': self.radioButton_1gram_UnknownEditor,
            '' : self.radioButton_1gram_NotClassifiedEditor
        }
        self.buttonDictionary_1Gram = {
            'Item': 'I',
            'Problem': 'P',
            'Solution': 'S',
            'Ambiguous (Unknown)': 'U',
            'Irrelevant (Stop-word)': 'X',
            'not yet classified': ''
        }

        self.classificationDictionary_NGram = {
            'S I': self.radioButton_Ngram_SolutionItemEditor,
            'P I': self.radioButton_Ngram_ProblemItemEditor,
            'I': self.radioButton_Ngram_ItemEditor,
            'U': self.radioButton_Ngram_UnknownEditor,
            'X': self.radioButton_Ngram_StopWordEditor,
            'P': self.radioButton_Ngram_ProblemEditor,
            'S': self.radioButton_Ngram_SolutionEditor,
            '': self.radioButton_Ngram_NotClassifiedEditor
        }

        self.buttonDictionary_NGram = {
            'Item': 'I',
            'Problem Item': 'P I',
            'Solution Item': 'S I',
            'Ambiguous (Unknown)': 'U',
            'Irrelevant (Stop-word)': 'X',
            'Problem': 'P',
            'Solution': 'S',
            'not yet classified': ''
        }

        self.buttonGroup_similarityPattern = QButtonGroup_similarityPattern(self.verticalLayout_1gram_SimilarityPattern)



        """
        Create the interaction on the MenuItems
        """
        self.actionTutorial.triggered.connect(self.setMenu_helpTutorial)

        self.actionNew_Project.triggered.connect(self.setMenu_projectNew)
        self.actionOpen_Project.triggered.connect(self.setMenu_projectOpen)
        self.actionProject_Settings.triggered.connect(self.setMenu_settings)
        self.actionSave_Project.triggered.connect(self.setMenu_projectSave)

        self.actionMap_CSV.triggered.connect(self.setMenu_mapCsvHeader)
        self.actionReplace_special_words.triggered.connect(self.setMenu_specialReplace)

        self.actionConnect.triggered.connect(self.setMenu_databaseConnect)
        self.actionRun_Query.triggered.connect(self.setMenu_databaseRunQuery)
        self.actionOpen_Database.triggered.connect(self.setMenu_databaseOpenBrowser)
        self.actionDisconnect.triggered.connect(self.setMenu_databaseDisconnect)

        self.action_AutoPopulate_FromDatabase_1gramVocab.triggered.connect(self.setMenu_autopopulateFromDatabase_1gVocab)
        self.action_AutoPopulate_FromDatabase_NgramVocab.triggered.connect(self.setMenu_autopopulateFromDatabase_NgVocab)
        self.action_AutoPopulate_FromCSV_1gramVocab.triggered.connect(self.setMenu_autopopulateFromCSV_1gVocab)
        self.action_AutoPopulate_FromCSV_NgramVocab.triggered.connect(self.setMenu_autopopulateFromCSV_NgVocab)
        self.actionFrom_AutoPopulate_From1gramVocab.triggered.connect(self.setMenu_autopopulateNgramFrom1gram)

        self.actionTo_Zip.triggered.connect(self.setMenu_ExportZip)
        self.actionTo_Tar.triggered.connect(self.setMenu_ExportTar)
        self.actionImport.triggered.connect(self.setMenu_Import)


        self.tableWidget_1gram_TagContainer.itemSelectionChanged.connect(self.onSelect_tableViewItems1gramVocab)
        self.tableWidget_Ngram_TagContainer.itemSelectionChanged.connect(self.onSelect_tableViewItemsNgramVocab)

        self.buttonGroup_NGram_Classification.buttonClicked.connect(self.setAliasFromNgramButton)
        self.horizontalSlider_1gram_FindingThreshold.sliderMoved.connect(self.onMoveSlider_similarPattern)
        self.horizontalSlider_1gram_FindingThreshold.sliderReleased.connect(self.onMoveSlider_similarPattern)
        self.pushButton_1gram_UpdateTokenProperty.clicked.connect(self.onClick_Update1GramVocab)
        self.pushButton_Ngram_UpdateTokenProperty.clicked.connect(self.onClick_UpdateNGramVocab)

        self.pushButton_report_saveTrack.clicked.connect(self.onClick_saveTrack)
        self.pushButton_report_saveNewCsv.clicked.connect(self.onClick_saveNewCsv)
        self.pushButton_report_saveH5.clicked.connect(self.onClick_saveTagsHDFS)

        self.dialogTOU = DialogMenu_TermsOfUse()
        self.actionAbout_TagTool.triggered.connect(self.dialogTOU.show)

        self.tabWidget.currentChanged.connect(self.onChange_tableView)
        self.tabWidget.setCurrentIndex(0)

        """
        Set the shortcut 
        """
        Qw.QShortcut(Qg.QKeySequence("Ctrl+N"), self).activated.connect(self.setMenu_projectNew)
        self.actionNew_Project.setText(self.actionNew_Project.text() + "\tCtrl+N")
        Qw.QShortcut(Qg.QKeySequence("Ctrl+S"), self).activated.connect(self.setMenu_projectSave)
        self.actionSave_Project.setText(self.actionSave_Project.text() + "\tCtrl+S")
        Qw.QShortcut(Qg.QKeySequence("Ctrl+O"), self).activated.connect(self.setMenu_projectOpen)
        self.actionOpen_Project.setText(self.actionOpen_Project.text() + "\tCtrl+O")
        Qw.QShortcut(Qg.QKeySequence("Ctrl+D"), self).activated.connect(self.setMenu_databaseConnect)
        self.actionConnect.setText(self.actionConnect.text() + "\tCtrl+D")

        Qw.QShortcut(Qg.QKeySequence("Alt+1"), self).activated.connect(lambda : self.tabWidget.setCurrentIndex(0))
        Qw.QShortcut(Qg.QKeySequence("Alt+2"), self).activated.connect(lambda : self.tabWidget.setCurrentIndex(1))
        Qw.QShortcut(Qg.QKeySequence("Alt+3"), self).activated.connect(lambda : self.tabWidget.setCurrentIndex(2))



        """
        Research Mode
        """
        self.actionResearch_NewProject.triggered.connect(self.setMenu_researchProject_new)
        self.actionPause.setEnabled(False)


        self.show()

    def center(self):
        frameGm = self.frameGeometry()
        screen = Qw.QApplication.desktop().screenNumber(Qw.QApplication.desktop().cursor().pos())
        centerPoint = Qw.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def setMenu_researchProject_new(self):
        """
        create a new Research project
        :return:
        """
        dialogMenu_newResearchProject = DialogMenu_ResearchWindow(self.iconPath)
        self.setEnabled(False)
        dialogMenu_newResearchProject.closeEvent = self.close_Dialog
        rect = self.geometry()
        rect.setHeight(300)
        rect.setWidth(200)
        dialogMenu_newResearchProject.setGeometry(rect)

        dialogMenu_newResearchProject.comboBox_ResearchWindows_projectName.addItems(["excavator_data"])

        dialogMenu_newResearchProject.lineEdit_ResearchWindows_saveVocab_percentage.setText("0,5,10,20,30,40,50,60")
        dialogMenu_newResearchProject.lineEdit_ResearchWindows_saveVocab_time.setText("0,1,2,3,4,5,10,20,30,40,50,60")
        dialogMenu_newResearchProject.lineEdit_ResearchWindows_saveVocab_nbtoken.setText("0,10,20,50,100,200,300,400,500,1000")
        dialogMenu_newResearchProject.lineEdit_ResearchWindows_saveVocab_nbUpdate.setText("0,10,20,50,100,200,300,400,500,1000")


        def onclick_ok():
            saveType, name, author, description, saveTime, savePercentage, saveNumberToken, saveNumberUpdate = dialogMenu_newResearchProject.get_data()

            if saveType and author:
                dialogMenu_newResearchProject.label_ResearchWindows_saveVocab.setStyleSheet(self.changeColor['default'])
                dialogMenu_newResearchProject.lineEdit_ResearchWindows_projectAuthor.setStyleSheet(self.changeColor['default'])

                self.__class__ = MyTaggingToolWindow_research
                self.__init__(savetype=saveType, name=name, author=author, description=description,
                              saveTime=saveTime, savePercentage=savePercentage, saveNumberToken=saveNumberToken, saveNumberUpdate=saveNumberUpdate
                              )

                dialogMenu_newResearchProject.close()

            else:
                dialogMenu_newResearchProject.label_ResearchWindows_saveVocab.setStyleSheet(self.changeColor['wrongInput'])
                dialogMenu_newResearchProject.lineEdit_ResearchWindows_projectAuthor.setStyleSheet(self.changeColor['wrongInput'])

        dialogMenu_newResearchProject.buttonBox_ResearchWindows.accepted.connect(onclick_ok)

    def setMenu_projectNew(self):
        """
        When click on the New Project menu
        :return:
        """

        dialogMenu_newProject = DialogMenu_newProject(self.iconPath)
        self.setEnabled(False)
        dialogMenu_newProject.closeEvent = self.close_Dialog
        rect = self.geometry()
        rect.setHeight(300)
        rect.setWidth(200)
        dialogMenu_newProject.setGeometry(rect)


        def onclick_ok():
            self.config = None
            self.config = self.config_default.copy()
            name, author, description, vocab1g, vocabNg, pathCSV_old = dialogMenu_newProject.get_data()

            if name and pathCSV_old:
                dialogMenu_newProject.lineEdit_NewProject_ProjectName.setStyleSheet(self.changeColor['default'])
                dialogMenu_newProject.lineEdit_NewProject_LoadCSV.setStyleSheet(self.changeColor['default'])
                if name not in self.existingProject:
                    dialogMenu_newProject.lineEdit_NewProject_ProjectName.setStyleSheet(self.changeColor['default'])
                    dialogMenu_newProject.close()

                    pathCSV_new = self.projectsPath / name
                    pathCSV_new.mkdir(parents=True, exist_ok=True)

                    pathCSV_old = Path(pathCSV_old)
                    self.set_config(name = name,
                                    author=author,
                                    description=description,
                                    vocab1g=vocab1g,
                                    vocabNg=vocabNg,
                                    original=pathCSV_old.name)


                    # create the projectfolder
                    pathCSV_new = self.projectsPath / name
                    pathCSV_new.mkdir(parents=True, exist_ok=True)

                    # open the dataframe and save is as utf8 on the project localisation
                    dataframe_tmp = openDataframe(pathCSV_old)
                    dataframe_tmp.to_csv(pathCSV_new/self.config['original'],encoding='utf-8-sig')

                    self.dataframe_Original = dataframe_tmp

                    self.setMenu_mapCsvHeader()

                else:
                    Qw.QMessageBox.about(self, 'Name alreay exists', "The name you have writen already exists, please write another one")
                    dialogMenu_newProject.lineEdit_NewProject_ProjectName.setStyleSheet(self.changeColor['wrongInput'])

            else:
                dialogMenu_newProject.lineEdit_NewProject_ProjectName.setStyleSheet(self.changeColor['wrongInput'])
                dialogMenu_newProject.lineEdit_NewProject_LoadCSV.setStyleSheet(self.changeColor['wrongInput'])

        dialogMenu_newProject.buttonBox__NewProject.accepted.connect(onclick_ok)

    def setMenu_projectOpen(self):
        """
        When click on the Load Project menu
        :return:
        """

        dialogMenu_openProject = DialogMenu_openProject(self.iconPath, self.projectsPath, self.existingProject)
        self.setEnabled(False)
        dialogMenu_openProject.closeEvent = self.close_Dialog
        rect = self.geometry()
        rect.setHeight(300)
        rect.setWidth(200)
        dialogMenu_openProject.setGeometry(rect)

        def onclick_ok():
            if dialogMenu_openProject.comboBox_OpenProject_ProjectName.currentText():
                self.config = dialogMenu_openProject.get_data()
                self.whenProjectOpen()
                dialogMenu_openProject.close()


        def onclick_remove():
            if dialogMenu_openProject.comboBox_OpenProject_ProjectName.currentText() != self.config.get("name", "None"):
                if dialogMenu_openProject.comboBox_OpenProject_ProjectName.currentText() != "":
                    choice = Qw.QMessageBox.question(self, 'Remove Project',
                                                     'Do you really want to remove the project?',
                                                     Qw.QMessageBox.Yes | Qw.QMessageBox.No, Qw.QMessageBox.No)

                    if choice == Qw.QMessageBox.Yes:
                        def remove_folderContent(folder):
                            for file in folder.iterdir():
                                if file.is_file():
                                    file.unlink()
                                elif file.is_dir:
                                    remove_folderContent(file)
                            folder.rmdir()

                        remove_folderContent(self.projectsPath / dialogMenu_openProject.comboBox_OpenProject_ProjectName.currentText())
                        self.existingProject.remove(dialogMenu_openProject.comboBox_OpenProject_ProjectName.currentText())
                        dialogMenu_openProject.comboBox_OpenProject_ProjectName.clear()
                        dialogMenu_openProject.comboBox_OpenProject_ProjectName.addItems(self.existingProject)

                    else:
                        print("NOTHING --> We did not remove your project")
                else:
                    print("NOT ALLOW --> You cannot delete your current project")

        dialogMenu_openProject.pushButton_OpenProject_ProjectRemove.clicked.connect(onclick_remove)
        dialogMenu_openProject.buttonBox_OpenProject.accepted.connect(onclick_ok)

    def setMenu_projectSave(self):
        """
        Whan saving the project
        :return:
        """
        projectName= self.config.get('name')

        if projectName:
            saveYAMLConfig_File(self.projectsPath / self.config.get('name') / "config.yaml", self.config)

            folderPath = self.projectsPath / projectName
            folderPath.mkdir(parents=True, exist_ok=True)

            #TODO if can save file
            if self.dataframe_vocab1Gram is not None:
                vocab1gPath = self.config.get('vocab1g', 'vocab1g') + ".csv"
                vocab1gPath = folderPath / vocab1gPath
                self.dataframe_vocab1Gram.to_csv(vocab1gPath, encoding='utf-8-sig')

                vocabNgPath = self.config.get('vocabNg', 'vocabNg') + ".csv"
                vocabNgPath = folderPath / vocabNgPath
                self.dataframe_vocabNGram.to_csv(vocabNgPath, encoding='utf-8-sig')

            self.existingProject.add(projectName)
            print('SAVE --> All yout project is now saved!!')

    def setMenu_databaseConnect(self):
        """
        when click on the connect to database menu
        :return:
        """
        dialogMenu_databaseConnect = DialogMenu_DatabaseConnect(iconPath=self.iconPath,
                                                                configDatabase = self.config.get('database',{})
                                                                )
        self.setEnabled(False)
        dialogMenu_databaseConnect.closeEvent = self.close_Dialog
        rect = self.geometry()
        rect.setHeight(300)
        rect.setWidth(200)
        dialogMenu_databaseConnect.setGeometry(rect)

        def onclick_ok():
            username, schema, server, serverport, browserport, password = dialogMenu_databaseConnect.get_data()

            schematmp = openYAMLConfig_File(Path(schema))
            try:
                self.set_config(username=username,
                                schema=schema,
                                server=server,
                                serverport=serverport,
                                browserport=browserport
                                )

                self.database = DatabaseNeo4J(user=username,
                                         password=password,
                                         server=server,
                                         portBolt=serverport,
                                         portUi=browserport,
                                         schema=schematmp)

                dialogMenu_databaseConnect.close()

                self.enableFeature(existDatabase=True)

            except neo4j.exceptions.AuthError:
                dialogMenu_databaseConnect.lineEdit_DialogDatabaseConnection_Username.setStyleSheet(self.changeColor['wrongInput'])
                dialogMenu_databaseConnect.lineEdit_DialogDatabaseConnection_Password.setStyleSheet(self.changeColor['wrongInput'])
            except (neo4j.exceptions.AddressError, neo4j.exceptions.ServiceUnavailable):
                dialogMenu_databaseConnect.lineEdit_DialogDatabaseConnection_ServerPortNumber.setStyleSheet(self.changeColor['wrongInput'])
                dialogMenu_databaseConnect.lineEdit_DialogDatabaseConnection_ServerName.setStyleSheet(self.changeColor['wrongInput'])
                dialogMenu_databaseConnect.lineEdit_DialogDatabaseConnection_Username.setStyleSheet(self.changeColor['default'])
                dialogMenu_databaseConnect.lineEdit_DialogDatabaseConnection_Password.setStyleSheet(self.changeColor['default'])
            except FileNotFoundError:
                dialogMenu_databaseConnect.lineEdit_DialogDatabaseConnection_OpenSchema.setStyleSheet(self.changeColor['wrongInput'])
                dialogMenu_databaseConnect.lineEdit_DialogDatabaseConnection_ServerPortNumber.setStyleSheet(self.changeColor['wrongInput'])
                dialogMenu_databaseConnect.lineEdit_DialogDatabaseConnection_ServerName.setStyleSheet(self.changeColor['default'])
                dialogMenu_databaseConnect.lineEdit_DialogDatabaseConnection_Username.setStyleSheet(self.changeColor['default'])
                dialogMenu_databaseConnect.lineEdit_DialogDatabaseConnection_Password.setStyleSheet(self.changeColor['default'])


        dialogMenu_databaseConnect.buttonBox_DialogDatabaseConnection.accepted.connect(onclick_ok)

    def setMenu_databaseRunQuery(self):
        """
        When click on the run Query menu
        :return:
        """

        dialogMenu_databaseRunQuery = DialogMenu_DatabaseRunQueries(iconPath = self.iconPath,
                                                                    database = self.database,
                                                                    dataframe_Original = self.dataframe_Original,
                                                                    dataframe_vocab1Gram= self.dataframe_vocab1Gram,
                                                                    dataframe_vocabNGram= self.dataframe_vocabNGram,
                                                                    bin1g_df=self.tag_df,
                                                                    binNg_df=self.relation_df,
                                                                    vocab1g_df=self.dataframe_vocab1Gram,
                                                                    vocabNg_df= self.dataframe_vocabNGram,
                                                                    csvHeaderMapping= self.config['csvinfo'].get('mapping',{}),
                                                                    databaseToCsv_mapping= self.databaseToCsv_mapping.copy()
                                                                    )

        self.setEnabled(False)
        dialogMenu_databaseRunQuery.closeEvent = self.close_Dialog
        rect = self.geometry()
        rect.setHeight(300)
        rect.setWidth(200)
        dialogMenu_databaseRunQuery.setGeometry(rect)

        def onclick_ok():
            dialogMenu_databaseRunQuery.runQueries()
            dialogMenu_databaseRunQuery.close()

        dialogMenu_databaseRunQuery.button_DialogDatabaseRunQuery.accepted.connect(onclick_ok)

    def setMenu_databaseOpenBrowser(self):
        """
        When click on open browser
        :return:
        """
        webbrowser.open(self.database.url, new=1)

    def setMenu_databaseDisconnect(self):
        """
        Disconnect the database from the project
        :return:
        """
        self.database.close()
        print("DATABASE --> Disconnect to the database")
        self.database = None
        self.enableFeature(existDatabase=False)

    def setMenu_helpTutorial(self):
        """
        When click on open browser
        :return:
        """
        webbrowser.open(self.helpTutorialLink, new=1)

    def setMenu_autopopulateFromDatabase_1gVocab(self):

        done, result = self.database.getTokenTagClassification()

        if done:
            df = resultToObservationDataframe(result).set_index("tokens")
            self.dataframe_vocab1Gram.replace('', np.nan, inplace=True)

            mask = self.dataframe_vocab1Gram[["NE", "alias"]].isnull().all(axis=1)

            df_tmp = self.dataframe_vocab1Gram.loc[mask, :]
            df_tmp.update(other=df, overwrite=False)
            df_tmp = df_tmp.dropna(thresh=3)

            #get the list of updated index localisation from dataframe_vocab1Gram
            dataframe_vocab1Gram_copy = self.dataframe_vocab1Gram.reset_index()
            self.tokenUpdate1g_database.update(dataframe_vocab1Gram_copy.
                                               index[dataframe_vocab1Gram_copy['tokens']
                                                     .isin(df_tmp.index.tolist())]
                                               .tolist())


            self.dataframe_vocab1Gram.update(df_tmp, overwrite=False)
            self.dataframe_vocab1Gram.fillna('', inplace=True)

            self.printDataframe_TableviewProgressBar(dataframe=self.dataframe_vocab1Gram,
                                                     tableview= self.tableWidget_1gram_TagContainer,
                                                     progressBar=self.progressBar_1gram_TagComplete)

    def setMenu_autopopulateFromDatabase_NgVocab(self):

        done, result = self.database.getTokenTagClassification()

        if done:
            df = resultToObservationDataframe(result).set_index("tokens")

            self.dataframe_vocabNGram.replace('', np.nan, inplace=True)

            mask = self.dataframe_vocabNGram[["NE", "alias"]].isnull().all(axis=1)

            df_tmp = self.dataframe_vocabNGram.loc[mask, :]
            df_tmp.update(other=df, overwrite=False)
            df_tmp = df_tmp.dropna(thresh=3)

            # get the list of updated index localisation from dataframe_vocab1Gram
            dataframe_vocabNGram_copy = self.dataframe_vocabNGram.reset_index()

            self.tokenUpdateNg_database.update(
                dataframe_vocabNGram_copy
                    .index[dataframe_vocabNGram_copy['tokens']
                    .isin(df_tmp.index.tolist())]
                    .tolist()
            )

            self.dataframe_vocabNGram.update(df_tmp, overwrite=False)
            self.dataframe_vocabNGram.fillna('', inplace=True)

            self.printDataframe_TableviewProgressBar(dataframe=self.dataframe_vocabNGram,
                                                     tableview=self.tableWidget_Ngram_TagContainer,
                                                     progressBar=self.progressBar_Ngram_TagComplete)

    def setMenu_autopopulateFromCSV_1gVocab(self):
        options = Qw.QFileDialog.Options()
        fileName, _ = Qw.QFileDialog.getOpenFileName(self,
                                                     self.objectName(), "Open NESTOR generated vocab File",
                                                     "csv Files (*.csv)", options=options)

        if fileName:

            df = pd.read_csv(fileName)[["tokens","NE","alias"]].set_index("tokens")

            self.dataframe_vocab1Gram.replace('', np.nan, inplace=True)

            mask = self.dataframe_vocab1Gram[["NE", "alias"]].isnull().all(axis=1)

            df_tmp = self.dataframe_vocab1Gram.loc[mask, :]
            df_tmp.update(other=df, overwrite=False)
            df_tmp = df_tmp.dropna(thresh=3)

            # get the list of updated index localisation from dataframe_vocab1Gram
            dataframe_vocab1Gram_copy = self.dataframe_vocab1Gram.reset_index()
            self.tokenUpdate1g_vocab.update(dataframe_vocab1Gram_copy.
                                               index[dataframe_vocab1Gram_copy['tokens']
                                               .isin(df_tmp.index.tolist())]
                                               .tolist())

            self.dataframe_vocab1Gram.update(df_tmp, overwrite=False)
            self.dataframe_vocab1Gram.fillna('', inplace=True)

            self.printDataframe_TableviewProgressBar(dataframe =self.dataframe_vocab1Gram,
                                                     tableview = self.tableWidget_1gram_TagContainer,
                                                     progressBar = self.progressBar_1gram_TagComplete)

    def setMenu_autopopulateFromCSV_NgVocab(self):

        options = Qw.QFileDialog.Options()
        fileName, _ = Qw.QFileDialog.getOpenFileName(self,
                                                     self.objectName(), "Open NESTOR generated vocab File",
                                                     "csv Files (*.csv)", options=options)

        if fileName:
            df = pd.read_csv(fileName)[["tokens", "NE", "alias"]].set_index("tokens")

            self.dataframe_vocabNGram.replace('', np.nan, inplace=True)

            mask = self.dataframe_vocabNGram[["NE", "alias"]].isnull().all(axis=1)

            df_tmp = self.dataframe_vocabNGram.loc[mask, :]
            df_tmp.update(other=df, overwrite=False)
            df_tmp = df_tmp.dropna(thresh=3)

            # get the list of updated index localisation from dataframe_vocab1Gram
            dataframe_vocabNGram_copy = self.dataframe_vocabNGram.reset_index()
            self.tokenUpdateNg_vocab.update(dataframe_vocabNGram_copy.
                                               index[dataframe_vocabNGram_copy['tokens']
                                               .isin(df_tmp.index.tolist())]
                                               .tolist())

            self.dataframe_vocabNGram.update(df_tmp, overwrite=False)
            self.dataframe_vocabNGram.fillna('', inplace=True)

            self.printDataframe_TableviewProgressBar(dataframe=self.dataframe_vocabNGram,
                                                     tableview=self.tableWidget_Ngram_TagContainer,
                                                     progressBar=self.progressBar_Ngram_TagComplete)

    def setMenu_autopopulateNgramFrom1gram(self):

        NE_types = self.config['classification'].get("type")
        NE_map_rules = self.config['classification'].get('mapping')
        self.dataframe_vocabNGram = kex.ngram_automatch(self.dataframe_vocab1Gram, self.dataframe_vocabNGram, NE_types, NE_map_rules)

        self.printDataframe_TableviewProgressBar(dataframe=self.dataframe_vocabNGram,
                                                 tableview=self.tableWidget_Ngram_TagContainer,
                                                 progressBar=self.progressBar_Ngram_TagComplete)

        print('Done --> Updated Ngram classification from 1-gram vocabulary!')

    def setMenu_settings(self):
        """
        When click on the Settings menu
        """

        dialogMenu_settings = DialogMenu_settings(name = self.config.get('name',''),
                                                  author = self.config.get('author',''),
                                                  description = self.config.get('description',''),
                                                  vocab1g = self.config.get('vocab1g',''),
                                                  vocabNg = self.config.get('vocabNg',''),
                                                  configSettings = self.config.get('settings'),
                                                  iconPath=self.iconPath
                                                  )
        self.setEnabled(False)
        dialogMenu_settings.closeEvent = self.close_Dialog
        rect = self.geometry()
        rect.setHeight(300)
        rect.setWidth(200)
        dialogMenu_settings.setGeometry(rect)


        def onclick_ok():
            self.existingProject.remove(self.config.get("name"))
            name, author, description, vocab1g, vocabNg, numberTokens, alreadyChecked_threshold, showCkeckBox_threshold = dialogMenu_settings.get_data()

            if name and name not in self.existingProject:

                oldnumberToken = self.config["settings"].get("numberTokens", 1000)


                Path(str(self.projectsPath / self.config.get("name") / self.config.get("vocab1g")) + ".csv").unlink()
                Path(str(self.projectsPath / self.config.get("name") / self.config.get("vocabNg")) + ".csv").unlink()

                dialogMenu_settings.lineEdit_Settings_ProjectName.setStyleSheet(self.changeColor['default'])
                oldPath = self.projectsPath / self.config.get('name')
                oldPath.rename(self.projectsPath / name)
                #TODO same as above but for the vocabfile name

                self.existingProject.add(name)

                self.set_config(name=name,
                                author= author,
                                description= description,
                                vocab1g=vocab1g,
                                vocabNg=vocabNg,
                                numberTokens=numberTokens,
                                alreadyChecked_threshold=alreadyChecked_threshold,
                                showCkeckBox_threshold=showCkeckBox_threshold
                                )
                dialogMenu_settings.close()

                self.horizontalSlider_1gram_FindingThreshold.setValue(self.config['settings'].get('showCkeckBox_threshold',50))
                self.onMoveSlider_similarPattern()

                #TODO: should be executed even if empty, just not if unchanged
                if oldnumberToken != self.config["settings"].get("numberTokens",1000) or self.config["csvinfo"].get("untracked_token", None):
                    self.setMenu_projectSave()
                    self.whenProjectOpen()

                self.setMenu_projectSave()
            else:
                dialogMenu_settings.lineEdit_Settings_ProjectName.setStyleSheet(self.changeColor['wrongInput'])

        dialogMenu_settings.buttonBox_Setup.accepted.connect(onclick_ok)

    def setMenu_mapCsvHeader(self):
        """
        When select the NLP collumn and mapping the csv to the database
        :return:
        """

        databaseToCsv_list = []
        for key,value in self.databaseToCsv_mapping.items():
            # for key2, value2 in value1.items():
            databaseToCsv_list.append(value)

        #TODO AttributeError: 'NoneType' object has no attribute 'columns'
        self.dialogMenu_csvHeaderMapping = DialogMenu_csvHeaderMapping(csvHeaderContent= list(self.dataframe_Original.columns.values),
                                                                  mappingContent= databaseToCsv_list,
                                                                  configCsvHeader = self.config['csvinfo'].get('nlpheader', []),
                                                                  configMapping = self.config['csvinfo'].get('mapping', {})
                                                                  )

        self.setEnabled(False)
        self.dialogMenu_csvHeaderMapping.closeEvent = self.close_Dialog
        rect = self.geometry()
        rect.setHeight(700)
        rect.setWidth(500)
        self.dialogMenu_csvHeaderMapping.setGeometry(rect)

        def onclick_ok():
            nlpHeader, csvMapping = self.dialogMenu_csvHeaderMapping.get_data()
            if nlpHeader:
                self.set_config(nlpHeader=nlpHeader, csvMapping=csvMapping)
                self.dialogMenu_csvHeaderMapping.close()

                self.whenProjectOpen()

        self.dialogMenu_csvHeaderMapping.buttonBox_csvHeaderMapping.accepted.connect(onclick_ok)

    def setMenu_specialReplace(self):
        dialogMenu_specialReplace = DialogMenu_SpecialReplace(iconPath=self.iconPath,
                                                              specialReplace= self.config["csvinfo"].get("untracked_token",{}))
        self.setEnabled(False)
        dialogMenu_specialReplace.closeEvent = self.close_Dialog
        rect = self.geometry()
        rect.setHeight(300)
        rect.setWidth(200)
        dialogMenu_specialReplace.setGeometry(rect)
        dialogMenu_specialReplace.show()

        def onclick_ok():
            self.set_config(untrackedTokenList=dialogMenu_specialReplace.get_data())

            self.whenProjectOpen()

            dialogMenu_specialReplace.close()

        dialogMenu_specialReplace.buttonBox_specialReplace.accepted.connect(onclick_ok)

    def setMenu_ExportZip(self, format):
        """
        save the current project to a format zip file
        :param format:
        :return:
        """
        target = str(Qw.QFileDialog.getExistingDirectory(self, "Select Directory"))

        if target:
            target = str(Path(target) / self.config.get('name', 'noName'))
            current = str(self.projectsPath / self.config.get('name'))

            shutil.make_archive(target, 'zip', current)

    def setMenu_ExportTar(self, format):
        """
        save the current project to a format tar file
        :param format:
        :return:
        """
        target = str(Qw.QFileDialog.getExistingDirectory(self, "Select Directory"))

        if target:
            target = str(Path(target) / self.config.get('name', 'noName'))
            current = str(self.projectsPath / self.config.get('name'))

            shutil.make_archive(target, 'tar', current)

    def setMenu_Import(self):
        """
        Import a zip or a tar project
        :return:
        """
        fileName, _ = Qw.QFileDialog.getOpenFileName(self, "", "Select file to import",
                                                     'zip and tar files (*.zip *.tar)')
        if fileName:
            fileName = Path(fileName)
            if fileName.stem not in self.existingProject:
                self.existingProject.add(fileName.stem)

                shutil.unpack_archive(str(fileName), str(self.projectsPath/fileName.stem))
                self.config=openYAMLConfig_File( self.projectsPath/fileName.stem/'config.yaml')

                self.whenProjectOpen()
            else:
                print("ISSUE --> the project ", fileName.stem," already exists localy, so it cannot be imported")

    def printDataframe_TableviewProgressBar(self, dataframe, tableview, progressBar):
        """
        print the given dataframe onto the given tableview
        :param dataframe:
        :param tableview:
        :return:
        """
        if dataframe is not None:

            temp_df = dataframe.reset_index()
            temp_df.columns = ['Words', 'Classification', 'Tag', 'Note', 'score']

            nbrows, nbcols = temp_df.shape
            nbrows = nbrows - 1
            tableview.setColumnCount(nbcols - 1)  # ignore score column
            tableview.setRowCount(min([nbrows, self.config['settings'].get('numberTokens', 1000)]))
            for i in range(tableview.rowCount()):
                for j in range(nbcols - 1):  # ignore score column
                    tableview.setItem(i, j, Qw.QTableWidgetItem(str(temp_df.iat[i, j])))

            try:
                for index in tableview.userUpdate:
                    if index < 1000:
                        tableview.item(index, 0).setBackground(Qg.QColor(77, 255, 184))

            except AttributeError:
                pass

            tableview.resizeRowsToContents()
            tableview.setHorizontalHeaderLabels(temp_df.columns.tolist()[:-1])  # ignore score column
            tableview.setSelectionBehavior(Qw.QTableWidget.SelectRows)

            header = tableview.horizontalHeader()
            header.setSectionResizeMode(3, Qw.QHeaderView.Stretch)  # notes column can stretch

            self.changeTableview_color()

            self.update_progress_bar(progressBar, dataframe)
        else:
            tableview.clearSpans()
            progressBar.setValue(0)

    def changeTableview_color(self):
        """
        Change the color of the item changed based on the type of change
        :return:
        """
        max_token_num = self.config['settings'].get('numberTokens', 1000)

        for t in self.tokenUpdate1g_database:
            if t < max_token_num:
                self.tableWidget_1gram_TagContainer.item(t, 0).setBackground(self.changeColor['updateToken_database'])

        for t in self.tokenUpdateNg_database:
            if t < max_token_num:
                self.tableWidget_Ngram_TagContainer.item(t, 0).setBackground(self.changeColor['updateToken_database'])

        for t in self.tokenUpdate1g_vocab:
            if t < max_token_num:
                self.tableWidget_1gram_TagContainer.item(t, 0).setBackground(self.changeColor['updateToken_vocab'])

        for t in self.tokenUpdateNg_vocab:
            if t < max_token_num:
                self.tableWidget_Ngram_TagContainer.item(t, 0).setBackground(self.changeColor['updateToken_vocab'])

        for t in self.tokenUpdateNg_user:
            if t < max_token_num:
                self.tableWidget_Ngram_TagContainer.item(t, 0).setBackground(self.changeColor['updateToken_user'])

        for t in self.tokenUpdate1g_user:
            if t < max_token_num:
                self.tableWidget_1gram_TagContainer.item(t, 0).setBackground(
                    self.changeColor['updateToken_user'])

    def onSelect_tableViewItems1gramVocab(self):
        """
        When a given item is selected on the 1Gram TableView
        :return:
        """
        items = self.tableWidget_1gram_TagContainer.selectedItems()  # selected row
        token, classification, alias, notes = (str(i.text()) for i in items)


        if alias:
            self.lineEdit_1gram_AliasEditor.setText(alias)
        else:
            self.lineEdit_1gram_AliasEditor.setText(token)
        self.textEdit_1gram_NoteEditor.setText(notes)
        self.classificationDictionary_1Gram.get(classification, self.radioButton_1gram_NotClassifiedEditor).setChecked(True)

        self.buttonGroup_similarityPattern.textAlreadySelected = set()
        self.buttonGroup_similarityPattern.textToUncheck = set()
        self.buttonGroup_similarityPattern.create_checkBoxs(token=token,
                                                            autoCheck_value=self.config['settings'].get('alreadyChecked_threshold', 50),
                                                            checkBox_show = self.horizontalSlider_1gram_FindingThreshold.value())

    def onMoveSlider_similarPattern(self):
        """
        When the slider on the buttom of the 1Gram is moved
        :return:
        """
        try:
            self.buttonGroup_similarityPattern.create_checkBoxs(token=self.tableWidget_1gram_TagContainer.selectedItems()[0].text(),
                                                                autoCheck_value=self.config['settings'].get('alreadyChecked_threshold', 50),
                                                                checkBox_show= self.horizontalSlider_1gram_FindingThreshold.value())
        except IndexError:
            print("NOT POSSIBLE --> you need to select a token first")

    def onSelect_tableViewItemsNgramVocab(self):
        """
        When a given item is selected on the Ngram TableView
        :return:
        """
        items = self.tableWidget_Ngram_TagContainer.selectedItems()  # selected row
        token, classification, alias, notes = (str(i.text()) for i in items)

        loc = self.tokenExtractor_nGram.ranks_[self.dataframe_vocabNGram.index.get_loc(token)]
        mask = self.tfidf_ng[:, loc].todense() > 0
        tooltip = str('<br><br>'.join(
            self.together[(
                mask
                    .flatten()
                    .tolist()[0]
            )]
                .head(3)
                .tolist()
        ))

        self.label_Ngram_CompositionDescription.setToolTip('<font>'+tooltip+'</font>')

        if not alias:
            alias = token
            if classification == "I":
                alias = "_".join(alias.split(" "))

        self.lineEdit_Ngram_AliasEditor.setText(alias)

        self.textEdit_Ngram_NoteEditor.setText(notes)
        self.classificationDictionary_NGram.get(classification, self.radioButton_Ngram_NotClassifiedEditor).setChecked(True)



        # Take care of the layout in the middle.

        while self.gridLayout_Ngram_NGramComposedof.count():
            item = self.gridLayout_Ngram_NGramComposedof.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        xPos = 0
        yLabel = 0
        yValue = 1

        for tok1g in token.split(" "):

            # creat the NE, alias, notes
            try:
                firstToken = self.dataframe_vocab1Gram.loc[self.dataframe_vocab1Gram['alias'] == tok1g].iloc[0]
            except IndexError:
                firstToken = pd.Series({"NE": "",
                       "alias" : "",
                       "note": "",
                       "score": ""
                       })
            for label, value in firstToken[:-1].iteritems():
                labelLabel = Qw.QLabel()
                labelLabel.setText(str(label)+":")
                labelLabel.setObjectName("labelNGramComposition" + str(label))
                self.gridLayout_Ngram_NGramComposedof.addWidget(labelLabel, xPos, yLabel)

                labelValue = Qw.QLabel()
                labelValue.setText(str(value))
                labelValue.setObjectName("labelNGramComposition" + str(value))
                self.gridLayout_Ngram_NGramComposedof.addWidget(labelValue, xPos, yValue)

                xPos += 1

            #creat the token list
            labelLabel = Qw.QLabel()
            labelLabel.setText('Words :')
            labelLabel.setObjectName("labelNGramComposition" + 'alias')
            self.gridLayout_Ngram_NGramComposedof.addWidget(labelLabel, xPos, yLabel)

            similarityList = "\n".join(self.dataframe_vocab1Gram.index[self.dataframe_vocab1Gram['alias'] == tok1g].tolist())

            labelValueSimilarity = Qw.QLabel()
            labelValueSimilarity.setText(similarityList)
            labelValueSimilarity.setObjectName("labelNGramComposition" + 'aliasValue')
            self.gridLayout_Ngram_NGramComposedof.addWidget(labelValueSimilarity, xPos, yValue)

            xPos += 1

            separator = Qw.QFrame()
            separator.setFrameShape(Qw.QFrame.HLine)
            separator.setFrameShadow(Qw.QFrame.Sunken)
            separator.setObjectName("separator" + tok1g)
            self.gridLayout_Ngram_NGramComposedof.addWidget(separator, xPos, yLabel)

            xPos += 1

        verticalSpacer = Qw.QSpacerItem(20, 40, Qw.QSizePolicy.Minimum, Qw.QSizePolicy.Expanding)
        self.gridLayout_Ngram_NGramComposedof.addItem(verticalSpacer)

    def onClick_Update1GramVocab(self):
        """
        update the dataframe when update the 1Gram
        :return:
        """
        try:
            items = self.tableWidget_1gram_TagContainer.selectedItems()  # selected row
            token, classification, alias, notes = (str(i.text()) for i in items)


            for btn in self.buttonGroup_similarityPattern.buttons():
                if btn.isChecked():
                    new_alias = self.buttonDictionary_1Gram.get(self.buttonGroup_1Gram_Classification.checkedButton().text(), '')

                    self.tokenUpdate1g_user.add(self.dataframe_vocab1Gram.index.get_loc(btn.text()))

                    self.dataframe_vocab1Gram.at[btn.text(), 'alias'] =  self.lineEdit_1gram_AliasEditor.text()
                    self.dataframe_vocab1Gram.at[btn.text(), 'notes'] = self.textEdit_1gram_NoteEditor.toPlainText()
                    self.dataframe_vocab1Gram.at[btn.text(), 'NE'] = new_alias



            # remove the information for the token that WAS the same but the user did not want it to be the same anymore
            # only if they had the same alias
            for textToUncheck in self.buttonGroup_similarityPattern.textToUncheck:
                if self.dataframe_vocab1Gram.at[textToUncheck,"alias"] == alias:
                    self.dataframe_vocab1Gram.at[textToUncheck, 'alias'] = ""
                    self.dataframe_vocab1Gram.at[textToUncheck, 'notes'] = ""
                    self.dataframe_vocab1Gram.at[textToUncheck, 'NE'] = ""

                    self.tokenUpdate1g_user.add(self.dataframe_vocab1Gram.index.get_loc(textToUncheck))

            self.printDataframe_TableviewProgressBar(dataframe= self.dataframe_vocab1Gram,
                                                     tableview=self.tableWidget_1gram_TagContainer,
                                                     progressBar=self.progressBar_1gram_TagComplete
                                                     )

            self.tableWidget_1gram_TagContainer.selectRow(self.tableWidget_1gram_TagContainer.currentRow() + 1)
            self.lineEdit_1gram_AliasEditor.setFocus()
        except (IndexError, ValueError):
            Qw.QMessageBox.about(self, 'Can\'t select', "You should select a row first")

    def onClick_UpdateNGramVocab(self):

        try:

            items = self.tableWidget_Ngram_TagContainer.selectedItems()  # selected row
            token, classification, alias, notes = (str(i.text()) for i in items)

            self.tokenUpdateNg_user.add(self.dataframe_vocabNGram.index.get_loc(token))

            self.dataframe_vocabNGram.at[token, 'alias'] = self.lineEdit_Ngram_AliasEditor.text()
            self.dataframe_vocabNGram.at[token, 'notes'] = self.textEdit_Ngram_NoteEditor.toPlainText()
            self.dataframe_vocabNGram.at[token, 'NE'] = self.buttonDictionary_NGram.get(self.buttonGroup_NGram_Classification.checkedButton().text(), '')

            if self.buttonDictionary_NGram.get(self.buttonGroup_NGram_Classification.checkedButton().text(), '') == "I":
                self.dataframe_vocabNGram.at[token, 'alias'] = "_".join(self.lineEdit_Ngram_AliasEditor.text().split(" "))

            self.printDataframe_TableviewProgressBar(dataframe=self.dataframe_vocabNGram,
                                                     tableview=self.tableWidget_Ngram_TagContainer,
                                                     progressBar=self.progressBar_Ngram_TagComplete)
            self.tableWidget_Ngram_TagContainer.selectRow(self.tableWidget_Ngram_TagContainer.currentRow() + 1)
            self.lineEdit_Ngram_AliasEditor.setFocus()
        except (IndexError, ValueError):
            Qw.QMessageBox.about(self, 'Can\'t select', "You should select a row first")

    def set_config(self, name=None, author=None, description=None, vocab1g=None, vocabNg=None, original=None,
                   numberTokens=None, alreadyChecked_threshold=None, showCkeckBox_threshold=None, untrackedTokenList=None,
                   username = None, schema = None, server = None, serverport = None, browserport = None,
                   nlpHeader = None, csvMapping=None):
        """
        When changing an information that needs to be saved in the config file
        It Reload all the printing and stuff
        :param name:
        :param author:
        :param description:
        :param vocab1g:
        :param vocabNg:
        :param original:
        :param numberTokens:
        :param alreadyChecked_threshold:
        :param showCkeckBox_threshold:
        :return:
        """

        if name is not None:
            self.config["name"] = name
        if author is not None:
            self.config["author"] = author
        if description is not None:
            self.config["description"] = description
        if vocab1g is not None:
            self.config["vocab1g"] = vocab1g
        if vocabNg is not None:
            self.config["vocabNg"] = vocabNg
        if original is not None:
            self.config["original"] = original

        if numberTokens is not None:
            self.config['settings']["numberTokens"] = numberTokens
        if alreadyChecked_threshold is not None:
            self.config['settings']["alreadyChecked_threshold"] = alreadyChecked_threshold
        if showCkeckBox_threshold is not None:
            self.config['settings']["showCkeckBox_threshold"] = showCkeckBox_threshold

        if untrackedTokenList is not None:
            print(untrackedTokenList)
            self.config['csvinfo']["untracked_token"] = untrackedTokenList
        if nlpHeader is not None:
            self.config['csvinfo']["nlpheader"] = nlpHeader
        if csvMapping is not None:
            self.config['csvinfo']["mapping"] = csvMapping

        if username is not None:
            self.config['database']["username"] =username
        if schema is not None:
            self.config['database']["schema"] =schema
        if server is not None:
            self.config['database']["server"] =server
        if serverport is not None:
            self.config['database']["serverport"] =serverport
        if browserport is not None:
            self.config['database']["browserport"] =browserport

        saveYAMLConfig_File(self.projectsPath / self.config.get('name') / "config.yaml", self.config)

    def onChange_tableView(self, tabindex):
        """
        when changing the tab
        :param tabindex:
        :return:
        """
        #1gramtab
        if tabindex == 0:
            pass
        #ngramtab
        elif tabindex == 1:
            self.extract_NgVocab(init=self.dataframe_vocabNGram)
            self.printDataframe_TableviewProgressBar(dataframe=self.dataframe_vocabNGram,
                                                     tableview=self.tableWidget_Ngram_TagContainer,
                                                     progressBar=self.progressBar_Ngram_TagComplete)


        #reporttab
        elif tabindex == 2:
            self.printReportTable()

    def whenProjectOpen(self):
        """
        This function will execute all the changes when you create / open / import a new project
        self.config needs to be updated with the new project
        :return:
        """
        self.set_config(schema=str(script_dir.parent / 'store_data' / 'DatabaseSchema.yaml'))

        self.existingProject.add(self.config.get('name',""))

        #reset all the value to default
        self.dataframe_Original = None
        self.dataframe_vocab1Gram = None
        self.dataframe_vocabNGram = None
        self.dataframe_completeness = None
        self.tokenExtractor_1Gram = kex.TokenExtractor()  # sklearn-style TF-IDF calc
        self.tokenExtractor_nGram = kex.TokenExtractor(ngram_range=(2, 2))
        self.clean_rawText_1Gram = None
        self.clean_rawText = None
        self.tfidf_ng = None
        self.tfidf_1g = None
        self.tag_df = None
        self.relation_df = None
        self.tag_readable = None
        self.dataframe_completeness = None
        self.dataframe_completeness=None
        self.buttonGroup_similarityPattern.clean_checkboxes()
        self.buttonGroup_similarityPattern = None
        self.tokenUpdate1g_user = set()
        self.tokenUpdate1g_vocab = set()
        self.tokenUpdate1g_database = set()
        self.tokenUpdateNg_user = set()
        self.tokenUpdateNg_vocab = set()
        self.tokenUpdateNg_database = set()

        self.printDataframe_TableviewProgressBar(dataframe=self.dataframe_vocab1Gram,
                                                 tableview=self.tableWidget_1gram_TagContainer,
                                                 progressBar=self.progressBar_1gram_TagComplete)
        self.printDataframe_TableviewProgressBar(dataframe=self.dataframe_vocabNGram,
                                                 tableview=self.tableWidget_Ngram_TagContainer,
                                                 progressBar=self.progressBar_Ngram_TagComplete)

        #self.config = self.config_default.copy()

        #Open dataframs
        self.dataframe_Original = openDataframe(self.projectsPath / self.config['name'] / self.config['original'])

        vocname = str(self.config.get('vocab1g')) + '.csv'
        vocab1gPath = self.projectsPath / self.config.get('name') / vocname
        vocname = str(self.config.get('vocabNg')) + '.csv'
        vocabNgPath = self.projectsPath / self.config.get('name') / vocname


        # if we open a project, init the new dataframe with the one in the vocab
        if vocab1gPath.exists():
            self.extract_1gVocab(vocab1gPath, openDataframe(vocab1gPath).fillna("").set_index("tokens"))
        #if new project, just create the dataframe
        else:
            self.extract_1gVocab(vocab1gPath)

        if vocabNgPath.exists():
            self.extract_NgVocab(init =openDataframe(vocabNgPath).fillna("").set_index("tokens"))
        else:
            self.extract_NgVocab(vocabNgPath =vocabNgPath)

        self.printDataframe_TableviewProgressBar(dataframe=self.dataframe_vocab1Gram,
                                                 tableview=self.tableWidget_1gram_TagContainer,
                                                 progressBar=self.progressBar_1gram_TagComplete)
        self.printDataframe_TableviewProgressBar(dataframe=self.dataframe_vocabNGram,
                                                 tableview=self.tableWidget_Ngram_TagContainer,
                                                 progressBar=self.progressBar_Ngram_TagComplete)


        self.buttonGroup_similarityPattern = QButtonGroup_similarityPattern(layout=self.verticalLayout_1gram_SimilarityPattern,
                                                                            vocab = self.dataframe_vocab1Gram,
                                                                            together = self.together,
                                                                            tfidf = self.tfidf_1g,
                                                                            tokenExtractor_1Gram=self.tokenExtractor_1Gram)

        self.tableWidget_Ngram_TagContainer.selectRow(0)
        self.tableWidget_1gram_TagContainer.selectRow(0)
        self.horizontalSlider_1gram_FindingThreshold.setValue(self.config['settings'].get('showCkeckBox_threshold',50))

        # make menu available
        self.enableFeature(existProject=True, existTagExtracted=False)

    def extract_1gVocab(self, vocab1gPath= None,  init=None):
        """
        create the 1Gvocab from the original dataframe
        :return:
        """
        columns = self.config['csvinfo'].get('nlpheader', 0)

        nlp_selector = kex.NLPSelect(columns=columns, special_replace=self.config['csvinfo'].get('untracked_token', None))

        self.clean_rawText = nlp_selector.transform(self.dataframe_Original)  # might not need to set it as self
        self.together = nlp_selector.together # acces the text before it is cleaned

        self.tfidf_1g = self.tokenExtractor_1Gram.fit_transform(self.clean_rawText)
        self.dataframe_vocab1Gram = kex.generate_vocabulary_df(self.tokenExtractor_1Gram, filename=vocab1gPath, init=init)

        self.dataframe_vocab1Gram.to_csv(vocab1gPath, encoding='utf-8-sig')

    def extract_NgVocab(self, vocabNgPath=None, init=None):
        """
        Create the Ngram Vocab from the 1G vocab and the original dataframe
        :return:
        """
        self.clean_rawText_1Gram = kex.token_to_alias(self.clean_rawText, self.dataframe_vocab1Gram)

        self.tfidf_ng = self.tokenExtractor_nGram.fit_transform(self.clean_rawText_1Gram)

        self.dataframe_vocabNGram = kex.generate_vocabulary_df(self.tokenExtractor_nGram, filename=vocabNgPath, init=init)

    def update_progress_bar(self, progressBar, dataframe):
        """set the value of the progress bar based on the dataframe score

        Parameters
        ----------
        progressBar :

        dataframe :


        Returns
        -------

        """
        scores = dataframe['score']
        matched = scores[dataframe['NE'] != '']
        completed_pct = matched.sum() / scores.sum()
        progressBar.setValue(100 * completed_pct)

    def setAliasFromNgramButton(self, button):
        """
        When check a radio button on the Ngram button group, change the alias dependent on the classification
        :param button:
        :return:
        """
        if button == self.classificationDictionary_NGram.get("I"):
            alias = '_'.join(self.lineEdit_Ngram_AliasEditor.text().split(" "))
            self.lineEdit_Ngram_AliasEditor.setText(alias)
        else:
            alias = ' '.join(self.lineEdit_Ngram_AliasEditor.text().split("_"))
            self.lineEdit_Ngram_AliasEditor.setText(alias)

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
            if self.tabWidget.currentIndex() == 0:
                self.onClick_Update1GramVocab()
            elif self.tabWidget.currentIndex() ==1:
                self.onClick_UpdateNGramVocab()

        ####### bad hack to move up and down checkboxes in pyqt #######
        if event.key() == Qt.Key_Up:
            if self.tabWidget.currentIndex() == 0:
                list_len = len(self.buttonGroup_similarityPattern.buttons_list)
                enum = None
                for n,button in enumerate(self.buttonGroup_similarityPattern.buttons_list):
                    if button.hasFocus():
                        enum = n
                if enum is not None:
                    new_idx = (enum-1) % list_len
                    # print(enum, new_idx)
                    self.buttonGroup_similarityPattern.buttons_list[new_idx].setFocus()

        if event.key() == Qt.Key_Down:
            if self.tabWidget.currentIndex() == 0:
                list_len = len(self.buttonGroup_similarityPattern.buttons_list)
                enum = None
                for n,button in enumerate(self.buttonGroup_similarityPattern.buttons_list):
                    if button.hasFocus():
                        enum = n
                if enum is not None:
                    new_idx = (enum+1) % list_len
                    # print(enum, new_idx)
                    self.buttonGroup_similarityPattern.buttons_list[new_idx].setFocus()
        ###############################################################

    def close_Dialog(self, event):
        """
        When a window is closed (x, cancel, ok)
        :param event:
        :return:
        """
        self.setEnabled(True)

    def closeEvent(self, event):
        """
        Trigger when the user close the Tagging Tool Window
        :param event:
        :return:
        """
        choice = Qw.QMessageBox.question(self, 'Shut it Down',
                                         'Do you want to save your changes before closing?',
                                         Qw.QMessageBox.Save | Qw.QMessageBox.Close | Qw.QMessageBox.Cancel)

        if choice == Qw.QMessageBox.Save:
            print("SAVE AND CLOSE --> vocab 1gram and Ngram, as well as the config file")
            if self.database:
                self.database.close()
            self.setMenu_projectSave()
        elif choice == Qw.QMessageBox.Cancel:
            print("NOTHING --> config file saved (in case)")
            event.ignore()
        else:
            print("CLOSE NESTOR --> we save your config file so it is easier to open it next time")
            if self.database:
                self.database.close()

    def onClick_saveTrack(self):
        """save the current completness of the token in a dataframe
        :return:

        Parameters
        ----------

        Returns
        -------

        """

        self.setEnabled(False)


        window_DialogWait = DialogWait(iconPath=self.iconPath)
        rect = self.geometry()
        rect.setHeight(300)
        rect.setWidth(200)
        window_DialogWait.setGeometry(rect)

        window_DialogWait.show()
        window_DialogWait.setProgress(0)

        Qw.QApplication.processEvents()

        print("SAVE IN PROCESS --> calculating the extracted tags and statistics...")
        # do 1-grams
        print('ONE GRAMS...')
        tags_df = kex.tag_extractor(self.tokenExtractor_1Gram,
                                    self.clean_rawText,
                                    vocab_df=self.dataframe_vocab1Gram)
        # self.tags_read = kex._get_readable_tag_df(self.tags_df)
        window_DialogWait.setProgress(30)

        # do 2-grams
        print('TWO GRAMS...')
        tags2_df = kex.tag_extractor(self.tokenExtractor_nGram,
                                     self.clean_rawText_1Gram,
                                     vocab_df=self.dataframe_vocabNGram[self.dataframe_vocabNGram.alias.notna()])

        window_DialogWait.setProgress(60)

        # merge 1 and 2-grams.
        self.tag_df = tags_df.join(tags2_df.drop(axis='columns', labels=tags_df.columns.levels[1].tolist(), level=1))
        self.tag_readable = kex._get_readable_tag_df(self.tag_df)

        self.relation_df = self.tag_df.loc[:, ['P I', 'S I']]
        self.tag_df = self.tag_df.loc[:, ['I', 'P', 'S', 'U', 'NA']]

        # do statistics
        tag_pct, tag_comp, tag_empt = kex.get_tag_completeness(self.tag_df)

        self.label_report_tagCompleteness.setText(f'<a href="https://en.wikipedia.org/wiki/Positive_and_negative_predictive_values">Tag PPV</a>: {tag_pct.mean():.2%} +/- {tag_pct.std():.2%}')
        self.label_report_completeDocs.setText(
            f'Complete Docs: {tag_comp} of {len(self.tag_df)}, or {tag_comp/len(self.tag_df):.2%}')
        self.label_report_emptyDocs.setText(
            f'Empty Docs: {tag_empt} of {len(self.tag_df)}, or {tag_empt/len(self.tag_df):.2%}')

        window_DialogWait.setProgress(90)
        self.completenessPlot._set_dataframe(tag_pct)
        nbins = int(np.percentile(self.tag_df.sum(axis=1), 90))
        print(f'Docs have at most {nbins} tokens (90th percentile)')

        self.completenessPlot.plot_it(nbins)

        self.dataframe_completeness = tag_pct
        window_DialogWait.setProgress(99)
        window_DialogWait.close()


        self.enableFeature(existTagExtracted=True)
        print("SAVE --> your information has been saved, you can now extract your result in CSV or HDF5")
        self.setEnabled(True)

    def onClick_saveNewCsv(self):
        """generate a new csv with the original csv and the generated token for the document
        :return:

        Parameters
        ----------

        Returns
        -------

        """
        if self.tag_readable is None:
            self.onClick_saveTrack()

        fname, _ = Qw.QFileDialog.getSaveFileName(self, 'Save File')
        if fname is not "":
            if fname[-4:] != '.csv':
                fname += '.csv'

            col_names = self.config['csvinfo'].get('mapping', {})
            if col_names:
                col_map = {k: next(nestorParams.datatype_search(v))
                       for k, v in col_names.items()}
            else:
                col_map = dict()
            save_df = (self.dataframe_Original[list(col_names.keys())]
                .join(self.tag_readable, lsuffix="_pre")
                .rename(columns=col_map)
            )
            save_df.to_csv(fname)
            # self.dataframe_Original.join(self.tag_readable, lsuffix="_pre").to_csv(fname)
            print('SAVE --> readable csv with tagged documents saved at: ', str(fname))

    def onClick_saveTagsHDFS(self):
        """generate a new csv with the document and the tag occurences (0 if not 1 if )
        :return:

        Parameters
        ----------

        Returns
        -------

        """

        if self.tag_df is None:
            self.onClick_saveTrack()
        fname, _ = Qw.QFileDialog.getSaveFileName(self, 'Save File')

        if fname is not "":
            if fname[-3:] != '.h5':
                fname += '.h5'

            col_names = self.config['csvinfo'].get('mapping', {})
            col_map = {k:next(nestorParams.datatype_search(v))
                       for k,v in col_names.items()}
            save_df = self.dataframe_Original[
                list(col_names.keys())
            ].rename(columns=col_map)
            save_df.to_hdf(fname, key='df')

            self.tag_df.to_hdf(fname, key='tags')
            self.relation_df.to_hdf(fname, key='rels')
            print('SAVE --> HDF5 document containing:'
                  '\n\t- the original document (with updated header)'
                  '\n\t- the binary matrices of Tag'
                  '\n\t- the binary matrices of combined Tag')

    def enableFeature(self, existProject = None, existDatabase = None, existTagExtracted=None):
        #database exists
        if existDatabase is not None:
            if dbModule_exists is True:
                if existDatabase is True :
                    self.actionRun_Query.setEnabled(True)
                    self.actionOpen_Database.setEnabled(True)
                    self.menu_AutoPopulate_FromDatabase.setEnabled(True)
                    self.actionDisconnect.setEnabled(True)

                elif existDatabase is False:
                    self.actionRun_Query.setEnabled(False)
                    self.actionOpen_Database.setEnabled(False)
                    self.menu_AutoPopulate_FromDatabase.setEnabled(False)
                    self.actionDisconnect.setEnabled(False)
            else:
                self.actionRun_Query.setEnabled(False)
                self.actionOpen_Database.setEnabled(False)
                self.menu_AutoPopulate_FromDatabase.setEnabled(False)
                self.actionDisconnect.setEnabled(False)
                self.actionConnect.setEnabled(False)

        #if project exists
        if existProject is not None:
            if existProject is True:
                self.actionSave_Project.setEnabled(True)
                self.actionProject_Settings.setEnabled(True)
                self.actionMap_CSV.setEnabled(True)
                self.menuAuto_populate.setEnabled(True)
                self.menuExport.setEnabled(True)
                self.pushButton_report_saveTrack.setEnabled(True)
                self.tabWidget.setEnabled(True)
                self.menuDatabase.setEnabled(True)
            elif existProject is False:
                self.actionSave_Project.setEnabled(False)
                self.actionProject_Settings.setEnabled(False)
                self.actionMap_CSV.setEnabled(False)
                self.menuAuto_populate.setEnabled(False)
                self.menuExport.setEnabled(False)
                self.pushButton_report_saveTrack.setEnabled(False)
                self.tabWidget.setEnabled(False)
                self.menuDatabase.setEnabled(False)

        #if tag has been extracted
        if existTagExtracted is not None:
            if existTagExtracted is True:
                self.pushButton_report_saveNewCsv.setEnabled(True)
                self.pushButton_report_saveH5.setEnabled(True)
            elif existTagExtracted is False:
                self.pushButton_report_saveNewCsv.setEnabled(False)
                self.pushButton_report_saveH5.setEnabled(False)

    def printReportTable(self):

        tmp_df = pd.concat([self.dataframe_vocab1Gram, self.dataframe_vocabNGram[self.dataframe_vocabNGram.NE != '']])
        totalword = tmp_df.NE.replace('','NA').value_counts()
        print(totalword)

        self.label_report_NumberTaggedValue.setText(
            str(totalword.drop('NA').sum()))
        self.label_report_NumberNotTaggedValue.setText(
            str(totalword.get('NA', '0')))


        self.label_report_table_NumberwordProblem.setText(
            str(totalword.get('P','')))
        self.label_report_table_NumberwordItem.setText(
            str(totalword.get('I','')))
        self.label_report_table_NumberwordSolution.setText(
            str(totalword.get('S','')))
        self.label_report_table_NumberwordProblemitem.setText(
            str(totalword.get('P I','')))
        self.label_report_table_NumberwordSolutionitem.setText(
            str(totalword.get('S I','')))
        self.label_report_table_NumberwordAmbiguous.setText(
            str(totalword.get('U','')))
        self.label_report_table_NumberwordIrrelevante.setText(
            str(totalword.get('X','')))
        self.label_report_table_NumberwordTotal.setText(
            str(totalword.drop('NA').sum()))

        totaltag = tmp_df[['alias','NE']].drop_duplicates().NE.replace('', 'NA').value_counts()
        print(totaltag)

        self.label_report_table_NumbertagProblem.setText(
            str(totaltag.get('P', '')))
        self.label_report_table_NumbertagItem.setText(
            str(totaltag.get('I', '')))
        self.label_report_table_NumbertagSolution.setText(
            str(totaltag.get('S', '')))
        self.label_report_table_NumbertagProblemitem.setText(
            str(totaltag.get('P I','')))
        self.label_report_table_NumbertagSolutionitem.setText(
            str(totaltag.get('S I','')))
        self.label_report_table_NumbertagAmbiguous.setText(
            str(totaltag.get('U','')))
        self.label_report_table_NumbertagIrrelevant.setText(
            str(totaltag.get('X','')))
        self.label_report_table_NumbertagTotal.setText(
            str(totaltag.drop('NA').sum()))


        totalfrac = (totalword-totaltag)/totalword

        self.label_report_table_FractionProblem.setText(
            '{:.1%}'.format(totalfrac.get('P', 0.)))
        self.label_report_table_FractionItem.setText(
            '{:.1%}'.format(totalfrac.get('I', 0.)))
        self.label_report_table_FractionSolution.setText(
            '{:.1%}'.format(totalfrac.get('S', 0.)))
        self.label_report_table_FractionProblemitem.setText(
            '{:.1%}'.format(totalfrac.get('P I', 0.)))
        self.label_report_table_FractionSolutionitem.setText(
            '{:.1%}'.format(totalfrac.get('S I', 0.)))
        self.label_report_table_FractionAmbiguous.setText(
            '{:.1%}'.format(totalfrac.get('U', 0.)))
        self.label_report_table_FractionIrrelevant.setText(
            '{:.1%}'.format(totalfrac.get('X', 0.)))
        self.label_report_table_FractionTotal.setText(
            '{:.1%}'.format((totalword.sum()-totaltag.sum())/totalword.sum()))

class MyTaggingToolWindow_research(MyTaggingToolWindow):
    def __init__(self, savetype,  name, author=None, description=None,
                 saveTime=None, savePercentage=None, saveNumberToken=None, saveNumberUpdate=None
                 ):
        # TODO not able to creat more than 1 per computeur because the name is the same this need to change
        if name == "excavator_data":
            vocab1g = "vocab1g"
            vocabNg = "vocabNg"
            original = "excavators.csv"
            nlpHeader = ["OriginalShorttext"]
            csvMapping = {
                'BscStartDate' : 'Work Order Start Time-stamp',
                'Asset' : 'Machine Name',
                'OriginalShorttext' : 'Description of Problem'
            }

            lacasion = Path(__file__).parent.parent / 'datasets' / 'excavators-cleaned.csv'

        # if the project already exists, make a second one with a new name
        nameTmp = str(name)
        numTmp = 1
        while nameTmp in self.existingProject:
            nameTmp = name + str(numTmp)
            numTmp +=1
        name = str(nameTmp)


        #Set up new project
        pathCSV_new = self.projectsPath / name
        pathCSV_new.mkdir(parents=True, exist_ok=True)

        dataframe_tmp = openDataframe(lacasion)
        dataframe_tmp.to_csv(pathCSV_new / original, encoding='utf-8-sig')

        self.dataframe_Original = dataframe_tmp

        self.set_config(name = name,
                        author = author,
                        description = description,
                        vocab1g=vocab1g,
                        vocabNg=vocabNg,
                        original=original,
                        nlpHeader=nlpHeader,
                        csvMapping=csvMapping,
                        research_savetype=savetype)

        self.whenProjectOpen()


        # setup folder for research


        if "time" in savetype and saveTime:
            saveTime = [int(x) for x in saveTime]

            self.saveTime = sorted(saveTime, key=int)

            #create the folder
            self.path_saveTime = pathCSV_new / "time"
            self.path_saveTime.mkdir(parents=True, exist_ok=True)

            # Transform the time to be interval instead of moment
            previous = 0
            self.saveTimeInterval = []
            for t in self.saveTime:
                self.saveTimeInterval.append(t - previous)
                previous = t
            self.timeToRemove = 0

            self.start_time = time.time()


        else:
            self.path_saveTime = None

        if "percentage" in savetype and savePercentage:
            savePercentage = [int(x) for x in savePercentage]

            savePercentage = sorted(savePercentage, key=int)

            # create the folder
            self.path_savePercentage = pathCSV_new / "percentage"
            self.path_savePercentage.mkdir(parents=True, exist_ok=True)

            #create the list for the different vocab
            self.savePercentage1gram = list(savePercentage)
            self.savePercentageNgram = list(savePercentage)


        else:
            self.path_savePercentage = None

        if "numbertoken" in savetype and saveNumberToken:
            saveNumberToken = [int(x) for x in saveNumberToken]

            saveNumberToken = sorted(saveNumberToken, key=int)

            # create the folder
            self.path_saveNumberToken = pathCSV_new / "numberToken"
            self.path_saveNumberToken.mkdir(parents=True, exist_ok=True)

            #create the list for the different vocab
            self.saveNumberToken1gram = list(saveNumberToken)
            self.saveNumberTokenNgram = list(saveNumberToken)


            self.saveNumberToken_whenUpdate()
        else:
            self.path_saveNumberToken = None

        if "numberupdate" in savetype and saveNumberUpdate:
            saveNumberUpdate = [int(x) for x in saveNumberUpdate]

            saveNumberUpdate = sorted(saveNumberUpdate, key=int)

            # create the folder
            self.path_saveNumberUpdate = pathCSV_new / "numberUpdate"
            self.path_saveNumberUpdate.mkdir(parents=True, exist_ok=True)

            # create the list for the different vocab
            self.saveNumberUpdate1gram = list(saveNumberUpdate)
            self.saveNumberUpdateNgram = list(saveNumberUpdate)
            self.numberUpdate1gram_count = 0
            self.numberUpdateNgram_count = 0



        else:
            self.path_saveNumberUpdate = None

        self.onClick_UpdateToSaveVocab()

        self.menu_AutoPopulate_FromDatabase.setEnabled(False)
        self.menu_AutoPopulate_FromCSV.setEnabled(False)
        self.actionNew_Project.setEnabled(False)
        self.actionOpen_Project.setEnabled(False)
        self.actionImport.setEnabled(False)
        self.actionProject_Settings.setEnabled(False)
        self.menuEdit.setEnabled(False)
        self.actionPause.setEnabled(True)

        self.pushButton_1gram_UpdateTokenProperty.clicked.connect(self.onClick_UpdateToSaveVocab)
        self.pushButton_Ngram_UpdateTokenProperty.clicked.connect(self.onClick_UpdateToSaveVocab)

        self.actionPause.triggered.connect(self.stopTime)


    def set_config(self, name=None, author=None, description=None, vocab1g=None, vocabNg=None, original=None,
                   numberTokens=None, alreadyChecked_threshold=None, showCkeckBox_threshold=None, untrackedTokenList=None,
                   username = None, schema = None, server = None, serverport = None, browserport = None,
                   nlpHeader = None, csvMapping=None,
                   research_savetype = None, saveTime = None, savePercentage = None, saveNumberToken = None, saveNumberUpdate=None):

        if research_savetype is not None:
            self.config["research"] = research_savetype
        if saveTime is not None:
            self.config["save"]["time"] = saveTime
        if savePercentage is not None:
            self.config["save"]["percentage"] = savePercentage
        if saveNumberToken is not None:
            self.config["save"]["time"] = saveNumberToken
        if saveNumberUpdate is not None:
            self.config["save"]["time"] = saveNumberUpdate

        MyTaggingToolWindow.set_config(self, name=name, author=author, description=description, vocab1g=vocab1g, vocabNg=vocabNg, original=original,
                   numberTokens=numberTokens, alreadyChecked_threshold=alreadyChecked_threshold, showCkeckBox_threshold=showCkeckBox_threshold, untrackedTokenList=untrackedTokenList,
                   username = username, schema = schema, server = server, serverport = serverport, browserport = browserport,
                   nlpHeader = nlpHeader, csvMapping=csvMapping)

    def saveTime_whenUpdate(self):
        """
        save the vocab file based on the Time at every X interval
        :return:
        """
        howLong = ((time.time() - self.start_time) - self.timeToRemove) /60

        if howLong >= self.saveTimeInterval[0]:
            thistime = self.saveTime.pop(0)
            self.saveTimeInterval.pop(0)
            self.start_time = time.time()
            self.timeToRemove = 0

            vocabname = f'{thistime}_{self.config.get("vocab1g")}.csv'
            self.dataframe_vocab1Gram.to_csv(self.path_saveTime / vocabname, encoding='utf-8-sig')
            vocabname = f'{thistime}_{self.config.get("vocabNg")}.csv'
            self.dataframe_vocabNGram.to_csv(self.path_saveTime/ vocabname, encoding='utf-8-sig')

    def savePercentage_whenUpdate(self):
        """
        save the vocab file based on the Percentage at every X interval
        :return:
        """
        percent1g = self.progressBar_1gram_TagComplete.value()
        percentNg = self.progressBar_Ngram_TagComplete.value()
        if self.savePercentage1gram:  # not empty, avoids (?) indexing err #58
            if percent1g >= self.savePercentage1gram[0]:
                thisPercent = self.savePercentage1gram.pop(0)

                vocabname = f'{thisPercent}_{self.config.get("vocab1g")}.csv'
                self.dataframe_vocab1Gram.to_csv(self.path_savePercentage / vocabname, encoding='utf-8-sig')

            if percentNg >= self.savePercentageNgram[0]:
                thisPercent = self.savePercentageNgram.pop(0)

                vocabname = f'{thisPercent}_{self.config.get("vocabNg")}.csv'
                self.dataframe_vocabNGram.to_csv(self.path_savePercentage/ vocabname, encoding='utf-8-sig')

    def saveNumberToken_whenUpdate(self):
        """
        save the vocab file based on the Percentage at every X interval
        :return:
        """
        self.dataframe_vocab1Gram.replace('', np.nan, inplace=True)
        nbToken1g = int(self.dataframe_vocab1Gram[["NE"]].notnull().sum())
        self.dataframe_vocab1Gram.fillna('', inplace=True)

        self.dataframe_vocabNGram.replace('', np.nan, inplace=True)
        nbTokenNg = int(self.dataframe_vocabNGram[["alias"]].notnull().sum())
        self.dataframe_vocabNGram.fillna('', inplace=True)

        if nbToken1g >= self.saveNumberToken1gram[0]:
            thisNbToken= self.saveNumberToken1gram.pop(0)

            vocabname = f'{thisNbToken}_{self.config.get("vocab1g")}.csv'
            self.dataframe_vocab1Gram.to_csv(self.path_saveNumberToken / vocabname, encoding='utf-8-sig')

        if nbTokenNg >= self.saveNumberTokenNgram[0]:
            thisNbToken= self.saveNumberTokenNgram.pop(0)

            vocabname = f'{thisNbToken}_{self.config.get("vocabNg")}.csv'
            self.dataframe_vocabNGram.to_csv(self.path_saveNumberToken / vocabname, encoding='utf-8-sig')

    def saveNumberUpdate_whenUpdate(self):
        """
        save the vocab file based on the Percentage at every X interval
        :return:
        """
        if self.tabWidget.currentIndex() == 0:
            self.numberUpdate1gram_count += 1

        if self.numberUpdate1gram_count >= self.saveNumberUpdate1gram[0]:
            thisNbUpdate = self.saveNumberUpdate1gram.pop(0)
            vocabname = f'{thisNbUpdate}_{self.config.get("vocab1g")}.csv'
            self.dataframe_vocab1Gram.to_csv(self.path_saveNumberUpdate / vocabname, encoding='utf-8-sig')

        if self.tabWidget.currentIndex() == 1:
            self.numberUpdateNgram_count += 1
        if self.numberUpdateNgram_count >= self.saveNumberUpdateNgram[0]:
            thisNbUpdate = self.saveNumberUpdateNgram.pop(0)
            vocabname = f'{thisNbUpdate}_{self.config.get("vocabNg")}.csv'
            self.dataframe_vocabNGram.to_csv(self.path_saveNumberUpdate / vocabname, encoding='utf-8-sig')

    def onClick_UpdateToSaveVocab(self):
        """
        When click on update, save based on the need
        :return:
        """
        # No need to call the super function, because this action is automaticaly executed
        # the parent function is executed first

        # TODO here enter is only execiting this one
        if self.path_saveTime is not None:
            self.saveTime_whenUpdate()

        if self.path_savePercentage is not None:
            self.savePercentage_whenUpdate()

        if self.path_saveNumberToken is not None:
            self.saveNumberToken_whenUpdate()

        if self.path_saveNumberUpdate is not None:
            self.saveNumberUpdate_whenUpdate()

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
            if self.tabWidget.currentIndex() == 0:
                self.onClick_Update1GramVocab()
                self.onClick_UpdateToSaveVocab()
            elif self.tabWidget.currentIndex() ==1:
                self.onClick_UpdateNGramVocab()
                self.onClick_UpdateToSaveVocab()
        if event.key() == Qt.Key_Backspace:
            self.stopTime()

    def stopTime(self):
        """
        stop the time
        :return:
        """
        thisTime = time.time()
        choice = Qw.QMessageBox.question(self, 'Pause the app', 'App in pause', Qw.QMessageBox.Ok)

        self.timeToRemove = self.timeToRemove + (time.time() - thisTime)


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

def saveYAMLConfig_File(yaml_path, dict):
    """save a Yaml file based on the given path
    :return: a dictionary

    Parameters
    ----------
    yaml_path :

    dict :


    Returns
    -------

    """


    with open(yaml_path, 'w') as yamlfile:
        pyaml.dump(dict, yamlfile)
        print("SAVE --> YAML file at: ", yaml_path)

def openDataframe(path):
    """set the dataframe for the window

    Parameters
    ----------
    dataframe_1Gram :
        param dataframe_NGram: (Default value = None)
    dataframe_NGram :
         (Default value = None)
    dataframe_Original :
         (Default value = None)

    Returns
    -------

    """

    try:
        return pd.read_csv(path)
    except UnicodeDecodeError:
        print("WAIT --> your file are not an UTF8 file, we are searching the good encoding")
        print("(you might want to open it and save it as UTF8 for the next time, it is way faster))")
        encoding = chardet.detect(open(path, 'rb').read())['encoding']
        return pd.read_csv(path, encoding=encoding)


class QButtonGroup_similarityPattern(Qw.QButtonGroup):
    def __init__(self, layout, vocab=None, together=None, tfidf=None, tokenExtractor_1Gram=None):
        Qw.QButtonGroup.__init__(self)
        self.setExclusive(False)
        self.layout = layout
        self.vocab = vocab
        self.together = together
        self.tfidf = tfidf
        self.tokenExtractor_1Gram = tokenExtractor_1Gram
        self.spacer = None
        self.textAlreadySelected = set()
        self.textToUncheck = set()

        self.buttons_list=[]

        self.buttonClicked.connect(self.set_textSelected)

    def set_textSelected(self, button):
        """
        store the selected button in a list
        :param button:
        :return:
        """
        if button.isChecked():
            self.textAlreadySelected.add(button.text())
            if button.text() in self.textToUncheck:
                self.textToUncheck.remove(button.text())
        else:
            self.textAlreadySelected.remove(button.text())
            self.textToUncheck.add(button.text())

    def create_checkBoxs(self, token, autoCheck_value= 99, checkBox_show= 50):
        """create and print the checkboxes
        check it on condition

        Parameters
        ----------
        token_list :
            param autoMatch_score:
        autoMatch_score :

        alias :


        Returns
        -------

        """
        self.clean_checkboxes()

        #get the similar tokne on the dataframe
        mask = self.vocab.index.str[0] == token[0]
        similar = zz.extractBests(token, self.vocab.index[mask],
                                  limit=20)[:int( checkBox_show * 20 / 100)]

        alias = self.vocab.loc[token, 'alias']

        #for each one, create the checkbox

        for token, score in similar:
            btn = Qw.QCheckBox(token)


            loc = self.tokenExtractor_1Gram.ranks_[self.vocab.index.get_loc(token)]
            mask = self.tfidf[:, loc].todense() > 0
            tooltip = str('<br><br> '.join(
                self.together[(
                    mask
                        .flatten()
                        .tolist()[0]
                )]
                    .head(3)
                    .tolist()
                )
            )
            #make the token bold not working everytime
            #tooltip = tooltip.replace(' '+token+' ', ' <b>'+token+'</b> ')
            btn.setToolTip('<font>'+tooltip+'</font>')

            self.addButton(btn)
            self.layout.addWidget(btn)

            # auto_checked the given chechbox
            if alias is '':
                if score >= autoCheck_value:
                    btn.setChecked(True)
                    self.textAlreadySelected.add(token)
            else:
                if self.vocab.loc[btn.text(), 'alias'] == alias:
                    btn.setChecked(True)
                    self.textAlreadySelected.add(token)

            if token in self.textAlreadySelected:
                btn.setChecked(True)

            self.buttons_list.append(btn)


        self.spacer = Qw.QSpacerItem(20, 40, Qw.QSizePolicy.Minimum, Qw.QSizePolicy.Expanding)
        self.layout.addSpacerItem(self.spacer)

    def clean_checkboxes(self):
        """remove all from the layout
        :return:

        Parameters
        ----------

        Returns
        -------

        """
        for btn in self.buttons():
            self.removeButton(btn)
            self.layout.removeWidget(btn)
            btn.deleteLater()
        self.layout.removeItem(self.spacer)
        self.buttons_list = []


class MyMplCanvas(FigureCanvas):
    """the canvas used to print the plot in the right layout of the kpi UI
    All the characteristic in common for all the plot should be in this class

    Parameters
    ----------

    Returns
    -------

    """

    def __init__(self, layout=None, parent_layout=None, dataframe=None, width=4, height=3, dpi=100):
        self._set_dataframe(dataframe)
        self.layout = layout

        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent_layout)
        self.layout.addWidget(self, 0,0,1,1)

        self.tokenUpdate_user = []
        self.tokenUpdate_vocab = []
        self.tokenUpdate_database = []

        # self.plot_it()

        FigureCanvas.setSizePolicy(self,Qw.QSizePolicy.Expanding, Qw.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def _set_dataframe(self, dataframe):
        """set the dataframe

        Parameters
        ----------
        dataframe :
            return:

        Returns
        -------

        """
        self.dataframe=dataframe

    def plot_it(self, nbins=10):
        """print the plot here we have the original plot
        :return:

        Parameters
        ----------

        Returns
        -------

        """
        self.axes.clear()
        if self.dataframe is not None:
            # with sns.axes_style('ticks') as style, \
            #         sns.plotting_context('poster') as context:
            sns.distplot(self.dataframe.dropna(),
                         bins=nbins,
                         kde=False,  # issue 56, 60
                         # kde_kws={'cut': 0},
                         hist_kws={'align': 'mid'},
                         # kde=True,
                         ax=self.axes,
                         color='xkcd:slate')
            self.axes.set_xlim(0.1, 1.0)
            self.axes.set_xlabel('fraction of MWO tokens getting tagged')
            self.axes.set_title('Distribution over MWO\'s')
            sns.despine(ax=self.axes, left=True, trim=True)
            self.axes.get_yaxis().set_visible(False)

        plt.show()
        self.draw()
        self.resize_event()

        self.draw()