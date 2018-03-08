import sys
import PyQt5.QtWidgets as Qw

from app.taggingUI.openFilesUI_skeleton import Ui_MainWindow_openFiles


class MyOpenFilesWindow(Qw.QMainWindow, Ui_MainWindow_openFiles):

    def __init__(self):
        Qw.QMainWindow.__init__(self)
        self.setupUi(self)

        self.lineEdit_openFiles_numberTokenShow.setInputMask('9999')

        self.pushButton_openFiles_OriginalCSV.clicked.connect(
            lambda: self.onClick_openFile(self.lineEdit_openFiles_OriginalCSV))
        self.pushButton_openFiles_1GramCSV.clicked.connect(
            lambda: self.onClick_openFile(self.lineEdit_openFiles_1GramCSV))
        self.pushButton_openFiles_NgramCSV.clicked.connect(
            lambda: self.onClick_openFile(self.lineEdit_openFiles_NgramCSV))

        #self.pushButton_openFiles_Save.clicked.connect(self.onClick_Save)
        self.pushButton_openFiles_Reset.clicked.connect(self.onClick_Reset)

    def onClick_openFile(self, lineEdit):
        """
        Action when you click on the open files
        it need an argument so use lambda in the connect function
        :param lineEdit:
        :return:
        """
        options = Qw.QFileDialog.Options()
        fileName, _ = Qw.QFileDialog.getOpenFileName(self, lineEdit.objectName(), "",
                                                  "CSV Files (*.csv)", options=options)
        if fileName:
            lineEdit.setText(fileName)

    def get_AllFilesPath(self):
        """
        Action when saving the files
        if some are empty it create a messageBox
        after saving we open the header selected UI
        :return:
        """
        if self.lineEdit_openFiles_OriginalCSV.text()\
                and self.lineEdit_openFiles_1GramCSV.text()\
                and self.lineEdit_openFiles_NgramCSV.text():
            self.filePath_OriginalCSV = self.lineEdit_openFiles_OriginalCSV.text()
            self.filePath_1GrammCSV = self.lineEdit_openFiles_1GramCSV.text()
            self.filePath_nGrammCSV = self.lineEdit_openFiles_NgramCSV.text()

            return True, self.filePath_OriginalCSV, self.filePath_1GrammCSV, self.filePath_nGrammCSV

        else:
            Qw.QMessageBox.about(self, 'Can\'t save', "You should open all the file first")
            return False, None, None, None

    def onClick_Reset(self):
        """
        Action when click on reset button
        remove all text in LineEdit
        :return:
        """
        self.lineEdit_openFiles_OriginalCSV.setText("")
        self.lineEdit_openFiles_1GramCSV.setText("")
        self.lineEdit_openFiles_NgramCSV.setText("")

    def set_config_values(self, config):
        """
        add to the linEdit the value stored inside the config file
        :param config:
        :return:
        """
        self.lineEdit_openFiles_OriginalCSV.setText(config['file']['filePath_OriginalCSV']['path'])
        self.lineEdit_openFiles_1GramCSV.setText(config['file']['filePath_1GrammCSV']['path'])
        self.lineEdit_openFiles_NgramCSV.setText(config['file']['filePath_nGrammCSV']['path'])
        self.lineEdit_openFiles_numberTokenShow.setText(str(config['value']['numberToken_show']))
        self.horizontalSlider__openFiles_similarityMatrixThreshold.setValue(config['value']['similarityMatrix_threshold'])

    def get_config_value(self, config):
        """
        update the new config file dictionary
        :param config:
        :return:
        """
        config['file']['filePath_OriginalCSV']['path'] = self.lineEdit_openFiles_OriginalCSV.text()
        config['file']['filePath_1GrammCSV']['path'] = self.lineEdit_openFiles_1GramCSV.text()
        config['file']['filePath_nGrammCSV']['path'] = self.lineEdit_openFiles_NgramCSV.text()
        config['value']['numberToken_show'] = self.lineEdit_openFiles_numberTokenShow.text
        config['value']['similarityMatrix_threshold'] = self.horizontalSlider__openFiles_similarityMatrixThreshold.value()

        return config


if __name__ == "__main__":
    app = Qw.QApplication(sys.argv)
    window = MyOpenFilesWindow()
    window.show()
    sys.exit(app.exec_())

