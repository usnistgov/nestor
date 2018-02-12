import sys
from PyQt5.QtCore import QCoreApplication, Qt, QSize
from PyQt5 import QtGui
import PyQt5.QtWidgets as Qw
import csv
import sip

sip.setapi('QString', 2)
sip.setapi('QVariant', 2)
from app.kpi_window.KPI_window_skeleton import Ui_KPIWindow


class LayoutKpiSelection:
    """
    an object that take care of the left part of the UI: the selection of the information
    The goal is to get all the properties from the given database,
    Print it
    allow the user to select the variable he wants to return
    filter on the data he wants

    when clicking on the Search button, it will send to the mainWindow : MyWindow
    the needed query to creat a pandas dataframe with the information
    """
    def __init__(self, layout, parent_layout, label_properties):
        """
        set the layout, the parent layout and the properties given by the mainWindow : MyWindow

        The properties are a dictionary with the name of the "node" and the properti inside
        The property is going to be generated dynamicly during the instantiation, it should not change

        :param layout:
        :param parent_layout:
        :param label_properties:
        """
        self.layout = layout
        self.parent_layout = parent_layout
        self.label_properties = label_properties
        self.rowX=0

        # create the label on the top of the layout
        self.groupCBox_selection = Qw.QButtonGroup()
        self.groupCBox_selection.setExclusive(False)
        self.LeftLabel_property = Qw.QLabel(self.parent_layout)
        self.LeftLabel_property.setText("Select the properties you want")
        self.LeftLabel_property.setObjectName("LeftLabel_property")
        self.layout.addWidget(self.LeftLabel_property, self.rowX, 0, 1, 1)

        # create all the information based on the properties
        self.print_form_property()

        # add a spacer to separate the properties from the search button
        self.rowX += 1
        spacerItem = Qw.QSpacerItem(20, 40, Qw.QSizePolicy.Minimum, Qw.QSizePolicy.Expanding)
        self.layout.addItem(spacerItem, self.rowX, 0, 1, 1)

        # add the Search button
        self.rowX += 1
        self.Left_PButton_search = Qw.QPushButton(self.parent_layout)
        self.Left_PButton_search.setText("Search")
        self.Left_PButton_search.setObjectName("Left_PButton_search")
        self.layout.addWidget(self.Left_PButton_search, self.rowX, 1, 2, 1)



    def print_form_property(self):
        """
        it print the view for the properties information based on the self.label_properties
        :return:
        """
        self.rowX += 1

        for label, properties in self.label_properties.items():

            #print the label of the node
            self.rowX += 1
            QLabel_label = Qw.QLabel()
            QLabel_label.setText(label)
            self.layout.addWidget(QLabel_label, self.rowX, 0)


            for property in properties:

                #print the check_box and the label for the properties in this node
                self.rowX += 1
                QCBox_select = Qw.QCheckBox(property, self.parent_layout)
                self.layout.addWidget(QCBox_select, self.rowX, 1)
                self.groupCBox_selection.addButton(QCBox_select)

                #print the filter panel for each properties
                self.rowX += 2
                QTextEdit_filter = Qw.QTextEdit(self.parent_layout)
                QTextEdit_filter.setMinimumSize(QSize(100, 20))
                QTextEdit_filter.setMaximumSize(QSize(300, 40))
                self.layout.addWidget(QTextEdit_filter, self.rowX, 1)

            #print the line to separate every node label
            self.rowX += 1
            line = Qw.QFrame(self.parent_layout)
            line.setFrameShape(Qw.QFrame.HLine)
            line.setFrameShadow(Qw.QFrame.Sunken)
            line.setObjectName("line")
            self.layout.addWidget(line)



class LayoutPlotSelection:
    """
    Class that contains all the information to take care about the center layout :
    it is used to select the given plot you want to print
    add the information of this plot based on the need and the pandas dataframe created by the class LayoutKpiSelection
    It return the information to the MainWindow about the plot selection

    The plot information is send as a dictionary by the MainWindow: MyWindow
    """
    def __init__(self, layout, parent_layout, dict_plot):

        self.layout = layout
        self.parent_layout = parent_layout

        self.dict_plot = dict_plot

        self.initial_view()



    #def set_QComboBox_content(self):


    def initial_view(self):
        """
        create the initial view for the Center layout
        :return:
        """

        #print the comboBox
        self.Center_comboBox_select_plot = Qw.QComboBox(self.parent_layout)
        self.Center_comboBox_select_plot.setObjectName("Center_comboBox_select_plot")
        self.layout.addWidget(self.Center_comboBox_select_plot, 1, 0, 1, 1)
        self.Center_comboBox_select_plot.addItems(self.dict_plot.keys())

        #print the label
        self.Center_label_SelectPlot = Qw.QLabel(self.parent_layout)
        self.Center_label_SelectPlot.setText("Select your plot")
        self.Center_label_SelectPlot.setMaximumSize(QSize(16777, 20))
        self.Center_label_SelectPlot.setObjectName("Center_label_SelectPlot")
        self.layout.addWidget(self.Center_label_SelectPlot, 0, 0, 1, 1)

        #creat a form layout to be able to select the plot information
        self.Center_formLayout_infoPlot = Qw.QFormLayout()
        self.Center_formLayout_infoPlot.setObjectName("Center_formLayout_infoPlot")
        self.layout.addLayout(self.Center_formLayout_infoPlot, 2, 0, 1, 1)

        #print the button to send back the information
        self.Center_pushButton_printPlot = Qw.QPushButton(self.parent_layout)
        self.Center_pushButton_printPlot.setText("print the plot")
        self.Center_pushButton_printPlot.setObjectName("Center_pushButton_printPlot")
        self.layout.addWidget(self.Center_pushButton_printPlot, 3, 0, 1, 1)




class MyWindow(Qw.QMainWindow, Ui_KPIWindow):
    """
    the main class it make the interaction between all the different view and the database: it is kind of a controller
    it ask the database to give a dict that contains the node and propeties from the given database
    it give this information to the class LayoutKpiSelection to allow the user to select the needed data
        this return a query used to ask the database to create the pandas dataframe
    it give the information to the class LayoutPlotSelection to allow the user to select the needed plot information
    It used the pandas and the plot information to create a plot and send it to the class LayoutPlotView to print it
    """
    def __init__(self, database=None):
        Qw.QMainWindow.__init__(self)
        self.setupUi(self)

        self.database = database

        #TODO the label_properties should be sent by the database
        # self.hLayoutGeneral.addLayout(LayoutKpiSelection(MWO.get_dict_database_structure(self.database)))
        self.label_properties = {'Human': {'name'},
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

        # It represent all the plot and the needed information to print print it
        self.dict_plot = {'Bar Plot' : ['name','x','y','hue'],
                          'Horizontal Bar Plot' : ['name','x','y','hue']
                          }

        self.Left_View_labelProperties = LayoutKpiSelection(self.Left_gridLayout_labelProperties, self.horizontalLayoutWidget, self.label_properties)
        self.Center_view_plotSelection = LayoutPlotSelection(self.Center_gridLayout_infoPlot, self.horizontalLayoutWidget, self.dict_plot)




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


