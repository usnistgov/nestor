import importlib
from pathlib import Path

import pandas as pd
import numpy as np
import fuzzywuzzy.process as zz
from PyQt5.QtCore import Qt
from PyQt5 import QtGui, uic
import PyQt5.QtWidgets as Qw

import pyaml, yaml
import chardet
import webbrowser


import nestor.keyword as kex
from .helper_objects import CompositionNGramItem, MyMplCanvas, QButtonGroup_similarityPattern, QTableWidget_token

from nestor.ui.meta_windows import *


neo4j_spec = importlib.util.find_spec("neo4j")
simplecrypt_spec = importlib.util.find_spec("simplecrypt")

dbModule_exists = neo4j_spec is not None and simplecrypt_spec is not None
#dbModule_exists = False

if dbModule_exists:
    from nestor.store_data.database import DatabaseNeo4J
    import neo4j

    #from nestor.ui.menu_app import DialogDatabaseRunQuery
    from nestor.store_data.helper import resultToObservationDataframe


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
        self.projectsPath = projectsPath

        self.iconPath = iconPath
        if self.iconPath:
            self.setWindowIcon(QtGui.QIcon(self.iconPath))

        self.existingProject =[folder.name for folder in projectsPath.iterdir() if folder.is_dir()]

        self.config_default = {
            'settings': {
                'numberTokens': 1000,
                'alreadyChecked_threshold': 99,
                'showCkeckBox_threshold': 50
            },
            'csvinfo': {},
            'database': {
                'schema' : str(script_dir.parent / 'store_data' / 'DatabaseSchema.yaml')
            }

        }
        self.config = self.config_default.copy()

        self.databaseToCsv_mapping = databaseToCsv_mapping


        """
        UI objects
        """
        self.setupUi(self)
        self.setGeometry(20, 20, 648, 705)

        #not connected to any database
        self.actionRun_Query.setEnabled(False)
        self.actionOpen_Database.setEnabled(False)
        self.menu_AutoPopulate_FromDatabase.setEnabled(False)

        # no project are created
        self.actionSave_Project.setEnabled(False)
        self.actionProject_Settings.setEnabled(False)
        self.actionMap_CSV.setEnabled(False)
        self.menuAuto_populate.setEnabled(False)


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
            'Stop-word': 'X',
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
            'Stop-word': 'X',
            'Problem': 'P',
            'Solution': 'S',
            'not yet classified': ''
        }


        """
        Default values
        """

        self.dataframe_Original = None
        self.dataframe_vocab1Gram = None
        self.dataframe_vocabNGram = None

        self.database = None

        # self.tokenExtractor_nGram =kex.TokenExtractor(ngram_range=(2, 2))
        # self.tokenExtractor_1Gram = kex.TokenExtractor()  # sklearn-style TF-IDF calc

        self.clean_rawText_1Gram = None

        self.tag_df = None
        self.relation_df = None
        self.tag_readable = None

        self.dataframe_completeness=None



        """
        Create the interaction on the MenuItems
        """
        self.actionNew_Project.triggered.connect(self.setMenu_projectNew)
        self.actionLoad_Project.triggered.connect(self.setMenu_projectLoad)
        self.actionProject_Settings.triggered.connect(self.setMenu_settings)
        self.actionSave_Project.triggered.connect(self.setMenu_projectSave)
        self.actionMap_CSV.triggered.connect(self.setMenu_mapCsvHeader)

        self.actionConnect.triggered.connect(self.setMenu_databaseConnect)
        self.actionRun_Query.triggered.connect(self.setMenu_databaseRunQuery)
        self.actionOpen_Database.triggered.connect(self.setMenu_databaseOpenBrowser)

        # self.action_AutoPopulate_FromDatabase_1gramVocab.triggered.connect(self.setMenu_autopopulateFromDatabase_1gVocab)
        # self.action_AutoPopulate_FromDatabase_NgramVocab.triggered.connect(self.setMenu_autopopulateFromDatabase_NgVocab)
        # self.action_AutoPopulate_FromCSV_1gramVocab.triggered.connect(self.setMenu_autopopulateFromCSV_1gVocab)
        # self.action_AutoPopulate_FromCSV_NgramVocab.triggered.connect(self.setMenu_autopopulateFromCSV_NgVocab)
        # self.﻿actionFrom_AutoPopulate_From1gramVocab.triggered.connect(self.setMenu_autopopulateNgramFrom1gram)

        self.dialogTOU = DialogMenu_TermsOfUse()
        self.actionAbout_TagTool.triggered.connect(self.dialogTOU.show)

        self.show()

    def setMenu_projectNew(self):
        """
        When click on the New Project menu
        :return:
        """

        dialogMenu_newProject = DialogMenu_newProject(self.iconPath)
        self.setEnabled(False)
        dialogMenu_newProject.closeEvent = self.close_Dialog


        def onclick_ok():
            self.config = self.config_default.copy()
            name, author, description, vocab1g, vocabNg, pathCSV_old = dialogMenu_newProject.get_data()

            if name and pathCSV_old:
                if name not in self.existingProject:
                    dialogMenu_newProject.close()

                    #create the projectfolder
                    pathCSV_new = self.projectsPath / name
                    pathCSV_new.mkdir(parents=True, exist_ok=True)

                    self.set_config(name = name,
                                    author=author,
                                    description=description,
                                    vocab1g=vocab1g,
                                    vocabNg=vocabNg,
                                    pathCSV=str(pathCSV_new / "original.csv"))

                    # open the dataframe and save is as utf8 on the project localisation
                    dataframe_tmp = openDataframe(pathCSV_old)
                    dataframe_tmp.to_csv(self.config["pathCSV"],encoding='utf-8-sig')

                    #open the dataframe on the project folder
                    self.dataframe_Original = openDataframe(self.config["pathCSV"])

                    self.setMenu_mapCsvHeader()

                    self.actionSave_Project.setEnabled(True)
                    self.actionProject_Settings.setEnabled(True)
                    self.actionMap_CSV.setEnabled(True)
                    self.menuAuto_populate.setEnabled(True)


        dialogMenu_newProject.buttonBox__NewProject.accepted.connect(onclick_ok)

    def setMenu_projectLoad(self):
        """
        When click on the Load Project menu
        :return:
        """

        dialogMenu_loadProject = DialogMenu_loadProject(self.iconPath, self.projectsPath, self.existingProject)
        self.setEnabled(False)
        dialogMenu_loadProject.closeEvent = self.close_Dialog

        def onclick_ok():
            self.config = dialogMenu_loadProject.get_data()
            dialogMenu_loadProject.close()

            self.dataframe_Original = openDataframe(self.config['pathCSV'])

            self.actionSave_Project.setEnabled(True)
            self.actionProject_Settings.setEnabled(True)
            self.actionMap_CSV.setEnabled(True)
            self.menuAuto_populate.setEnabled(True)

        dialogMenu_loadProject.buttonBox_LoadProject.accepted.connect(onclick_ok)

    def setMenu_projectSave(self):
        """
        Whan saving the project
        :return:
        """
        projectName= self.config.get('name')

        if projectName:

            self.existingProject.append(projectName)
            folderPath = self.projectsPath / projectName
            folderPath.mkdir(parents=True, exist_ok=True)
            
            #TODO save dataframe in folderPath

            saveYAMLConfig_File(folderPath/ "config.yaml", self.config)

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

        def onclick_ok():
            username, schema, server, serverport, browserport, password = dialogMenu_databaseConnect.get_data()

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
                                         schema=schema)

                dialogMenu_databaseConnect.close()

                self.actionRun_Query.setEnabled(True)
                self.actionOpen_Database.setEnabled(True)
                self.menu_AutoPopulate_FromDatabase.setEnabled(True)

            except neo4j.exceptions.AuthError:
                dialogMenu_databaseConnect.lineEdit_DialogDatabaseConnection_Username.setStyleSheet("color: rgb(255, 0, 0);")
                dialogMenu_databaseConnect.lineEdit_DialogDatabaseConnection_Password.setStyleSheet("color: rgb(255, 0, 0);")
            except (neo4j.exceptions.AddressError, neo4j.exceptions.ServiceUnavailable):
                dialogMenu_databaseConnect.lineEdit_DialogDatabaseConnection_ServerPortNumber.setStyleSheet("color: rgb(255, 0, 0);")
                dialogMenu_databaseConnect.lineEdit_DialogDatabaseConnection_ServerName.setStyleSheet("color: rgb(255, 0, 0);")
                dialogMenu_databaseConnect.lineEdit_DialogDatabaseConnection_Username.setStyleSheet("color: rgb(0, 0, 0);")
                dialogMenu_databaseConnect.lineEdit_DialogDatabaseConnection_Password.setStyleSheet("color: rgb(0, 0, 0);")
            except FileNotFoundError:
                dialogMenu_databaseConnect.lineEdit_DialogDatabaseConnection_OpenSchema.setStyleSheet("color: rgb(255, 0, 0);")
                dialogMenu_databaseConnect.lineEdit_DialogDatabaseConnection_ServerPortNumber.setStyleSheet("color: rgb(0, 0, 0);")
                dialogMenu_databaseConnect.lineEdit_DialogDatabaseConnection_ServerName.setStyleSheet("color: rgb(0, 0, 0);")
                dialogMenu_databaseConnect.lineEdit_DialogDatabaseConnection_Username.setStyleSheet("color: rgb(0, 0, 0);")
                dialogMenu_databaseConnect.lineEdit_DialogDatabaseConnection_Password.setStyleSheet("color: rgb(0, 0, 0);")


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
                                                                    bin1g_df=None,
                                                                    binNg_df=None,
                                                                    csvHeaderMapping= self.config['csvinfo'].get('mapping',{}),
                                                                    databaseToCsv_mapping= self.databaseToCsv_mapping
                                                                    )
        self.setEnabled(False)
        dialogMenu_databaseRunQuery.closeEvent = self.close_Dialog

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

    # def setMenu_autopopulateFromDatabase_1gVocab(self):
    #
    #     done, result = self.database.getTokenTagClassification()
    #
    #     if done:
    #         df = resultToObservationDataframe(result).set_index("tokens")
    #         self.dataframe_vocab1Gram.replace('', np.nan, inplace=True)
    #
    #         mask = self.dataframe_vocab1Gram[["NE", "alias"]].isnull().all(axis=1)
    #
    #         df_tmp = self.dataframe_vocab1Gram.loc[mask, :]
    #         df_tmp.update(other=df, overwrite=False)
    #
    #         self.dataframe_vocab1Gram.update(df_tmp, overwrite=False)
    #         self.dataframe_vocab1Gram.fillna('', inplace=True)
    #
    #         self.tableWidget_1gram_TagContainer.set_dataframe(self.dataframe_vocab1Gram)
    #         self.tableWidget_1gram_TagContainer.printDataframe_tableView()
    #         self.update_progress_bar(self.progressBar_1gram_TagComplete, self.dataframe_vocab1Gram)
    #
    # def setMenu_autopopulateFromDatabase_NgVocab(self):
    #
    #     done, result = self.database.getTokenTagClassification()
    #
    #     if done:
    #         df = resultToObservationDataframe(result).set_index("tokens")
    #
    #         self.dataframe_vocabNGram.replace('', np.nan, inplace=True)
    #
    #         mask = self.dataframe_vocabNGram[["NE", "alias"]].isnull().all(axis=1)
    #
    #         df_tmp = self.dataframe_vocabNGram.loc[mask, :]
    #         df_tmp.update(other=df, overwrite=False)
    #
    #         self.dataframe_vocabNGram.update(df_tmp, overwrite=False)
    #         self.dataframe_vocabNGram.fillna('', inplace=True)
    #
    #         self.tableWidget_Ngram_TagContainer.set_dataframe(self.dataframe_vocabNGram)
    #         self.tableWidget_Ngram_TagContainer.printDataframe_tableView()
    #         self.update_progress_bar(self.progressBar_Ngram_TagComplete, self.dataframe_vocabNGram)
    #
    # def setMenu_autopopulateFromCSV_1gVocab(self):
    #     options = Qw.QFileDialog.Options()
    #     fileName, _ = Qw.QFileDialog.getOpenFileName(self,
    #                                                  self.objectName(), "Open NESTOR generated vocab File",
    #                                                  "csv Files (*.csv)", options=options)
    #
    #     if fileName:
    #
    #         df = pd.read_csv(fileName)[["tokens","NE","alias"]].set_index("tokens")
    #
    #         self.dataframe_vocab1Gram.replace('', np.nan, inplace=True)
    #
    #         mask = self.dataframe_vocab1Gram[["NE", "alias"]].isnull().all(axis=1)
    #
    #         df_tmp = self.dataframe_vocab1Gram.loc[mask, :]
    #         df_tmp.update(other=df, overwrite=False)
    #
    #         self.dataframe_vocab1Gram.update(df_tmp, overwrite=False)
    #         self.dataframe_vocab1Gram.fillna('', inplace=True)
    #
    #         self.tableWidget_1gram_TagContainer.set_dataframe(self.dataframe_vocab1Gram)
    #         self.tableWidget_1gram_TagContainer.printDataframe_tableView()
    #         self.update_progress_bar(self.progressBar_1gram_TagComplete, self.dataframe_vocab1Gram)
    #
    #
    # def setMenu_autopopulateFromCSV_NgVocab(self):
    #     options = Qw.QFileDialog.Options()
    #     fileName, _ = Qw.QFileDialog.getOpenFileName(self,
    #                                                  self.objectName(), "Open NESTOR generated vocab File",
    #                                                  "csv Files (*.csv)", options=options)
    #
    #     if fileName:
    #         df = pd.read_csv(fileName)[["tokens", "NE", "alias"]].set_index("tokens")
    #
    #         self.dataframe_vocabNGram.replace('', np.nan, inplace=True)
    #
    #         mask = self.dataframe_vocabNGram[["NE", "alias"]].isnull().all(axis=1)
    #
    #         df_tmp = self.dataframe_vocabNGram.loc[mask, :]
    #         df_tmp.update(other=df, overwrite=False)
    #
    #         self.dataframe_vocabNGram.update(df_tmp, overwrite=False)
    #         self.dataframe_vocabNGram.fillna('', inplace=True)
    #
    #         self.tableWidget_Ngram_TagContainer.set_dataframe(self.dataframe_vocabNGram)
    #         self.tableWidget_Ngram_TagContainer.printDataframe_tableView()
    #         self.update_progress_bar(self.progressBar_Ngram_TagComplete, self.dataframe_vocabNGram)
    #
    #
    # def setMenu_autopopulateNgramFrom1gram(self, filename=None, init=None):
    #     """update the Bgram dataframe from the new 1gram input
    #
    #     Parameters
    #     ----------
    #     filename :
    #         param init: (Default value = None)
    #     init :
    #          (Default value = None)
    #
    #     Returns
    #     -------
    #
    #     """
    #
    #     self.clean_rawText_1Gram = kex.token_to_alias(self.clean_rawText, self.dataframe_1Gram)
    #     self.tokenExtractor_nGram = kex.TokenExtractor(ngram_range=(2, 2))
    #     list_tokenExtracted = self.tokenExtractor_nGram.fit_transform(self.clean_rawText_1Gram)
    #
    #     # create the n gram dataframe
    #
    #     self.dataframe_NGram = kex.generate_vocabulary_df(self.tokenExtractor_nGram, filename=filename, init=init)
    #
    #     NE_types = self.config_default['NE_info']['NE_types']
    #     NE_map_rules = self.config_default['NE_info']['NE_map']
    #     self.dataframe_NGram = kex.ngram_automatch(self.dataframe_1Gram, self.dataframe_NGram, NE_types, NE_map_rules)
    #
    #     self.window_taggingTool._set_tokenExtractor(tokenExtractor_nGram=self.tokenExtractor_nGram)
    #     self.window_taggingTool._set_cleanRawText(clean_rawText_1Gram=self.clean_rawText_1Gram)
    #
    #     #print('Done --> Updated Ngram classification from 1-gram vocabulary!')
    #


    def setMenu_settings(self):
        """
        When click on the Settings menu
        """

        dialogMenu_settings = DialogMenu_settings(self.iconPath, self.config.get('settings'),
                                                  "; ".join(self.config['csvinfo'].get('untracked_token', ""))
                                                  )
        self.setEnabled(False)
        dialogMenu_settings.closeEvent = self.close_Dialog

        def onclick_ok():
            numberTokens, alreadyChecked_threshold, showCkeckBox_threshold, untrackedTokenList = dialogMenu_settings.get_data()
            self.set_config(numberTokens=numberTokens,
                            alreadyChecked_threshold=alreadyChecked_threshold,
                            showCkeckBox_threshold=showCkeckBox_threshold,
                            untrackedTokenList=untrackedTokenList)
            dialogMenu_settings.close()
            print(self.config)

        dialogMenu_settings.buttonBox_Setup.accepted.connect(onclick_ok)

    def setMenu_mapCsvHeader(self):
        """
        When select the NLP collumn and mapping the csv to the database
        :return:
        """

        databaseToCsv_list = []
        for key1 ,value1 in self.databaseToCsv_mapping.items():
            for key2, value2 in value1.items():
                databaseToCsv_list.append(value2)

        #TODO AttributeError: 'NoneType' object has no attribute 'columns'
        dialogMenu_csvHeaderMapping = DialogMenu_csvHeaderMapping(csvHeaderContent= list(self.dataframe_Original.columns.values),
                                                                  mappingContent= databaseToCsv_list,
                                                                  configCsvHeader = self.config['csvinfo'].get('nlpheader', []),
                                                                  configMapping = self.config['csvinfo'].get('mapping', {}))

        self.setEnabled(False)
        dialogMenu_csvHeaderMapping.closeEvent = self.close_Dialog

        def onclick_ok():
            self.config["csvinfo"]["nlpheader"], self.config["csvinfo"]["mapping"] = dialogMenu_csvHeaderMapping.get_data()
            dialogMenu_csvHeaderMapping.close()

        dialogMenu_csvHeaderMapping.buttonBox_csvHeaderMapping.accepted.connect(onclick_ok)

    def set_config(self, name=None, author=None, description=None, vocab1g=None, vocabNg=None, pathCSV=None,
                   numberTokens=None, alreadyChecked_threshold=None, showCkeckBox_threshold=None, untrackedTokenList=None,
                   username = None, schema = None, server = None, serverport = None, browserport = None):
        """
        When changing an information that needs to be saved in the config file
        It Reload all the printing and stuff
        :param name:
        :param author:
        :param description:
        :param vocab1g:
        :param vocabNg:
        :param pathCSV:
        :param numberTokens:
        :param alreadyChecked_threshold:
        :param showCkeckBox_threshold:
        :return:
        """

        if name:
            self.config["name"] = name
        if author:
            self.config["author"] = author
        if description:
            self.config["description"] = description
        if vocab1g:
            self.config["vocab1g"] = vocab1g
        if vocabNg:
            self.config["vocabNg"] = vocabNg
        if pathCSV:
            self.config["pathCSV"] = pathCSV

        if numberTokens:
            self.config['settings']["numberTokens"] = numberTokens
        if alreadyChecked_threshold:
            self.config['settings']["alreadyChecked_threshold"] = alreadyChecked_threshold
        if showCkeckBox_threshold:
            self.config['settings']["showCkeckBox_threshold"] = showCkeckBox_threshold
        if untrackedTokenList:
            self.config['csvinfo']["untracked_token"] = untrackedTokenList

        if username:
            self.config['database']["username"] =username
        if schema:
            self.config['database']["schema"] =schema
        if server:
            self.config['database']["server"] =server
        if serverport:
            self.config['database']["serverport"] =serverport
        if browserport:
            self.config['database']["browserport"] =browserport


        #TODO update all the print view and stuff

        # self.buttonGroup_1Gram_similarityPattern = QButtonGroup_similarityPattern(self.verticalLayout_1gram_SimilarityPattern)
        # self.tableWidget_1gram_TagContainer.__class__ = QTableWidget_token
        # self.tableWidget_Ngram_TagContainer.__class__ = QTableWidget_token
        #
        # row_color = QtGui.QColor(77, 255, 184)
        #
        # self.tableWidget_1gram_TagContainer.userUpdate= set()
        # self.tableWidget_1gram_TagContainer.color = row_color
        # self.tableWidget_Ngram_TagContainer.userUpdate= set()
        # self.tableWidget_Ngram_TagContainer.color = row_color
        #
        # self.middleLayout_Ngram_Composition = CompositionNGramItem(self.verticalLayout_Ngram_CompositionDisplay)
        # self.tabWidget.setCurrentIndex(0)
        #
        # self.tableWidget_1gram_TagContainer.itemSelectionChanged.connect(self.onSelectedItem_table1Gram)
        # self.tableWidget_Ngram_TagContainer.itemSelectionChanged.connect(self.onSelectedItem_tableNGram)
        # self.horizontalSlider_1gram_FindingThreshold.sliderMoved.connect(self.onSliderMoved_similarityPattern)
        # self.horizontalSlider_1gram_FindingThreshold.sliderReleased.connect(self.onSliderMoved_similarityPattern)
        # self.pushButton_1gram_UpdateTokenProperty.clicked.connect(self.onClick_updateButton_1Gram)
        # self.pushButton_Ngram_UpdateTokenProperty.clicked.connect(self.onClick_updateButton_NGram)
        # self.pushButton_1gram_SaveTableView.clicked.connect(lambda: self.onClick_saveButton(self.dataframe_vocab1Gram, self.config['file']['filePath_1GrammCSV']['path']))
        # self.pushButton_Ngram_SaveTableView.clicked.connect(lambda: self.onClick_saveButton(self.dataframe_vocabNGram, self.config['file']['filePath_nGrammCSV']['path']))
        #
        # self.pushButton_report_saveTrack.clicked.connect(self.onClick_saveTrack)
        # self.pushButton_report_saveNewCsv.clicked.connect(self.onClick_saveNewCsv)
        # self.pushButton_report_saveBinnaryCsv.clicked.connect(self.onClick_saveTagsHDFS)
        #
        # self.completenessPlot= MyMplCanvas(self.gridLayout_report_progressPlot, self.tabWidget, self. dataframe_completeness)
        #
        # self.buttonGroup_NGram_Classification.buttonClicked.connect(self.onClick_changeClassification)
        #
        #
        # # Load up the terms of service class/window
        # self.terms_of_use = TermsOfServiceDialog(iconPath=self.iconPath) # doesn't need a close button, just "x" out
        # self.actionAbout_TagTool.triggered.connect(self.terms_of_use.show)  # in the `about` menu>about TagTool
        #
        # self.action_AutoPopulate_FromCSV_1gramVocab.triggered.connect(self.setMenu_AutoPopulate_FromCSV)
        #
        # if dbModule_exists:
        #     self.actionConnect.triggered.connect(self.setMenu_DialogConnectToDatabase)
        # else:
        #     self.menuDatabase.setEnabled(False)

