from PyQt5.QtWidgets import QSizePolicy
import PyQt5.QtWidgets as Qw

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import seaborn as sns
import pandas as pd
from numpy.ma import arange, sin

dict_all_plot = {
    'Bar Plot' : ['x', 'height'],
    'Horizontal Bar Plot' : ['y','width'],
    'Date Plot' : ['date', 'over'],
    # 'Count Plot' : ['x', 'hue']
}


class MyMplCanvas(FigureCanvas):
    """
    the canvas used to print the plot in the right layout of the KPI UI
    All the characteristic in common for all the plot should be in this class
    """

    def __init__(self, layout=None, parent_layout=None, dataframe=None, properties=None, width=5, height=4, dpi=100):
        self.properties = properties
        self.dataframe = dataframe
        self.layout = layout


        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent_layout)
        self.layout.addWidget(self)

        self.plot_it()

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def plot_it(self):
        """
        print the plot here we have the original plot
        :return:
        """
        pass


class BarPlot_canevas(MyMplCanvas):
    """
    the sub canvas for a barplot
    """
    def __init__(self, layout=None, parent_layout=None, dataframe=None, properties=None, width=5, height=4, dpi=100):
        super().__init__(layout=layout, parent_layout=parent_layout, dataframe=dataframe, properties=properties, width=width, height=height, dpi=dpi)
        self.plot_it()

    def plot_it(self):
        """
        print the plot
        :return:
        """
        self.dataframe.sort_values(by="issue_count", ascending=False, inplace=True)
        try :
            self.axes.bar(x=self.dataframe[self.properties["x"]], height=self.dataframe[self.properties["height"]])
        except (KeyError, TypeError):
            Qw.QMessageBox.about(self, 'cannot plot', "One of the axes you have selected is not in your database")


class HorizontalBarPlot_canevas(MyMplCanvas):
    """
    the sub canvas for a horizontal Horizontal barplot
    """
    def __init__(self, layout=None, parent_layout=None, dataframe=None, properties=None, width=5, height=4, dpi=100):
        super().__init__(layout=layout, parent_layout=parent_layout, dataframe=dataframe, properties=properties, width=width, height=height, dpi=dpi)
        self.plot_it()

    def plot_it(self):
        """
        print the plot
        :return:
        """
        try :
            #self.dataframe.sort_values(self.properties["width"], ascending=False, inplace=True)
            self.axes.barh(y=self.dataframe[self.properties["y"]], width=self.dataframe[self.properties["width"]])
        except (KeyError, TypeError):
            Qw.QMessageBox.about(self, 'cannot plot', "One of the axes you have selected is not in your database")


class DatePlot_canevas(MyMplCanvas):
    """
    the sub canvas for a Date plot
    """
    def __init__(self, layout=None, parent_layout=None, dataframe=None, properties=None, width=5, height=4, dpi=100):
        super().__init__(layout=layout, parent_layout=parent_layout, dataframe=dataframe, properties=properties, width=width, height=height, dpi=dpi)
        self.plot_it()

    def plot_it(self):
        """
        print the plot
        :return:
        """
        try:
            #print(self.dataframe[self.properties["date"]])
            #print(self.dataframe[self.properties["over"]])
            self.axes.plot_date(self.dataframe[self.properties["date"]], self.dataframe[self.properties["over"]], 'b-')
        except (KeyError, TypeError):
            Qw.QMessageBox.about(self, 'cannot plot', "One of the axes you have selected is not in your database")
