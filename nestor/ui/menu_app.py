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

sheetColor = {
    "blue": "color: rgb(27, 143, 255);",
    "red": "color: rgb(252, 21, 7);",
    "green": "color: rgb(28, 189, 27);"
}


script_dir = Path(__file__).parent
fname1 = 'dialogDatabaseConnection.ui'
Ui_MainWindow_DatabaseConnection, QtBaseClass_DialogDatabaseConnection = uic.loadUiType(script_dir/fname1)

class DialogDatabaseConnection(Qw.QDialog, Ui_MainWindow_DatabaseConnection):

    def __init__(self, iconPath=None):
        Qw.QDialog.__init__(self)
        Ui_MainWindow_DatabaseConnection.__init__(self)
        self.setupUi(self)

        #ici tu fait le reverse !!!

        # self.set_csvHeader(csvHeaderMapping, csvHeaderOriginal)

        self.database = None

        if iconPath:
            self.setWindowIcon(QtGui.QIcon(iconPath))

        self.lineEdit_DialogDatabaseConnection_ConnectInfo.setText('Not connected to any database')
        self.pushButton_DialogDatabaseConnection_OpenSchema.clicked.connect(self.onClick_openSchema)


        self.lineEdit_DialogDatabaseConnection_ConnectInfo.setStyleSheet(sheetColor['blue'])

    def get_input(self):
        return  self.lineEdit_DialogDatabaseConnection_Username.text(), \
                encrypt('password', self.lineEdit_DialogDatabaseConnection_Password.text()),\
                self.lineEdit_DialogDatabaseConnection_OpenSchema.text(),\
                self.lineEdit_DialogDatabaseConnection_ServerName.text(),\
                self.lineEdit_DialogDatabaseConnection_ServerPortNumber.text(),\
                self.lineEdit_DialogDatabaseConnection_BrowserPortNumber.text()


    def get_database(self):

        username, password, schema_path, server, serverPort, browserPort = self.get_input()
        uri = f'bolt://{server}:{serverPort}'


        try:
            schema = openYAMLFile(schema_path)

            database = DatabaseNeo4J(user = username,
                                 password=decrypt('password', password).decode('utf8'),
                                 uri=uri,
                                 schema=schema)

            self.lineEdit_DialogDatabaseConnection_ConnectInfo.setText(
                f'Connection created')

            self.lineEdit_DialogDatabaseConnection_ConnectInfo.setStyleSheet(sheetColor['green'])



        except (neo4j.exceptions.AddressError, neo4j.exceptions.ServiceUnavailable):
            self.lineEdit_DialogDatabaseConnection_ConnectInfo.setText(
                f'FAIL to connect to the server or port')
            database = None
            self.lineEdit_DialogDatabaseConnection_ConnectInfo.setStyleSheet(sheetColor['red'])


        except neo4j.exceptions.AuthError:
            self.lineEdit_DialogDatabaseConnection_ConnectInfo.setText(
                f'FAIL during authentication for username or password')
            database = None
            self.lineEdit_DialogDatabaseConnection_ConnectInfo.setStyleSheet(sheetColor['red'])



        except FileNotFoundError:
            self.lineEdit_DialogDatabaseConnection_ConnectInfo.setText(
                f'FAIL cannot open the file {schema_path}')
            database = None
            self.lineEdit_DialogDatabaseConnection_ConnectInfo.setStyleSheet(self.sheetColor['red'])

        return database


    def onClick_openSchema(self):

        options = Qw.QFileDialog.Options()
        fileName, _ = Qw.QFileDialog.getOpenFileName(self, self.lineEdit_DialogDatabaseConnection_OpenSchema.objectName(), "",
                                                     "YAML Files (*.yaml *.yml)", options=options)
        if fileName:
            self.lineEdit_DialogDatabaseConnection_OpenSchema.setText(fileName)


fname2 = 'dialogDatabaseRunQuery.ui'
Ui_MainWindow_DialogDatabaseRunQuery, QtBaseClass_DialogDatabaseRunQuery = uic.loadUiType(script_dir/fname2)

