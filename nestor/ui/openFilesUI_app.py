from pathlib import Path
import os
import sys

from PyQt5 import uic, QtGui
from PyQt5.QtCore import Qt
import PyQt5.QtWidgets as Qw


fname = 'openFilesUI.ui'
qtDesignerFile_openFiles = Path('nestor/ui')/fname
Ui_MainWindow_openFiles, QtBaseClass_openFiles = uic.loadUiType(str(qtDesignerFile_openFiles))


class MyOpenFilesWindow(Qw.QMainWindow, Ui_MainWindow_openFiles):

    def __init__(self, iconPath=None, closeFunction=None, nextWindow=None):
        Qw.QMainWindow.__init__(self)
        Ui_MainWindow_openFiles.__init__(self)
        self.setupUi(self)
        self.setGeometry(20, 20, 544, 433)
        self.closeFunction = closeFunction
        self.nextWindowFunction = nextWindow
        if iconPath:
            self.setWindowIcon(QtGui.QIcon(iconPath))

        self.lineEdit_openFiles_numberTokenShow.setInputMask('99999')
        self.lineEdit_openFiles_SimilarityAlreadyChecked.setInputMask('99')
        self.pushButton_openFiles_OriginalCSV.clicked.connect(
            lambda: self.onClick_openFile(self.lineEdit_openFiles_OriginalCSV))
        self.pushButton_openFiles_1GramCSV.clicked.connect(
            lambda: self.onClick_openFile(self.lineEdit_openFiles_1GramCSV))
        self.pushButton_openFiles_NgramCSV.clicked.connect(
            lambda: self.onClick_openFile(self.lineEdit_openFiles_NgramCSV))
        self.pushButton_openFiles_RemoveOriginalCSV.clicked.connect(
            lambda : self.onClick_removePath(self.lineEdit_openFiles_OriginalCSV))
        self.pushButton_openFiles_Remove1GramCSV.clicked.connect(
            lambda: self.onClick_removePath(self.lineEdit_openFiles_1GramCSV))
        self.pushButton_openFiles_RemoveNgramCSV.clicked.connect(
            lambda: self.onClick_removePath(self.lineEdit_openFiles_NgramCSV))

        self.horizontalSlider_openFiles_similarityMatrixThreshold.sliderMoved.connect(self.onSlider_similarityMatrixThreshold)
        self.horizontalSlider_openFiles_similarityMatrixThreshold.sliderReleased.connect(self.onSlider_similarityMatrixThreshold)

        #self.pushButton_openFiles_Save.clicked.connect(self.onClick_Save)
        self.pushButton_openFiles_Reset.clicked.connect(self.onClick_Reset)

        self.pushButton_openFiles_Save.clicked.connect(self.nextWindowFunction)

    def onSlider_similarityMatrixThreshold(self):
        self.label_openFiles_similarityMatrixThresholdValue.setText(
            str(100 - self.horizontalSlider_openFiles_similarityMatrixThreshold.value()) + '%')

    def onClick_removePath(self, lineEdit):
        """when click on a X button remove the file path

        Parameters
        ----------
        lineEdit :
            return:

        Returns
        -------

        """
        lineEdit.setText("")

    def onClick_openFile(self, lineEdit):
        """Action when you click on the open files
        it need an argument so use lambda in the connect function

        Parameters
        ----------
        lineEdit :
            return:

        Returns
        -------

        """
        options = Qw.QFileDialog.Options()
        fileName, _ = Qw.QFileDialog.getOpenFileName(self, lineEdit.objectName(), "",
                                                  "CSV Files (*.csv)", options=options)
        if fileName:
            lineEdit.setText(fileName)

    def onClick_Reset(self):
        """Action when click on reset button
        remove all text in LineEdit
        :return:

        Parameters
        ----------

        Returns
        -------

        """
        self.onClick_removePath(self.lineEdit_openFiles_OriginalCSV)
        self.onClick_removePath(self.lineEdit_openFiles_1GramCSV)
        self.onClick_removePath(self.lineEdit_openFiles_NgramCSV)


    def set_config(self, config):
        """add to the window the values from the config dict

        Parameters
        ----------
        config :
            return:

        Returns
        -------

        """

        self.lineEdit_openFiles_OriginalCSV.setText(config['file']['filePath_OriginalCSV']['path'])
        self.lineEdit_openFiles_1GramCSV.setText(config['file']['filePath_1GrammCSV']['path'])
        self.lineEdit_openFiles_NgramCSV.setText(config['file']['filePath_nGrammCSV']['path'])
        self.lineEdit_openFiles_numberTokenShow.setText(str(config['value']['numberToken_show']))
        self.horizontalSlider_openFiles_similarityMatrixThreshold.setValue(config['value']['similarityMatrix_threshold'])
        self.label_openFiles_similarityMatrixThresholdValue.setText(str(config['value']['similarityMatrix_threshold']) + '%')
        # self.lineEdit_openFiles_SimilarityAlreadyChecked.setText(str(config['value']['similarityMatrix_alreadyChecked']))

    def get_config(self, config):
        """replace the given config dict with a new one based on the window values
        
        it is call when we save the view
        :return:

        Parameters
        ----------
        config :
            

        Returns
        -------

        """
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
            config['value']['similarityMatrix_alreadyChecked'] = int(self.lineEdit_openFiles_SimilarityAlreadyChecked.text())

            return True, config

        else:
            Qw.QMessageBox.about(self, 'Can\'t save', "You should open all the file first")
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

    # def closeEvent(self, event):
    #     """
    #     trigger when we close the window
    #     :param event:
    #     :return:
    #     """
    #
    #     self.closeFunction(self)


if __name__ == "__main__":
    app = Qw.QApplication(sys.argv)
    window = MyOpenFilesWindow()
    window.show()
    sys.exit(app.exec_())

