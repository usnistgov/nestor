# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'openFilesUI.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow_openFiles(object):
    def setupUi(self, MainWindow_openFiles):
        MainWindow_openFiles.setObjectName("MainWindow_openFiles")
        MainWindow_openFiles.resize(651, 571)
        self.centralwidget = QtWidgets.QWidget(MainWindow_openFiles)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout_openFiles_OriginalCSV = QtWidgets.QGridLayout()
        self.gridLayout_openFiles_OriginalCSV.setObjectName("gridLayout_openFiles_OriginalCSV")
        self.label_openFiles_OriginalCSV = QtWidgets.QLabel(self.centralwidget)
        self.label_openFiles_OriginalCSV.setObjectName("label_openFiles_OriginalCSV")
        self.gridLayout_openFiles_OriginalCSV.addWidget(self.label_openFiles_OriginalCSV, 0, 0, 1, 1)
        self.lineEdit_openFiles_OriginalCSV = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_openFiles_OriginalCSV.setEnabled(False)
        self.lineEdit_openFiles_OriginalCSV.setObjectName("lineEdit_openFiles_OriginalCSV")
        self.gridLayout_openFiles_OriginalCSV.addWidget(self.lineEdit_openFiles_OriginalCSV, 1, 0, 1, 1)
        self.pushButton_openFiles_OriginalCSV = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_openFiles_OriginalCSV.setObjectName("pushButton_openFiles_OriginalCSV")
        self.gridLayout_openFiles_OriginalCSV.addWidget(self.pushButton_openFiles_OriginalCSV, 1, 2, 1, 1)
        self.pushButton_openFiles_RemoveOriginalCSV = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_openFiles_RemoveOriginalCSV.setObjectName("pushButton_openFiles_RemoveOriginalCSV")
        self.gridLayout_openFiles_OriginalCSV.addWidget(self.pushButton_openFiles_RemoveOriginalCSV, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_openFiles_OriginalCSV)
        self.line1 = QtWidgets.QFrame(self.centralwidget)
        self.line1.setFrameShape(QtWidgets.QFrame.HLine)
        self.line1.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line1.setObjectName("line1")
        self.verticalLayout.addWidget(self.line1)
        self.gridLayout_openFiles_1GramCSV = QtWidgets.QGridLayout()
        self.gridLayout_openFiles_1GramCSV.setObjectName("gridLayout_openFiles_1GramCSV")
        self.lineEdit_openFiles_1GramCSV = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_openFiles_1GramCSV.setEnabled(False)
        self.lineEdit_openFiles_1GramCSV.setObjectName("lineEdit_openFiles_1GramCSV")
        self.gridLayout_openFiles_1GramCSV.addWidget(self.lineEdit_openFiles_1GramCSV, 1, 0, 1, 1)
        self.pushButton_openFiles_1GramCSV = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_openFiles_1GramCSV.setObjectName("pushButton_openFiles_1GramCSV")
        self.gridLayout_openFiles_1GramCSV.addWidget(self.pushButton_openFiles_1GramCSV, 1, 2, 1, 1)
        self.label_openFiles_1GramCSV = QtWidgets.QLabel(self.centralwidget)
        self.label_openFiles_1GramCSV.setObjectName("label_openFiles_1GramCSV")
        self.gridLayout_openFiles_1GramCSV.addWidget(self.label_openFiles_1GramCSV, 0, 0, 1, 1)
        self.pushButton_openFiles_Remove1GramCSV = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_openFiles_Remove1GramCSV.setObjectName("pushButton_openFiles_Remove1GramCSV")
        self.gridLayout_openFiles_1GramCSV.addWidget(self.pushButton_openFiles_Remove1GramCSV, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_openFiles_1GramCSV)
        self.line2 = QtWidgets.QFrame(self.centralwidget)
        self.line2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line2.setObjectName("line2")
        self.verticalLayout.addWidget(self.line2)
        self.gridLayout_openFiles_NgramCSV = QtWidgets.QGridLayout()
        self.gridLayout_openFiles_NgramCSV.setObjectName("gridLayout_openFiles_NgramCSV")
        self.pushButton_openFiles_NgramCSV = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_openFiles_NgramCSV.setObjectName("pushButton_openFiles_NgramCSV")
        self.gridLayout_openFiles_NgramCSV.addWidget(self.pushButton_openFiles_NgramCSV, 2, 2, 1, 1)
        self.label_openFiles_NgramCSV = QtWidgets.QLabel(self.centralwidget)
        self.label_openFiles_NgramCSV.setObjectName("label_openFiles_NgramCSV")
        self.gridLayout_openFiles_NgramCSV.addWidget(self.label_openFiles_NgramCSV, 1, 0, 1, 1)
        self.lineEdit_openFiles_NgramCSV = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_openFiles_NgramCSV.setEnabled(False)
        self.lineEdit_openFiles_NgramCSV.setObjectName("lineEdit_openFiles_NgramCSV")
        self.gridLayout_openFiles_NgramCSV.addWidget(self.lineEdit_openFiles_NgramCSV, 2, 0, 1, 1)
        self.pushButton_openFiles_RemoveNgramCSV = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_openFiles_RemoveNgramCSV.setObjectName("pushButton_openFiles_RemoveNgramCSV")
        self.gridLayout_openFiles_NgramCSV.addWidget(self.pushButton_openFiles_RemoveNgramCSV, 2, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_openFiles_NgramCSV)
        self.line3 = QtWidgets.QFrame(self.centralwidget)
        self.line3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line3.setObjectName("line3")
        self.verticalLayout.addWidget(self.line3)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.gridLayout_openFiles_configValues = QtWidgets.QGridLayout()
        self.gridLayout_openFiles_configValues.setObjectName("gridLayout_openFiles_configValues")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_openFiles_configValues.addItem(spacerItem1, 0, 3, 1, 1)
        self.label_openFiles_similarityMatrixThreshold = QtWidgets.QLabel(self.centralwidget)
        self.label_openFiles_similarityMatrixThreshold.setObjectName("label_openFiles_similarityMatrixThreshold")
        self.gridLayout_openFiles_configValues.addWidget(self.label_openFiles_similarityMatrixThreshold, 0, 0, 1, 1, QtCore.Qt.AlignHCenter)
        self.horizontalSlider_openFiles_similarityMatrixThreshold = QtWidgets.QSlider(self.centralwidget)
        self.horizontalSlider_openFiles_similarityMatrixThreshold.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_openFiles_similarityMatrixThreshold.setObjectName("horizontalSlider_openFiles_similarityMatrixThreshold")
        self.gridLayout_openFiles_configValues.addWidget(self.horizontalSlider_openFiles_similarityMatrixThreshold, 1, 0, 1, 1)
        self.label_openFiles_similarityMatrixThresholdValue = QtWidgets.QLabel(self.centralwidget)
        self.label_openFiles_similarityMatrixThresholdValue.setEnabled(False)
        self.label_openFiles_similarityMatrixThresholdValue.setObjectName("label_openFiles_similarityMatrixThresholdValue")
        self.gridLayout_openFiles_configValues.addWidget(self.label_openFiles_similarityMatrixThresholdValue, 1, 1, 1, 1)
        self.label_openFiles_numberTokenShow = QtWidgets.QLabel(self.centralwidget)
        self.label_openFiles_numberTokenShow.setObjectName("label_openFiles_numberTokenShow")
        self.gridLayout_openFiles_configValues.addWidget(self.label_openFiles_numberTokenShow, 0, 4, 1, 1, QtCore.Qt.AlignHCenter)
        self.lineEdit_openFiles_numberTokenShow = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_openFiles_numberTokenShow.setMaximumSize(QtCore.QSize(100, 16777215))
        self.lineEdit_openFiles_numberTokenShow.setObjectName("lineEdit_openFiles_numberTokenShow")
        self.gridLayout_openFiles_configValues.addWidget(self.lineEdit_openFiles_numberTokenShow, 1, 4, 1, 1, QtCore.Qt.AlignHCenter)
        self.label_openFiles_SimilarityAlreadyChecked = QtWidgets.QLabel(self.centralwidget)
        self.label_openFiles_SimilarityAlreadyChecked.setObjectName("label_openFiles_SimilarityAlreadyChecked")
        self.gridLayout_openFiles_configValues.addWidget(self.label_openFiles_SimilarityAlreadyChecked, 0, 2, 1, 1)
        self.lineEdit_openFiles_SimilarityAlreadyChecked = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_openFiles_SimilarityAlreadyChecked.setMaximumSize(QtCore.QSize(50, 16777215))
        self.lineEdit_openFiles_SimilarityAlreadyChecked.setInputMethodHints(QtCore.Qt.ImhDigitsOnly)
        self.lineEdit_openFiles_SimilarityAlreadyChecked.setObjectName("lineEdit_openFiles_SimilarityAlreadyChecked")
        self.gridLayout_openFiles_configValues.addWidget(self.lineEdit_openFiles_SimilarityAlreadyChecked, 1, 2, 1, 1, QtCore.Qt.AlignHCenter)
        self.verticalLayout.addLayout(self.gridLayout_openFiles_configValues)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.horizontalLayout_openFiles_ActionButton = QtWidgets.QHBoxLayout()
        self.horizontalLayout_openFiles_ActionButton.setObjectName("horizontalLayout_openFiles_ActionButton")
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_openFiles_ActionButton.addItem(spacerItem3)
        self.pushButton_openFiles_Reset = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_openFiles_Reset.setObjectName("pushButton_openFiles_Reset")
        self.horizontalLayout_openFiles_ActionButton.addWidget(self.pushButton_openFiles_Reset)
        self.pushButton_openFiles_Save = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_openFiles_Save.setObjectName("pushButton_openFiles_Save")
        self.horizontalLayout_openFiles_ActionButton.addWidget(self.pushButton_openFiles_Save)
        self.verticalLayout.addLayout(self.horizontalLayout_openFiles_ActionButton)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        MainWindow_openFiles.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow_openFiles)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 651, 24))
        self.menubar.setObjectName("menubar")
        MainWindow_openFiles.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow_openFiles)
        self.statusbar.setObjectName("statusbar")
        MainWindow_openFiles.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow_openFiles)
        QtCore.QMetaObject.connectSlotsByName(MainWindow_openFiles)

    def retranslateUi(self, MainWindow_openFiles):
        _translate = QtCore.QCoreApplication.translate
        MainWindow_openFiles.setWindowTitle(_translate("MainWindow_openFiles", "Open Files"))
        self.label_openFiles_OriginalCSV.setText(_translate("MainWindow_openFiles", "Select your original csv file"))
        self.pushButton_openFiles_OriginalCSV.setText(_translate("MainWindow_openFiles", "open"))
        self.pushButton_openFiles_RemoveOriginalCSV.setText(_translate("MainWindow_openFiles", "X"))
        self.pushButton_openFiles_1GramCSV.setText(_translate("MainWindow_openFiles", "open"))
        self.label_openFiles_1GramCSV.setText(_translate("MainWindow_openFiles", "select the csv file to save your 1 gram token"))
        self.pushButton_openFiles_Remove1GramCSV.setText(_translate("MainWindow_openFiles", "X"))
        self.pushButton_openFiles_NgramCSV.setText(_translate("MainWindow_openFiles", "open"))
        self.label_openFiles_NgramCSV.setText(_translate("MainWindow_openFiles", "select the csv file to save your N gram token"))
        self.pushButton_openFiles_RemoveNgramCSV.setText(_translate("MainWindow_openFiles", "X"))
        self.label_openFiles_similarityMatrixThreshold.setText(_translate("MainWindow_openFiles", "Similarity threshold"))
        self.label_openFiles_similarityMatrixThresholdValue.setText(_translate("MainWindow_openFiles", "0%"))
        self.label_openFiles_numberTokenShow.setText(_translate("MainWindow_openFiles", "Number of tokens extracted"))
        self.lineEdit_openFiles_numberTokenShow.setText(_translate("MainWindow_openFiles", "1000"))
        self.label_openFiles_SimilarityAlreadyChecked.setText(_translate("MainWindow_openFiles", "Pattern already checked (%)"))
        self.lineEdit_openFiles_SimilarityAlreadyChecked.setText(_translate("MainWindow_openFiles", "99"))
        self.pushButton_openFiles_Reset.setText(_translate("MainWindow_openFiles", "clear all"))
        self.pushButton_openFiles_Save.setText(_translate("MainWindow_openFiles", "Next"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow_openFiles = QtWidgets.QMainWindow()
    ui = Ui_MainWindow_openFiles()
    ui.setupUi(MainWindow_openFiles)
    MainWindow_openFiles.show()
    sys.exit(app.exec_())

