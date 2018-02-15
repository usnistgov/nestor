import sys
from PyQt5.QtCore import QCoreApplication, Qt, QSize
from PyQt5 import QtGui
import PyQt5.QtWidgets as Qw
import csv
import sip
import json

sip.setapi('QString', 2)
sip.setapi('QVariant', 2)
from app.kpi_window.KPI_window_skeleton import Ui_KPIWindow

from matplotlib.figure import Figure
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar


class LayoutLeftKpiSelection:
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
                # I added the name of the node in the checkbox button text because it is easyer to get it after
                self.rowX += 1
                QCBox_select = Qw.QCheckBox(property, self.parent_layout)
                QCBox_select.setObjectName(f'{label.lower()}.{property}')
                self.layout.addWidget(QCBox_select, self.rowX, 1)
                self.groupCBox_selection.addButton(QCBox_select)

                #print the filter panel for each properties
                self.rowX += 2
                QTextEdit_filter = Qw.QTextEdit(QCBox_select)
                QTextEdit_filter.setObjectName(f'{label.lower()}.{property}')
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



class LayoutCenterPlotSelection:
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
        self.array_xy_values = []

        self.initial_view()

        self.Center_comboBox_select_plot.currentIndexChanged.connect(self.print_plot_settings)

        self.print_plot_settings()




    def _set_possible_xy_values(self, array_xy_values):
        """
        this function set the content of every combobox from a given array
        :param array_xy_values: the array of value to be added
        :return:
        """
        self.array_xy_values = array_xy_values

        for i in reversed(range(self.Center_formLayout_infoPlot.count())):
            if isinstance(self.Center_formLayout_infoPlot.itemAt(i).widget(), Qw.QComboBox):
                self.Center_formLayout_infoPlot.itemAt(i).widget().clear()
                self.Center_formLayout_infoPlot.itemAt(i).widget().addItems(self.array_xy_values)


    def print_plot_settings(self):
        """
        this function create and print the Widget in the form
        It changes based on the plot selected
        :return:
        """

        self.clean_formLayout()

        if self.Center_comboBox_select_plot.currentText() in self.dict_plot.keys():
            #print(self.Center_comboBox_select_plot.currentText())
            textEdit_plotName = Qw.QTextEdit(self.parent_layout)
            textEdit_plotName.setObjectName("name")
            textEdit_plotName.setMinimumSize(QSize(100, 20))
            textEdit_plotName.setMaximumSize(QSize(300, 40))
            self.Center_formLayout_infoPlot.addRow("Plot name", textEdit_plotName)


            for value in self.dict_plot[self.Center_comboBox_select_plot.currentText()]:
                comboBox_value = Qw.QComboBox(self.parent_layout)
                comboBox_value.setObjectName(value)
                comboBox_value.setMinimumSize(QSize(300, 20))
                self.Center_formLayout_infoPlot.addRow(value, comboBox_value)

        self._set_possible_xy_values(self.array_xy_values)


    def clean_formLayout(self):
        """
        clean the form layout by removing all the Widget in it
        :return:
        """
        for i in reversed(range(self.Center_formLayout_infoPlot.count())):
            if self.Center_formLayout_infoPlot.itemAt(i).widget() is not None:
                self.Center_formLayout_infoPlot.itemAt(i).widget().deleteLater()

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