class DialogDatabaseRunQuery(Qw.QDialog, Ui_MainWindow_DialogDatabaseRunQuery):
    def __init__(self, database, original_df, csvHeaderOriginal, csvHeaderMapping, bin1g_df, binNg_df, vocab1g_df, vocabNg_df,  iconPath=None):
        Qw.QDialog.__init__(self)
        Ui_MainWindow_DialogDatabaseRunQuery.__init__(self)
        self.setupUi(self)

        self.database = database
        self.set_csvHeader(csvHeaderOriginal, csvHeaderMapping)

        self.original_df = original_df
        self.bin1g_df = bin1g_df
        self.binNg_df = binNg_df
        self.vocab1g_df = vocab1g_df
        self.vocabNg_df = vocabNg_df

        self.lineEdit_DialogDatabaseRunQuery_Info.setText(
            f'Wait for your input')
        self.lineEdit_DialogDatabaseRunQuery_Info.setStyleSheet(sheetColor['blue'])

        self.check_checkBoxGroup()

        self.pushButton_DialogDatabaseRunQuery_DeleteData.clicked.connect(self.onClick_removeData)
        self.pushButton_DialogDatabaseRunQuery_RunQueries.clicked.connect(self.onClick_runQuery)

        self.checkBox_DialogDatabaseRunQuery_OriginalData.clicked.connect(self.check_checkBoxGroup)
        self.checkBox_DialogDatabaseRunQuery_Tag1g.clicked.connect(self.check_checkBoxGroup)
        self.checkBox_DialogDatabaseRunQuery_TagNg.clicked.connect(self.check_checkBoxGroup)
        self.checkBox_DialogDatabaseRunQuery_1gToNg.clicked.connect(self.check_checkBoxGroup)
        self.checkBox_DialogDatabaseRunQuery_IssueToItem.clicked.connect(self.check_checkBoxGroup)
        self.checkBox_DialogDatabaseRunQuery_ItemToItem.clicked.connect(self.check_checkBoxGroup)


        if iconPath:
            self.setWindowIcon(QtGui.QIcon(iconPath))

    def set_csvHeader(self, csvHeaderOriginal, csvHeaderMapping):

        for key1, value1 in csvHeaderOriginal.items():
            for key2, value2 in value1.items():
                for keyO, valueO in csvHeaderMapping.items():
                    if valueO == value2:
                        csvHeaderOriginal[key1][key2] = keyO

        self.csv_header = csvHeaderOriginal


    def onClick_runQuery(self):

        self.database.dropConstraints()
        self.database.dropIndexes()
        self.database.createIndexes()
        self.database.createConstraints()


        self.setEnabled(False)
        self.lineEdit_DialogDatabaseRunQuery_Info.setText(
            f'Please wait while storing your data onto the database!!')
        self.lineEdit_DialogDatabaseRunQuery_Info.setStyleSheet(sheetColor['blue'])

        df_original = self.original_df.fillna("")

        self.progressBar_DialogDatabaseRunQuery_RunQueries.setValue(10)

        Qw.QApplication.processEvents()

        if self.checkBox_DialogDatabaseRunQuery_OriginalData.isChecked():
            self.database.runQueries(cypherQuery.cypherCreate_historicalMaintenanceWorkOrder(
                schema=self.database.schema,
                originalDataframe=df_original,
                propertyToHeader_dict=self.csv_header
            ))
            print("\nDONE -----> Data from Original CSV Work Order stored !!")

        self.progressBar_DialogDatabaseRunQuery_RunQueries.setValue(30)
        Qw.QApplication.processEvents()


        if self.checkBox_DialogDatabaseRunQuery_Tag1g.isChecked():
            self.database.runQueries(cypherQuery.cypherCreate_tag(
                schema=self.database.schema,
                dataframe=self.bin1g_df,
                vocab1g=self.vocab1g_df,
                vocabNg=self.vocabNg_df
            ))
            print("\nDONE -----> Data from Tag1g Stored!!")
        self.progressBar_DialogDatabaseRunQuery_RunQueries.setValue(60)
        Qw.QApplication.processEvents()

        if self.checkBox_DialogDatabaseRunQuery_TagNg.isChecked():
            self.database.runQueries(cypherQuery.cypherCreate_tag(
                schema=self.database.schema,
                dataframe=self.binNg_df,
                vocab1g=self.vocab1g_df,
                vocabNg=self.vocabNg_df
            ))
            print("\nDONE ----->  Data from TagNg stored !!")
        self.progressBar_DialogDatabaseRunQuery_RunQueries.setValue(90)
        Qw.QApplication.processEvents()

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

        self.progressBar_DialogDatabaseRunQuery_RunQueries.setValue(100)

        self.lineEdit_DialogDatabaseRunQuery_Info.setText(
            f'All your data have been stored!!')

        self.lineEdit_DialogDatabaseRunQuery_Info.setStyleSheet(sheetColor['green'])

        self.setEnabled(True)
        Qw.QApplication.processEvents()

    def check_checkBoxGroup(self):

        if self.database is not None and self.original_df is not None and self.csv_header is not None:
            self.checkBox_DialogDatabaseRunQuery_OriginalData.setEnabled(True)
        else:
            self.checkBox_DialogDatabaseRunQuery_OriginalData.setEnabled(False)
            self.checkBox_DialogDatabaseRunQuery_OriginalData.setChecked(False)

        if self.checkBox_DialogDatabaseRunQuery_OriginalData.isChecked() and self.vocab1g_df is not None and self.vocabNg_df is not None:
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

    def onClick_removeData(self):
        dialog_sure = Qw.QMessageBox.question(self, 'Dalate Data', "Are you sure you want to remove your data??",
                                           Qw.QMessageBox.Yes | Qw.QMessageBox.No, Qw.QMessageBox.No)
        if dialog_sure == Qw.QMessageBox.Yes:
            self.database.deleteData()
            self.lineEdit_DialogDatabaseRunQuery_Info.setText(
            f'All your data have been removed!!')
            print('We delete your data.')
        else:
            print('We are NOT going to remove your data.')


# Now the ToS dialog .ui file
fname3 = 'termsOfUse.ui'
qtDesignerFile_tosDialog = script_dir/fname3
Ui_MainWindow_tosDialog, QtBaseClass_tos_Dialog = uic.loadUiType(qtDesignerFile_tosDialog)


class TermsOfServiceDialog(Qw.QDialog, Ui_MainWindow_tosDialog):
    """Class to instantiate window showing NIST license. FUTURE: any other versioning information."""
    def __init__(self, iconPath=None, closeFunction=None):
        Qw.QDialog.__init__(self)
        Ui_MainWindow_tosDialog.__init__(self)
        self.setupUi(self)
        self.closeFunction = closeFunction

        if iconPath:
            self.setWindowIcon(QtGui.QIcon(iconPath))

