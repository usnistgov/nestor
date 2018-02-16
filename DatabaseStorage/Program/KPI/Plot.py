from PyQt5.QtWidgets import QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import seaborn as sns
import pandas as pd
from numpy.ma import arange, sin

dict_all_plot = {
    'Bar Plot' : ['x', 'height'],
    'Horizontal Bar Plot' : ['y','width'],
    # 'over_time' : ['x', 'y'],
    # 'Count Plot' : ['x', 'hue']
}


class MyMplCanvas(FigureCanvas):
    """
    the canvas used to print the plot in the right layout of the KPI UI
    All the characteristic that are the same for all the other plot should be in this class
    and the specifique on on the subclass
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
    the sub ccanvas for a barplot
    """
    def __init__(self, layout=None, parent_layout=None, dataframe=None, properties=None, width=5, height=4, dpi=100):
        super().__init__(layout=layout, parent_layout=parent_layout, dataframe=dataframe, properties=properties, width=width, height=height, dpi=dpi)
        self.plot_it()

    def plot_it(self):
        """
        print the plot
        :return:
        """
        #self.dataframe = self.dataframe.sort_values("issue_count", ascending=False)

        self.axes.bar(x=self.dataframe[self.properties["x"]], height=self.dataframe[self.properties["height"]])


class HorizontalBarPlot_canevas(MyMplCanvas):
    """
    the sub ccanvas for a horizontal barplot
    """
    def __init__(self, layout=None, parent_layout=None, dataframe=None, properties=None, width=5, height=4, dpi=100):
        super().__init__(layout=layout, parent_layout=parent_layout, dataframe=dataframe, properties=properties, width=width, height=height, dpi=dpi)
        self.plot_it()

    def plot_it(self):
        """
        print the plot
        :return:
        """
        #self.dataframe = self.dataframe.sort_values("issue_count", ascending=False)
        self.axes.barh(y=self.dataframe[self.properties["y"]], width=self.dataframe[self.properties["width"]])