class LayoutRightPlotPrint:
    """
    Contains all the information to take care of the right layout :
    it is used to print the given plot but also it contains the save information

    It gather the plot information send by the centerlayout
    and the pandas dataframe create based on the leftlayout
    to print a nice matplotlib plot

    """
    def __init__(self, layout, parent_layout):
        self.layout = layout
        self.parent_layout = parent_layout
        self.figure_canevas = None

        self.initial_view()
        self.print_plot()

    def _set_dataframe(self, dataframe):
        self.dataframe = dataframe

    def _set_plotProperties(self, properties):
        self.properties = properties

    def initial_view(self):
        """
        the initial view of the tool
        :return:
        """
        self.Right_VBoxLayout_PlotView = Qw.QVBoxLayout(self.parent_layout)
        self.Right_VBoxLayout_PlotView.setObjectName("Right_graphicsView_Plot")
        self.layout.addLayout(self.Right_VBoxLayout_PlotView, 0, 0, 1, 1)

        self.Right_pushButton_openJson = Qw.QPushButton(self.parent_layout)
        self.Right_pushButton_openJson.setText("Open a plot information")
        self.Right_pushButton_openJson.setObjectName("Right_pushButton_openJson")
        self.layout.addWidget(self.Right_pushButton_openJson, 1, 0, 1, 1)

        self.Right_pushButton_savePlot = Qw.QPushButton(self.parent_layout)
        self.Right_pushButton_savePlot.setText("Save the plot")
        self.Right_pushButton_savePlot.setObjectName("Right_pushButton_savePlot")
        self.layout.addWidget(self.Right_pushButton_savePlot, 2, 0, 1, 1)

        self.Right_pushButton_saveJson = Qw.QPushButton(self.parent_layout)
        self.Right_pushButton_saveJson.setText("Save the information")
        self.Right_pushButton_saveJson.setObjectName("Right_pushButton_saveJson")
        self.layout.addWidget(self.Right_pushButton_saveJson, 3, 0, 1, 1)


    def print_plot(self):
        """
        print the plot on the layout
        :return:
        """
        self.clean_plotLayout()

        self.figure_canevas = FigureCanvas(Figure(figsize=(5, 3)))
        self.Right_VBoxLayout_PlotView.addWidget(self.figure_canevas)

        self.plot = self.figure_canevas.figure.subplots()
        t = np.linspace(0, 10, 501)
        self.plot.plot(t, np.tan(t), ".")

    def clean_plotLayout(self):
        """
        clean the plot layout
        :return:
        """
        for i in reversed(range(self.Right_VBoxLayout_PlotView.count())):
            if self.Right_VBoxLayout_PlotView.itemAt(i).widget() is not None:
                self.Right_VBoxLayout_PlotView.itemAt(i).widget().deleteLater()

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


        self.folder_rawPlot_save = ""
        self.file_jsonPlot_save = "save_file.json"
        self.database = database

        self.query, self.array_selection, self.dict_needed_plot = None, None, None


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
        self.dict_all_plots = {'Bar Plot' : ['x', 'y', 'hue'],
                          'Horizontal Bar Plot' : ['x','y','hue'],
                          'over_time' : ['x', 'y']
                               }

        #here we create all our class for the different layout and the interaction with it
        self.Left_View_labelProperties = LayoutLeftKpiSelection(self.Left_gridLayout_labelProperties, self.horizontalLayoutWidget, self.label_properties)
        self.Left_View_labelProperties.Left_PButton_search.clicked.connect(self.onClick_leftLayout_searchButton)

        self.Center_view_plotSelection = LayoutCenterPlotSelection(self.Center_gridLayout_infoPlot, self.horizontalLayoutWidget, self.dict_all_plots)
        self.Center_view_plotSelection.Center_pushButton_printPlot.clicked.connect(self.onClick_centerLayout_printPlotButton)

        self.Right_view_plorPrint = LayoutRightPlotPrint(self.Right_gridLayout_Plot, self.horizontalLayoutWidget)
        self.Right_view_plorPrint.Right_pushButton_saveJson.clicked.connect(self.onClick_saveJson)
        self.Right_view_plorPrint.Right_pushButton_savePlot.clicked.connect(self.onClick_savePlot)
        self.Right_view_plorPrint.Right_pushButton_openJson.clicked.connect(self.onClick_openJson)


    def onClick_leftLayout_searchButton(self):
        """
        when you click on the search buttom from the left layout
        it gather all information selected
        create an object to represent it when needed
        and it return the query in cypher language
        and the array of the possible selection
        :return: query, array of seletion
        """
        groub_checkBoxs = self.Left_View_labelProperties.groupCBox_selection

        objects = []

        # self.human = Human()
        # self.issue = Issue()
        # self.item = TagItem()
        # self.machine = Machine()
        # self.operator = Operator()
        # self.problem = TagAction(it_is = 'p')
        # self.solution = TagAction(it_is = 's')
        # self.tag = Tag()
        # self.technician = Technician()

        #TODO to answer that you might need to add a special cypherquery in the node human
        # technician_operator = ?

        #loop over the checkboxes in the group
        for checkBox in groub_checkBoxs.buttons():
            if checkBox.isChecked():
                print(checkBox.objectName())
                objects.append(self.create_object_from_left_layout(name=checkBox.objectName(), texts="_"))

        # loop over all the Qtextedit of the layout
        for i in reversed(range(self.Left_gridLayout_labelProperties.count())):
            widget = self.Left_gridLayout_labelProperties.itemAt(i).widget()
            if widget is not None:
                if isinstance(widget, Qw.QTextEdit):
                    if widget.toPlainText().strip().lower() is not "":
                        texts = [t.strip() for t in widget.toPlainText().strip().lower().split(",")]
                        objects += self.create_object_from_left_layout( name = widget.objectName(), texts = texts)


        #TODO it send an array to it not an numbert of objects
        #query = KPI.cypher_to_KPI(objects)
        self.query = "MATCH (technician:TECHNICIAN)<--(issue:ISSUE) RETURN technician.name"
        print(self.query)
        self.array_selection = ["technician.name", "item.keyword", "issue.description_of_problem"]
        print(self.array_selection)

        self.Center_view_plotSelection._set_possible_xy_values(self.array_selection)
        #self.dataframe, result = KPI.dataframe_from_query(query)


    def query_to_dataframe(self):
        """
        from a array of object, it create an cypher query
        :return:
        """
        pass


    def onClick_centerLayout_printPlotButton(self):
        """
        when you click on rhe center button
        it gather the needed information for the plot in a dictionary
        :return: dictionary
        """
        form_layout = self.Center_view_plotSelection.Center_formLayout_infoPlot
        plot_text = self.Center_view_plotSelection.Center_comboBox_select_plot.currentText()
        dict_needed_plot = {'type': plot_text}

        # for every reverse widget of the layout
        for i in reversed(range(form_layout.count())):
            widget = form_layout.itemAt(i).widget()
            if widget is not None and not isinstance(widget, Qw.QLabel):
                try:
                    dict_needed_plot[widget.objectName()] = widget.currentText()
                except AttributeError:
                    dict_needed_plot[widget.objectName()] = widget.toPlainText()
                except:
                    pass
        print(dict_needed_plot)
        self.dict_needed_plot = dict_needed_plot

        self.Right_view_plorPrint.print_plot()


    def onClick_saveJson(self):
        """
        when you want to save the information to create your plot
        it gather the query, the dictionary created from the center layout and save it in an json file
        :return:
        """
        if self.query and self.array_selection and self.dict_needed_plot is not None:
            name, okPressed = Qw.QInputDialog.getText(self, "Get Name", "plot name", Qw.QLineEdit.Normal, "")
            if okPressed and name != '':
                ##TODO do not save the query alone, save as well the selection information to print it back
                string_object = { "name" : name,
                              "query" : self.query,
                              "selection" : self.array_selection,
                              "plot": self.dict_needed_plot
                }

                if self.file_jsonPlot_save:
                    with open(self.file_jsonPlot_save, "r+", newline= '\n') as file:
                        data = json.load(file)
                        data.append(string_object)
                        file.seek(0)
                        json.dump(data, file)
                        Qw.QMessageBox.about(self, 'save done',
                                             "Your information have been saved")

        else:
            Qw.QMessageBox.about(self, 'save first', "You should gather all information before you can save it")



    def onClick_savePlot(self):
        """
        save the plot as a png images in you folder
        :return:
        """
        if self.Right_view_plorPrint.plot is not None:
            name, okPressed = Qw.QInputDialog.getText(self, "Get Name", "plot name", Qw.QLineEdit.Normal, "")
            if okPressed and name != '':
                self.Right_view_plorPrint.plot.get_figure().savefig(name + ".png")
        else:
            Qw.QMessageBox.about(self, 'cannot save', "You should create a plot first")


    def onClick_openJson(self):
        """
        to add the information back to the user from the information previously saved
        :return:
        """
        if self.file_jsonPlot_save:
            with open(self.file_jsonPlot_save, "r", newline='\n') as file:
                dict_line_json = json.load(file)
                dict_line_json.append({"test":"test"})
                plots_names = []
                for plot_json in dict_line_json:
                    if "name" in plot_json:
                        #print(plot_json['name'])
                        plots_names.append(plot_json['name'])

                plot_name, okPressed = Qw.QInputDialog.getItem(self, "plot name selection", "choose your plot name", plots_names)

                if okPressed and plot_name != '':
                    for plot_json in dict_line_json:
                        if "name" in plot_json:
                            if plot_json['name'] == plot_name:

                                self.query = plot_json["query"]
                                self.array_selection = plot_json["selection"]
                                self.dict_needed_plot = plot_json["plot"]

                                print(self.query)
                                print(self.array_selection)
                                print(self.dict_needed_plot)

                                self.Center_view_plotSelection._set_possible_xy_values(self.array_selection)
                                self.Center_view_plotSelection.Center_comboBox_select_plot.setCurrentText(plot_json["plot"]["type"])
                                print(plot_json["plot"]["type"])
                                for i in reversed(range(self.Center_view_plotSelection.Center_formLayout_infoPlot.count())):
                                    widget = self.Center_view_plotSelection.Center_formLayout_infoPlot.itemAt(i).widget()
                                    print(widget)
                                    if isinstance(widget, Qw.QComboBox):
                                        if widget.objectName() in  plot_json["plot"]:
                                            widget.setCurrentText(plot_json["plot"][widget.objectName()])
                                    if isinstance(widget, Qw.QTextEdit):
                                        if widget.objectName() in  plot_json["plot"]:
                                            widget.setText(plot_json["plot"][widget.objectName()])





    def close_application(self):
        """
        close the application
        :return:
        """
        # this running means somewhere, an option to leave has been clicked
        choice = Qw.QMessageBox.question(self, 'Shut it Down',
                                         'Are you sure?',
                                         Qw.QMessageBox.Yes | Qw.QMessageBox.No)
        if choice == Qw.QMessageBox.Yes:
            print('exiting program...')
            sys.exit()
        else:
            pass



    def create_object_from_left_layout(self, name, texts):
        """
        create the object for the left layout selection
        :param name:
        :param texts:
        :return:
        """
    #TODO be carefull when _get_ return None it might break the system
    ##TODO change all the endswith() with the label inside the object

        result = []
        pass
    #     if name.startswith("human."):
    #         result.append(self.human)
    #         if name.endswith(".name"):
    #             self.human._set_name(self.human._get_name() + texts)
    #
    #     elif name.startswith("issue."):
    #         result.append(self.issue)
    #         if name.endswith(f'.description_of_problem'):
    #             self.issue._set_problem(self.issue._get_problem() + texts)
    #         elif name.endswith(".description_of_solution"):
    #             self.issue._set_solution(self.issue._get_solution() + texts)
    #         elif name.endswith(".part_in_process"):
    #             self.issue._set_part_in_process(self.issue._get_part_in_process() + texts)
    #         elif name.endswith(".machine_down"):
    #             self.issue._set_machine_down(self.issue._get_machine_down() + texts)
    #
    #         elif name.endswith(".date_maintenance_work_order_issue"):
    #             self.issue._set_date_maintenance_work_order_issue(self.issue._get_date_maintenance_work_order_issue() + texts)
    #         elif name.endswith(".date_maintenance_work_order_close"):
    #             self.issue._set_date_maintenance_work_order_close(self.issue._get_date_maintenance_work_order_close() + texts)
    #
    #     elif name.startswith("item."):
    #         result.append(self.item)
    #         if name.endswith(".keyword"):
    #             self.item._set_keyword(self.item._get_keyword() + texts)
    #             pass
    #
    #     elif name.startswith("machine."):
    #         result.append(self.machine)
    #         if name.endswith(".name"):
    #             self.human._set_name(self.human._get_name() + texts)
    #             pass
    #
    #     elif name.startswith("operator."):
    #         result.append(self.operator)
    #         if name.endswith(".name"):
    #             self.operator._set_name(self.operator._get_name() + texts)
    #             pass
    #
    #     elif name.startswith("problem."):
    #         result.append(self.problem)
    #         if name.endswith(".name"):
    #             self.problem._set_keyword(self.problem._get_keyword() + texts)
    #             pass
    #
    #     elif name.startswith("solution."):
    #         result.append(self.solution)
    #         if name.endswith(".name"):
    #             self.solution._set_keyword(self.solution._get_keyword() + texts)
    #             pass
    #
    #     elif name.startswith("tag."):
    #         result.append(self.tag)
    #         if name.endswith(".name"):
    #             self.tag._set_keyword(self.tag._get_keyword() + texts)
    #             pass
    #
    #     elif name.startswith("technician."):
    #         result.append(self.technician)
    #         if name.endswith(".name"):
    #             self.technician._set_name(self.technician._get_name() + texts)
    #             pass
    #
    #     # elif name.startswith("technician and operator."):
    #         result.append(self.technician_operator)
    #     #     if name.endswith(".name"):
    #     #         # self.human._set_name(self.human._get_name() + texts)
    #     #         pass
    #
    #       return result


if __name__ == "__main__":
    app = Qw.QApplication(sys.argv)
    # database = DatabaseNeo4J("bolt://127.0.0.1:7687", "neo4j", 'GREYSTONE!!')
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())


