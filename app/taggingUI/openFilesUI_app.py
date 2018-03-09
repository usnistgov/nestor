import sys
import os
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

        self.horizontalSlider_openFiles_similarityMatrixThreshold.sliderMoved.connect(self.onSlider_similarityMatrixThreshold)
        self.horizontalSlider_openFiles_similarityMatrixThreshold.sliderReleased.connect(self.onSlider_similarityMatrixThreshold)

        #self.pushButton_openFiles_Save.clicked.connect(self.onClick_Save)
        self.pushButton_openFiles_Reset.clicked.connect(self.onClick_Reset)

    def onSlider_similarityMatrixThreshold(self):
        self.label_openFiles_similarityMatrixThresholdValue.setText(
            str(self.horizontalSlider_openFiles_similarityMatrixThreshold.value()) + '%')


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

    def onClick_Reset(self):
        """
        Action when click on reset button
        remove all text in LineEdit
        :return:
        """
        self.lineEdit_openFiles_OriginalCSV.setText("")
        self.lineEdit_openFiles_1GramCSV.setText("")
        self.lineEdit_openFiles_NgramCSV.setText("")


    def set_config(self, config):
        """
        add to the window the values from the config dict
        :param config:
        :return:
        """

        self.lineEdit_openFiles_OriginalCSV.setText(config['file']['filePath_OriginalCSV']['path'])
        self.lineEdit_openFiles_1GramCSV.setText(config['file']['filePath_1GrammCSV']['path'])
        self.lineEdit_openFiles_NgramCSV.setText(config['file']['filePath_nGrammCSV']['path'])
        self.lineEdit_openFiles_numberTokenShow.setText(str(config['value']['numberToken_show']))
        self.horizontalSlider_openFiles_similarityMatrixThreshold.setValue(config['value']['similarityMatrix_threshold'])
        self.label_openFiles_similarityMatrixThresholdValue.setText(str(config['value']['similarityMatrix_threshold']) + '%')



    def get_config(self, config):
        """
        replace the given config dict with a new one based on the window values

        it is call when we save the view
        :return:
        """
        #TODO create new file if none is selected

        # if we are on a Windows machine
        if os.name == 'nt':
            separator = '\\'
        else:
            separator = '/'

        if self.lineEdit_openFiles_OriginalCSV.text():
            config['file']['filePath_OriginalCSV']['path'] = self.lineEdit_openFiles_OriginalCSV.text()
            path_list = config['file']['filePath_OriginalCSV']['path'].split(separator)
            name_list = path_list[-1].split('.')

            if self.lineEdit_openFiles_1GramCSV.text():
                config['file']['filePath_1GrammCSV']['path'] = self.lineEdit_openFiles_1GramCSV.text()
            else:
                path = path_list
                name = "_1Gram.".join(name_list)
                path[-1] = name
                path = separator.join(path)

                config['file']['filePath_1GrammCSV']['path'] = path

            if self.lineEdit_openFiles_NgramCSV.text():
                config['file']['filePath_nGrammCSV']['path'] = self.lineEdit_openFiles_NgramCSV.text()
            else :
                path = path_list
                name = "_nGram.".join(name_list)
                path[-1] = name
                path = separator.join(path)

                config['file']['filePath_nGrammCSV']['path'] = path

            config['value']['numberToken_show'] = self.lineEdit_openFiles_numberTokenShow.text()
            config['value']['similarityMatrix_threshold'] = self.horizontalSlider_openFiles_similarityMatrixThreshold.value()

            return True, config

        else:
            Qw.QMessageBox.about(self, 'Can\'t save', "You should open all the file first")
            return False, None



if __name__ == "__main__":
    app = Qw.QApplication(sys.argv)
    window = MyOpenFilesWindow()
    window.show()
    sys.exit(app.exec_())

