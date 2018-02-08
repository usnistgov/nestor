# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'KPIWindow.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_KPIWindow(object):
    def setupUi(self, KPIWindow):
        KPIWindow.setObjectName("KPIWindow")
        KPIWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(KPIWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(9, 9, 781, 541))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.hLayoutGeneral = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.hLayoutGeneral.setContentsMargins(0, 0, 0, 0)
        self.hLayoutGeneral.setObjectName("hLayoutGeneral")
        KPIWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(KPIWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 22))
        self.menubar.setObjectName("menubar")
        KPIWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(KPIWindow)
        self.statusbar.setObjectName("statusbar")
        KPIWindow.setStatusBar(self.statusbar)

        self.retranslateUi(KPIWindow)
        QtCore.QMetaObject.connectSlotsByName(KPIWindow)

    def retranslateUi(self, KPIWindow):
        _translate = QtCore.QCoreApplication.translate
        KPIWindow.setWindowTitle(_translate("KPIWindow", "MainWindow"))



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())