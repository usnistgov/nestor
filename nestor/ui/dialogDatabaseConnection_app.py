from simplecrypt import encrypt, decrypt
import neo4j
import webbrowser
from pathlib import Path


from database_storage.database.database import DatabaseNeo4J
from database_storage import main as cypherQuery
from  database_storage.helper import openYAMLFile

from PyQt5.QtCore import Qt
from PyQt5 import QtGui, uic
import PyQt5.QtWidgets as Qw



script_dir = Path(__file__).parent
fname4 = 'dialogDatabaseConnection.ui'
Ui_MainWindow_DatabaseConnection, QtBaseClass_DialogDatabaseConnection = uic.loadUiType(script_dir/fname4)

class DialogDatabaseConnection(Qw.QDialog, Ui_MainWindow_DatabaseConnection):

    def __init__(self, original_df, bin1g_df, binNg_df, vocab1g_df, vocabNg_df, csvHeaderMapping, csvHeaderOriginal,  iconPath=None):
        Qw.QDialog.__init__(self)
        Ui_MainWindow_DatabaseConnection.__init__(self)
        self.setupUi(self)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.original_df = original_df
        self.bin1g_df = bin1g_df
        self.binNg_df = binNg_df
        self.vocab1g_df = vocab1g_df
        self.vocabNg_df = vocabNg_df

        #ici tu fait le reverse !!!

        self.set_csvHeader(csvHeaderMapping, csvHeaderOriginal)

        self.database = None

        if iconPath:
            self.setWindowIcon(QtGui.QIcon(iconPath))

        self.lineEdit_DialogDatabaseConnection_ConnectInfo.setText('Not connected to any database')

        self.lineEdit_DialogDatabaseConnection_Username.setText("neo4j")
        self.lineEdit_DialogDatabaseConnection_Password.setText("GREYSTONE!!")
        self.lineEdit_DialogDatabaseConnection_ServerName.setText("localhost")
        self.lineEdit_DialogDatabaseConnection_ServerPortNumber.setText("7687")
        self.lineEdit_DialogDatabaseConnection_BrowserPortNumber.setText("7474")
        self.lineEdit_DialogDatabaseConnection_OpenSchema.setText("/Users/sam11/Git/nestor/database_storage/database/DatabaseSchema.yaml")


        self.checkBox_DialogDatabaseConnection_OriginalData.clicked.connect(self.check_checkBoxGroup)
        self.checkBox_DialogDatabaseConnection_Tag1g.clicked.connect(self.check_checkBoxGroup)
        self.checkBox_DialogDatabaseConnection_TagNg.clicked.connect(self.check_checkBoxGroup)
        self.checkBox_DialogDatabaseConnection_1gToNg.clicked.connect(self.check_checkBoxGroup)
        self.checkBox_DialogDatabaseConnection_IssueToItem.clicked.connect(self.check_checkBoxGroup)
        self.checkBox_DialogDatabaseConnection_ItemToItem.clicked.connect(self.check_checkBoxGroup)

        self.pushButton_DialogDatabaseConnection_OpenSchema.clicked.connect(self.onClick_openSchema)
        self.pushButton_DialogDatabaseConnection_Connect.clicked.connect(self.onClick_connectDatabase)
        self.pushButton_DialogDatabaseConnection_RunQueries.clicked.connect(self.onClick_runQuery)
        self.pushButton_DialogDatabaseConnection_DeleteData.clicked.connect(self.onClick_removeData)
        self.pushButton_DialogDatabaseConnection_OpenDatabaseBrowser.clicked.connect(self.onClick_openDatabase)


        self.pushButton_DialogDatabaseConnection_RunQueries.setEnabled(True)


    def set_csvHeader(self, csvHeaderMapping, csvHeaderOriginal):

        for key1, value1 in csvHeaderOriginal.items():
            for key2, value2 in value1.items():
                for keyO, valueO in csvHeaderMapping.items():
                    if valueO == value2:
                        csvHeaderOriginal[key1][key2] = keyO

        self.csv_header = csvHeaderOriginal


    def get_input(self):
        return  self.lineEdit_DialogDatabaseConnection_Username.text(), \
                encrypt('password', self.lineEdit_DialogDatabaseConnection_Password.text()),\
                self.lineEdit_DialogDatabaseConnection_OpenSchema.text(),\
                self.lineEdit_DialogDatabaseConnection_ServerName.text(),\
                self.lineEdit_DialogDatabaseConnection_ServerPortNumber.text(),\
                self.lineEdit_DialogDatabaseConnection_BrowserPortNumber.text()


    def onClick_openDatabase(self):

        username, password, schema_path, server, serverPort, browserPort = self.get_input()

        url = f'{server}:{browserPort}'

        webbrowser.open_new(url)


    def onClick_connectDatabase(self):

        self.pushButton_DialogDatabaseConnection_RunQueries.setEnabled(False)

        username, password, schema_path, server, serverPort, browserPort = self.get_input()
        uri = f'bolt://{server}:{serverPort}'


        try:
            schema = openYAMLFile(schema_path)

            self.database = DatabaseNeo4J(user = username,
                                 password=decrypt('password', password).decode('utf8'),
                                 uri=uri,
                                 schema=schema)

            self.lineEdit_DialogDatabaseConnection_ConnectInfo.setText(
                f'Connection created')


            self.pushButton_DialogDatabaseConnection_RunQueries.setEnabled(True)
            self.pushButton_DialogDatabaseConnection_DeleteData.setEnabled(True)



        except (neo4j.exceptions.AddressError, neo4j.exceptions.ServiceUnavailable):
            self.lineEdit_DialogDatabaseConnection_ConnectInfo.setText(
                f'FAIL to connect to the server or port')
            self.database = None

        except neo4j.exceptions.AuthError:
            self.lineEdit_DialogDatabaseConnection_ConnectInfo.setText(
                f'FAIL during authentication for username or password')
            self.database = None

        except FileNotFoundError:
            self.lineEdit_DialogDatabaseConnection_ConnectInfo.setText(
                f'FAIL cannot open the file {schema_path}')
            self.database = None

        self.check_checkBoxGroup()

    def onClick_runQuery(self):

        self.database.dropConstraints()
        self.database.dropIndexes()
        self.database.createIndexes()
        self.database.createConstraints()


        self.setEnabled(False)
        self.lineEdit_DialogDatabaseConnection_ConnectInfo.setText(
            f'Please wait while storing your data onto the database!!')

        df_original = self.original_df.fillna("")

        self.progressBar_DialogDatabaseConnection_RunQueries.setValue(10)

        Qw.QApplication.processEvents()

        if self.checkBox_DialogDatabaseConnection_OriginalData.isChecked():
            self.database.runQueries(cypherQuery.cypherCreate_historicalMaintenanceWorkOrder(
                schema=self.database.schema,
                originalDataframe=df_original,
                propertyToHeader_dict=self.csv_header
            ))
            print("\nDONE -----> Data from Original CSV Work Order stored !!")

        self.progressBar_DialogDatabaseConnection_RunQueries.setValue(30)
        Qw.QApplication.processEvents()


        if self.checkBox_DialogDatabaseConnection_Tag1g.isChecked():
            self.database.runQueries(cypherQuery.cypherCreate_tag(
                schema=self.database.schema,
                dataframe=self.bin1g_df,
                vocab1g=self.vocab1g_df,
                vocabNg=self.vocabNg_df
            ))
            print("\nDONE -----> Data from Tag1g Stored!!")
        self.progressBar_DialogDatabaseConnection_RunQueries.setValue(60)
        Qw.QApplication.processEvents()

        if self.checkBox_DialogDatabaseConnection_TagNg.isChecked():
            self.database.runQueries(cypherQuery.cypherCreate_tag(
                schema=self.database.schema,
                dataframe=self.binNg_df,
                vocab1g=self.vocab1g_df,
                vocabNg=self.vocabNg_df
            ))
            print("\nDONE ----->  Data from TagNg stored !!")
        self.progressBar_DialogDatabaseConnection_RunQueries.setValue(90)
        Qw.QApplication.processEvents()

        if self.checkBox_DialogDatabaseConnection_1gToNg.isChecked():
            self.database.runQueries(cypherQuery.cypherLink_Ngram1gram(
                schema=self.database.schema
            ))
            print("\nDONE ----->  TagNg --> Tag1g link created !!")


        if self.checkBox_DialogDatabaseConnection_IssueToItem.isChecked():
            self.database.runQueries(cypherQuery.cypherLink_itemIssue(
                schema=self.database.schema
            ))
            print("\nDONE ----->  item -> issue link upated !!")

        if self.checkBox_DialogDatabaseConnection_ItemToItem.isChecked():
            # self.database.runQueries(cypherQuery.cypherCreate_itemsTree(
            #     schema=self.database.schema
            # ))
            print("DONE ----->  Item hierarchy created !!")

        self.progressBar_DialogDatabaseConnection_RunQueries.setValue(100)

        self.lineEdit_DialogDatabaseConnection_ConnectInfo.setText(
            f'All your data have been stored!!')

        self.setEnabled(True)
        Qw.QApplication.processEvents()

    def check_checkBoxGroup(self):

        if self.database is not None and self.original_df is not None and self.csv_header is not None:
            self.checkBox_DialogDatabaseConnection_OriginalData.setEnabled(True)
        else:
            self.checkBox_DialogDatabaseConnection_OriginalData.setEnabled(False)
            self.checkBox_DialogDatabaseConnection_OriginalData.setChecked(False)

        if self.checkBox_DialogDatabaseConnection_OriginalData.isChecked() and self.vocab1g_df is not None and self.vocabNg_df is not None:
            if self.bin1g_df is not None:
                self.checkBox_DialogDatabaseConnection_Tag1g.setEnabled(True)
            else:
                self.checkBox_DialogDatabaseConnection_Tag1g.setEnabled(False)
                self.checkBox_DialogDatabaseConnection_Tag1g.setChecked(False)

            if self.binNg_df is not None:
                self.checkBox_DialogDatabaseConnection_TagNg.setEnabled(True)
            else:
                self.checkBox_DialogDatabaseConnection_TagNg.setEnabled(False)
                self.checkBox_DialogDatabaseConnection_TagNg.setChecked(False)
        else:
            self.checkBox_DialogDatabaseConnection_Tag1g.setEnabled(False)
            self.checkBox_DialogDatabaseConnection_Tag1g.setChecked(False)
            self.checkBox_DialogDatabaseConnection_TagNg.setEnabled(False)
            self.checkBox_DialogDatabaseConnection_TagNg.setChecked(False)

        if self.checkBox_DialogDatabaseConnection_Tag1g.isChecked() and self.checkBox_DialogDatabaseConnection_TagNg.isChecked():
            self.checkBox_DialogDatabaseConnection_1gToNg.setEnabled(True)
        else:
            self.checkBox_DialogDatabaseConnection_1gToNg.setEnabled(False)
            self.checkBox_DialogDatabaseConnection_1gToNg.setChecked(False)


        if self.checkBox_DialogDatabaseConnection_1gToNg.isChecked():
            self.checkBox_DialogDatabaseConnection_IssueToItem.setEnabled(True)
        else:
            self.checkBox_DialogDatabaseConnection_IssueToItem.setEnabled(False)
            self.checkBox_DialogDatabaseConnection_IssueToItem.setChecked(False)

        if self.checkBox_DialogDatabaseConnection_Tag1g.isChecked():
            self.checkBox_DialogDatabaseConnection_ItemToItem.setEnabled(True)
        else:
            self.checkBox_DialogDatabaseConnection_ItemToItem.setEnabled(False)
            self.checkBox_DialogDatabaseConnection_ItemToItem.setChecked(False)

    def onClick_removeData(self):
        dialog_sure = Qw.QMessageBox.question(self, 'Dalate Data', "Are you sure you want to remove your data??",
                                           Qw.QMessageBox.Yes | Qw.QMessageBox.No, Qw.QMessageBox.No)
        if dialog_sure == Qw.QMessageBox.Yes:
            self.database.deleteData()
            print('We delete your data.')
        else:
            print('We are NOT going to remove your data.')


    def onClick_openSchema(self):

        options = Qw.QFileDialog.Options()
        fileName, _ = Qw.QFileDialog.getOpenFileName(self, self.lineEdit_DialogDatabaseConnection_OpenSchema.objectName(), "",
                                                     "YAML Files (*.yaml *.yml)", options=options)
        if fileName:
            self.lineEdit_DialogDatabaseConnection_OpenSchema.setText(fileName)