#########################################################################################################
#########################################################################################################
#########################################################################################################
#########################################################################################################
#########################################################################################################
#########################################################################################################
#########################################################################################################
#########################################################################################################
#########################################################################################################
#########################################################################################################
#########################################################################################################


    def onClick_changeClassification(self, btn):
        new_clf = self.buttonDictionary_NGram.get(btn.text())
        items = self.tableWidget_Ngram_TagContainer.selectedItems()  # selected row
        tokens, classification, alias, notes = (str(i.text()) for i in items)

        if not alias:
            if new_clf in ['I','S','P']:
                labels = tokens.split(' ')  # the ngram component 1-gram parts
                #self.lineEdit_Ngram_AliasEditor.setStyleSheet("QLineEdit{background: red;}")

                self.lineEdit_Ngram_AliasEditor.setText("_".join(labels))

    def onClick_saveTrack(self):
        """save the current completness of the token in a dataframe
        :return:

        Parameters
        ----------

        Returns
        -------

        """

        #block any action on the main window

        # get the main wondow possition
        rect = self.geometry()
        rect.setHeight(70)
        rect.setWidth(200)

        window_DialogWait = DialogWait(iconPath=self.iconPath)
        window_DialogWait.setGeometry(rect)
        # block the Dialog_wait in front of all other windows
        window_DialogWait.show()
        Qw.QApplication.processEvents()


        print("SAVE IN PROCESS --> calculating the extracted tags and statistics...")
        # do 1-grams
        print('ONE GRAMS...')
        tags_df = kex.tag_extractor(self.tokenExtractor_1Gram,
                                    self.clean_rawText,
                                    vocab_df=self.dataframe_vocab1Gram)
        # self.tags_read = kex._get_readable_tag_df(self.tags_df)
        window_DialogWait.setProgress(30)
        Qw.QApplication.processEvents()
        # do 2-grams
        print('TWO GRAMS...')
        tags2_df = kex.tag_extractor(self.tokenExtractor_nGram,
                                     self.clean_rawText_1Gram,
                                     vocab_df=self.dataframe_vocabNGram[self.dataframe_vocabNGram.alias.notna()])

        window_DialogWait.setProgress(60)
        Qw.QApplication.processEvents()
        # merge 1 and 2-grams.
        tag_df = tags_df.join(tags2_df.drop(axis='columns', labels=tags_df.columns.levels[1].tolist(), level=1))
        self.tag_readable = kex._get_readable_tag_df(tag_df)

        self.relation_df = tag_df.loc[:, ['P I', 'S I']]
        self.tag_df = tag_df.loc[:, ['I', 'P', 'S', 'U', 'NA']]
        # tag_readable.head(10)

        # do statistics
        tag_pct, tag_comp, tag_empt = kex.get_tag_completeness(self.tag_df)

        self.label_report_tagCompleteness.setText(f'Tag PPV: {tag_pct.mean():.2%} +/- {tag_pct.std():.2%}')
        self.label_report_completeDocs.setText(f'Complete Docs: {tag_comp} of {len(self.tag_df)}, or {tag_comp/len(tag_df):.2%}')
        self.label_report_emptyDocs.setText(f'Empty Docs: {tag_empt} of {len(self.tag_df)}, or {tag_empt/len(self.tag_df):.2%}')

        window_DialogWait.setProgress(90)
        Qw.QApplication.processEvents()
        self.completenessPlot._set_dataframe(tag_pct)
        nbins = int(np.percentile(tag_df.sum(axis=1), 90))
        print(f'Docs have at most {nbins} tokens (90th percentile)')
        self.completenessPlot.plot_it(nbins)

        self.dataframe_completeness = tag_pct
        # return tag_readable, tag_df
        window_DialogWait.setProgress(99)
        Qw.QApplication.processEvents()
        window_DialogWait.close()


        self.pushButton_report_saveNewCsv.setEnabled(True)
        self.pushButton_report_saveBinnaryCsv.setEnabled(True)

        Qw.QApplication.processEvents()

        print("SAVE --> your information has been saved, you can now extract your result in CSV or HDF5")

    def onClick_saveNewCsv(self):
        """generate a new csv with the original csv and the generated token for the document
        :return:

        Parameters
        ----------

        Returns
        -------

        """
        # tag_readable, tag_df = self.onClick_saveTrack()
        #TODO add this stuff to the original csv data
        if self.tag_readable is None:
            self.onClick_saveTrack()

        fname, _ = Qw.QFileDialog.getSaveFileName(self, 'Save File')
        if fname is not "":
            if fname[-4:] != '.csv':
                fname += '.csv'

            self.dataframe_Original.join(self.tag_readable, lsuffix="_pre").to_csv(fname)
            print('SAVE --> readable csv with tagged documents saved at: ', str(fname))

    def onClick_saveTagsHDFS(self):
        """generate a new csv with the document and the tag occurences (0 if not 1 if )
        :return:

        Parameters
        ----------

        Returns
        -------

        """
        # tag_readable, tag_df = self.onClick_saveTrack()

        if self.tag_df is None:
            self.onClick_saveTrack()
        # fname = Path('.')
        fname, _ = Qw.QFileDialog.getSaveFileName(self, 'Save File')

        if fname is not "":
            if fname[-3:] != '.h5':
                fname += '.h5'


            col_map = self.config['csvheader_mapping']
            save_df = self.dataframe_Original[list(col_map.keys())]
            save_df = save_df.rename(columns=col_map)
            save_df.to_hdf(fname, key='df')

            self.tag_df.to_hdf(fname, key='tags')
            self.relation_df.to_hdf(fname, key='rels')
            print('SAVE --> HDF5 document containing:'
                  '\n\t- the original document (with updated header)'
                  '\n\t- the binary matrices of Tag'
                  '\n\t- the binary matrices of combined Tag')
            # TODO add fname to config.yml as pre-loaded "update tag extraction"

    def onSelectedItem_table1Gram(self):
        """action when we select an item from the 1Gram table view
        :return:

        Parameters
        ----------

        Returns
        -------

        """
        items = self.tableWidget_1gram_TagContainer.selectedItems()  # selected row
        token, classification, alias, notes = (str(i.text()) for i in items)

        self._set_editorValue_1Gram(alias, token, notes, classification)
        matches = self._get_similarityMatches(token)

        self.buttonGroup_1Gram_similarityPattern.set_checkBoxes_initial(matches, self.similarityThreshold_alreadyChecked, self.dataframe_vocab1Gram, alias)
        #self.buttonGroup_1Gram_similarityPattern.autoChecked(self.dataframe_1Gram, alias)

    def onSelectedItem_tableNGram(self):
        """action when we select an item from the NGram table view
        :return:

        Parameters
        ----------

        Returns
        -------

        """
        items = self.tableWidget_Ngram_TagContainer.selectedItems()  # selected row
        tokens, classification, alias, notes = (str(i.text()) for i in items)

        self.middleLayout_Ngram_Composition.printView(self.dataframe_vocab1Gram, tokens)

        if not alias:
            if classification in ['P','S','I']:
                labels = tokens.split(' ')
                alias = '_'.join(labels)

        self._set_editorValue_NGram(alias, tokens, notes, classification)

    def onClick_saveButton(self, dataframe, path):
        """save the dataframe to the CSV file
        :return:

        Parameters
        ----------
        dataframe :
            
        path :
            

        Returns
        -------

        """
        dataframe.to_csv(path)

    def onClick_updateButton_1Gram(self):
        """Triggers with update button. Saves user annotation to the dataframe"""
        try:
            items = self.tableWidget_1gram_TagContainer.selectedItems()  # selected row
            token, classification, alias, notes = (str(i.text()) for i in items)

            new_alias = self.lineEdit_1gram_AliasEditor.text()
            new_notes = self.textEdit_1gram_NoteEditor.toPlainText()
            new_clf = self.buttonDictionary_1Gram.get(self.buttonGroup_1Gram_Classification.checkedButton().text(), pd.np.nan)
            self.dataframe_vocab1Gram = self._set_dataframeItemValue(self.dataframe_vocab1Gram, token, new_alias, new_clf, new_notes)
            self.tableWidget_1gram_TagContainer.set_dataframe(self.dataframe_vocab1Gram)

            self.tableWidget_1gram_TagContainer.userUpdate.add(self.dataframe_vocab1Gram.index.get_loc(token))

            for btn in self.buttonGroup_1Gram_similarityPattern.buttons():
                if btn in self.buttonGroup_1Gram_similarityPattern.checkedButtons():
                    self.dataframe_vocab1Gram = self._set_dataframeItemValue(self.dataframe_vocab1Gram, btn.text(), new_alias, new_clf,
                                                                             new_notes)
                    self.tableWidget_1gram_TagContainer.userUpdate.add(self.dataframe_vocab1Gram.index.get_loc(btn.text()))

                elif self.dataframe_vocab1Gram.loc[btn.text()]['alias']:
                    self.dataframe_vocab1Gram = self._set_dataframeItemValue(self.dataframe_vocab1Gram, btn.text(), '',
                                                                       '', '')

                    self.tableWidget_1gram_TagContainer.userUpdate.add(self.dataframe_vocab1Gram.index.get_loc(btn.text()))


            self.tableWidget_1gram_TagContainer.printDataframe_tableView()

            self.update_progress_bar(self.progressBar_1gram_TagComplete, self.dataframe_vocab1Gram)
            self.tableWidget_1gram_TagContainer.selectRow(self.tableWidget_1gram_TagContainer.currentRow() + 1)


        except (IndexError, ValueError):
            Qw.QMessageBox.about(self, 'Can\'t select', "You should select a row first")

    def onClick_updateButton_NGram(self):
        """Triggers with update button. Saves user annotation to the dataframe"""
        try :
            items = self.tableWidget_Ngram_TagContainer.selectedItems()  # selected row
            token, classification, alias, notes = (str(i.text()) for i in items)

            self.tableWidget_Ngram_TagContainer.userUpdate.add(self.dataframe_vocabNGram.index.get_loc(token))

            new_alias = self.lineEdit_Ngram_AliasEditor.text()
            new_notes = self.textEdit_Ngram_NoteEditor.toPlainText()
            new_clf = self.buttonDictionary_NGram.get(self.buttonGroup_NGram_Classification.checkedButton().text(),
                                                      pd.np.nan)

            self.dataframe_vocabNGram = self._set_dataframeItemValue(self.dataframe_vocabNGram, token, new_alias, new_clf, new_notes)
            self.tableWidget_Ngram_TagContainer.set_dataframe(self.dataframe_vocabNGram)

            self.tableWidget_Ngram_TagContainer.printDataframe_tableView()
            self.update_progress_bar(self.progressBar_Ngram_TagComplete, self.dataframe_vocabNGram)
            self.tableWidget_Ngram_TagContainer.selectRow(self.tableWidget_Ngram_TagContainer.currentRow() + 1)

        except (IndexError, ValueError):
            Qw.QMessageBox.about(self, 'Can\'t select', "You should select a row first")
        pass

    def onSliderMoved_similarityPattern(self):
        """when the slider change, print the good groupboxes
        :return:

        Parameters
        ----------

        Returns
        -------

        """
        btn_checked = []
        for btn in self.buttonGroup_1Gram_similarityPattern.checkedButtons():
            btn_checked.append(btn.text())

        try:
            token = self.tableWidget_1gram_TagContainer.selectedItems()[0].text()
            matches = self._get_similarityMatches(token)
            self.buttonGroup_1Gram_similarityPattern.set_checkBoxes_rechecked(matches, btn_checked)

        except IndexError:
            Qw.QMessageBox.about(self, 'Can\'t select', "You should select a row first")

    def _set_dataframeItemValue(self, dataframe, token, alias, classification, notes):
        """update the value of the dataframe

        Parameters
        ----------
        dataframe :
            param token:
        alias :
            param classification:
        notes :
            return:
        token :
            
        classification :
            

        Returns
        -------

        """
        dataframe.loc[token,"alias"] = alias
        dataframe.loc[token,"notes"] = notes
        dataframe.loc[token,"NE"] = classification
        return dataframe

    def _set_tokenExtractor(self, tokenExtractor_1Gram = None, tokenExtractor_nGram=None):
        """set both token extractore
        Needed for the report tab

        Parameters
        ----------
        tokenExtractor_1Gram :
             (Default value = None)
        tokenExtractor_nGram :
             (Default value = None)

        Returns
        -------

        """
        if tokenExtractor_1Gram is not None:
            self.tokenExtractor_1Gram = tokenExtractor_1Gram
        if tokenExtractor_nGram is not None:
            self.tokenExtractor_nGram = tokenExtractor_nGram

    def _set_cleanRawText(self, clean_rawText=None, clean_rawText_1Gram=None):
        """set the clean raw text
        Needed for the report tab

        Parameters
        ----------
        clean_rawText :
            param clean_rawText_1Gram: (Default value = None)
        clean_rawText_1Gram :
             (Default value = None)

        Returns
        -------

        """
        if clean_rawText is not None:
            self.clean_rawText= clean_rawText
        if clean_rawText_1Gram is not None:
            self.clean_rawText_1Gram=clean_rawText_1Gram

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
        #TODO THURSTON which one?
        #completed_pct = pd.np.log(matched+1).sum()/pd.np.log(self.scores+1).sum()
        completed_pct = matched.sum()/scores.sum()
        progressBar.setValue(100*completed_pct)

    def _set_editorValue_1Gram(self, alias, token, notes, classification):
        """print all the information from the token to the right layout 1Gram
        (alias, button, notes)

        Parameters
        ----------
        alias :
            param token:
        notes :
            param classification:
        token :
            
        classification :
            

        Returns
        -------

        """

        #alias
        if alias is '':
            self.lineEdit_1gram_AliasEditor.setText(token)
        else:
            self.lineEdit_1gram_AliasEditor.setText(alias)

        #notes
        self.textEdit_1gram_NoteEditor.setText(notes)

        #classification
        btn = self.classificationDictionary_1Gram.get(classification)
        try:
            btn.toggle()  # toggle that button
        except AttributeError:
            self.radioButton_1gram_NotClassifiedEditor.toggle()

    def _set_editorValue_NGram(self, alias, token, notes, classification):
        """print all the information from the token to the right layout NGram
        (alias, button, notes)

        Parameters
        ----------
        alias :
            
        token :
            
        notes :
            
        classification :
            

        Returns
        -------

        """
        # alias
        if alias is '':
            self.lineEdit_Ngram_AliasEditor.setText(token)
        else:
            self.lineEdit_Ngram_AliasEditor.setText(alias)

        # notes
        self.textEdit_Ngram_NoteEditor.setText(notes)

        # classification
        btn = self.classificationDictionary_NGram.get(classification)
        try:
            btn.toggle()  # toggle that button
        except AttributeError:
            self.radioButton_Ngram_NotClassifiedEditor.toggle()

    def _get_similarityMatches(self, token):
        """get the list of token similar to the given token

        Parameters
        ----------
        token :
            return:

        Returns
        -------

        """

        # TODO THURSTON which one should we keep
        # method 1: only find related terms with same 1st letter (way, way less computation)
        mask = self.dataframe_vocab1Gram.index.str[0] == token[0]
        matches = zz.extractBests(token, self.dataframe_vocab1Gram.index[mask],
                                  limit=20)[:int(self.horizontalSlider_1gram_FindingThreshold.value() * 20 / 100)]

        # # method 2: find all matching terms
        # matches = self.alias_lookup[token][:int(self.horizontalSlider_1gram_FindingThreshold.value()*1/10)]

        return matches

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
                self.onClick_updateButton_1Gram()
            elif self.tabWidget.currentIndex() ==1:
                self.onClick_updateButton_NGram()


    def closeEvent(self, event):
        """trigger when we close the window

        Parameters
        ----------
        event :
            return:

        Returns
        -------

        """
        #self.closeFunction(event)

        pass

    def close_Dialog(self):
        print("oulala")
        self.setEnabled(True)



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



