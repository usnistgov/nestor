import sys
from PyQt5.QtCore import QCoreApplication, Qt, QSize
from PyQt5 import QtGui
import PyQt5.QtWidgets as Qw
import csv
import sip

sip.setapi('QString', 2)
sip.setapi('QVariant', 2)
from app.kpi_window.KPI_window_skeleton import Ui_KPIWindow


class LayoutKpiSelection():
    def __init__(self, parent_layout, dict):
        self.GLayout = Qw.QGridLayout(parent_layout)
        self.dict = dict

    def print_form_property(self):
        for key, properties in self.dict:
            QLabel_key = QLabel(self.GLayout)
            QLabel_key.setText(key)
            print(key)
            self.GLayout.addWidget(QLabel_key, collumn = 0 )



class MyWindow(Qw.QMainWindow, Ui_KPIWindow):
    def __init__(self, database=None):
        Qw.QMainWindow.__init__(self)
        self.setupUi(self)

        self.database = database

        # self.hLayoutGeneral.addLayout(LayoutKpiSelection(MWO.get_dict_database_structure(self.database)))

        dict = {'Human': {'name'},
                'Issue': {'date_maintenance_work_order_close',
                          'date_maintenance_work_order_issue',
                          'description_of_problem',
                          'description_of_solution',
                          'machine_down',
                          'part_in_process'},
                'Item': {'keyword'},
                'Machine': {'name'},
                'Operator': {'name'},
                'Problem': {'keyword'},
                'Solution': {'keyword'},
                'Tag': {'keyword'},
                'Technician': {'name'},
                'Technician and Operator': {'name'}}

        self.Glayout_properties_selection = LayoutKpiSelection(self.horizontalLayoutWidget, dict)

    def close_application(self):
        # this running means somewhere, an option to leave has been clicked
        choice = Qw.QMessageBox.question(self, 'Shut it Down',
                                         'Are you sure?',
                                         Qw.QMessageBox.Yes | Qw.QMessageBox.No)
        if choice == Qw.QMessageBox.Yes:
            print('exiting program...')
            sys.exit()
        else:
            pass


if __name__ == "__main__":
    app = Qw.QApplication(sys.argv)
    # database = DatabaseNeo4J("bolt://127.0.0.1:7687", "neo4j", 'GREYSTONE!!')
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())


