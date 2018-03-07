# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'selectCSVHeadersUI.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow_selectCSVHeaders(object):
    def setupUi(self, MainWindow_selectCSVHeaders):
        MainWindow_selectCSVHeaders.setObjectName("MainWindow_selectCSVHeaders")
        MainWindow_selectCSVHeaders.resize(494, 478)
        self.centralwidget = QtWidgets.QWidget(MainWindow_selectCSVHeaders)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout_selectCSVHeaders_ActionButton = QtWidgets.QGridLayout()
        self.gridLayout_selectCSVHeaders_ActionButton.setObjectName("gridLayout_selectCSVHeaders_ActionButton")
        self.pushButton_selectCSVHeaders_save = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_selectCSVHeaders_save.setObjectName("pushButton_selectCSVHeaders_save")
        self.gridLayout_selectCSVHeaders_ActionButton.addWidget(self.pushButton_selectCSVHeaders_save, 1, 2, 1, 1, QtCore.Qt.AlignBottom)
        self.pushButton_selectCSVHeaders_checkAll = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_selectCSVHeaders_checkAll.setObjectName("pushButton_selectCSVHeaders_checkAll")
        self.gridLayout_selectCSVHeaders_ActionButton.addWidget(self.pushButton_selectCSVHeaders_checkAll, 1, 0, 1, 1)
        self.pushButton_selectCSVHeaders_uncheckAll = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_selectCSVHeaders_uncheckAll.setObjectName("pushButton_selectCSVHeaders_uncheckAll")
        self.gridLayout_selectCSVHeaders_ActionButton.addWidget(self.pushButton_selectCSVHeaders_uncheckAll, 1, 1, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_selectCSVHeaders_ActionButton, 2, 0, 1, 1)
        self.gridLayout_selectCSVHeaders_editor = QtWidgets.QGridLayout()
        self.gridLayout_selectCSVHeaders_editor.setObjectName("gridLayout_selectCSVHeaders_editor")
        self.gridLayout.addLayout(self.gridLayout_selectCSVHeaders_editor, 0, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 1, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        MainWindow_selectCSVHeaders.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow_selectCSVHeaders)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 494, 22))
        self.menubar.setObjectName("menubar")
        MainWindow_selectCSVHeaders.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow_selectCSVHeaders)
        self.statusbar.setObjectName("statusbar")
        MainWindow_selectCSVHeaders.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow_selectCSVHeaders)
        QtCore.QMetaObject.connectSlotsByName(MainWindow_selectCSVHeaders)

    def retranslateUi(self, MainWindow_selectCSVHeaders):
        _translate = QtCore.QCoreApplication.translate
        MainWindow_selectCSVHeaders.setWindowTitle(_translate("MainWindow_selectCSVHeaders", "MainWindow"))
        self.pushButton_selectCSVHeaders_save.setText(_translate("MainWindow_selectCSVHeaders", "save"))
        self.pushButton_selectCSVHeaders_checkAll.setText(_translate("MainWindow_selectCSVHeaders", "check all"))
        self.pushButton_selectCSVHeaders_uncheckAll.setText(_translate("MainWindow_selectCSVHeaders", "uncheck all"))

