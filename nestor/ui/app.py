from nestor.ui import mainwindow

from PyQt5.QtWidgets import QApplication, QMessageBox, qApp
from PyQt5 import QtCore
import sys
import traceback


def exception_handler(type_, value, traceback_):
    if qApp.thread() is QtCore.QThread.currentThread():
        p = traceback.format_exc()
        msg = QMessageBox()
        msg.setWindowTitle("Nestor has encountered an error")
        msg.setIcon(QMessageBox.Critical)
        msg.setText("An unhandled error occurred! Check the log for more detailed information...")
        msg.setDetailedText(p)
        msg.setEscapeButton(QMessageBox.Ok)
        msg.exec_()


def main():
    app = QApplication(sys.argv)

    stylesheet = """
        QGroupBox { 
            border: 1px solid gray;
            border-radius: 9px;
            margin-top: 0.5em;
            font-weight: bold;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 3px 0 3px;
        }
        """

    app.setStyleSheet(stylesheet)
    window = mainwindow.MainWindow()
    sys.excepthook = exception_handler
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
