#
# TODO DEPRECIATED
#
# from PyQt5.QtWidgets import QSizePolicy
# import PyQt5.QtWidgets as Qw
#
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# from matplotlib.figure import Figure
# import matplotlib as mpl
# import seaborn as sns
# import pandas as pd
#
# dict_all_plot = {
#     'Bar Plot' : ['x', 'number', 'hue'],
#     'Horizontal Bar Plot' : ['y', 'number', 'hue'],
#     'Date Plot' : ['time', 'number', 'hue']
# }
#
#
# class MyMplCanvas(FigureCanvas):
#     """
#     the canvas used to print the plot in the right layout of the kpi UI
#     All the characteristic in common for all the plot should be in this class
#     """
#
#     def __init__(self, layout=None, parent_layout=None, dataframe=None, properties=None, width=5, height=4, dpi=100):
#         self.properties = properties
#         self.dataframe = dataframe
#         self.layout = layout
#
#
#         self.fig = Figure(figsize=(width, height), dpi=dpi)
#         self.axes = self.fig.add_subplot(111)
#
#         FigureCanvas.__init__(self, self.fig)
#         self.setParent(parent_layout)
#         self.layout.addWidget(self)
#
#         self.plot_it()
#
#         FigureCanvas.setSizePolicy(self,
#                                    QSizePolicy.Expanding,
#                                    QSizePolicy.Expanding)
#         FigureCanvas.updateGeometry(self)
#
#     def plot_it(self):
#         """
#         print the plot here we have the original plot
#         :return:
#         """
#         pass
#
#
# class BarPlot_canevas(MyMplCanvas):
#     """
#     the sub canvas for a barplot
#     """
#     def __init__(self, layout=None, parent_layout=None, dataframe=None, properties=None, width=5, height=4, dpi=100):
#         super().__init__(layout=layout, parent_layout=parent_layout, dataframe=dataframe, properties=properties, width=width, height=height, dpi=dpi)
#         self.plot_it()
#
#     def plot_it(self):
#         """
#         print the plot
#         :return:
#         """
#
#         try :
#             if not self.dataframe.empty:
#                 df = self.dataframe.sort_values(self.properties["number"], ascending=False)
#                 if not self.properties["hue"] is "":
#                     sns.barplot(data=df,
#                                 x=self.properties["x"],
#                                 y=self.properties["number"],
#                                 hue=self.properties["hue"],
#                                 ax=self.axes)
#                 else:
#                     sns.barplot(data=df,
#                                 x=self.properties["x"],
#                                 y=self.properties["number"],
#                                 ax=self.axes)
#         except (KeyError, TypeError):
#             Qw.QMessageBox.about(self, 'cannot plot', "One of the axes you have selected is not in your database")
#
#
# class HorizontalBarPlot_canevas(MyMplCanvas):
#     """
#     the sub canvas for a horizontal Horizontal barplot
#     """
#     def __init__(self, layout=None, parent_layout=None, dataframe=None, properties=None, width=5, height=4, dpi=100):
#         super().__init__(layout=layout, parent_layout=parent_layout, dataframe=dataframe, properties=properties, width=width, height=height, dpi=dpi)
#         self.plot_it()
#
#     def plot_it(self):
#         """
#         print the plot
#         :return:
#         """
#         try :
#             if not self.dataframe.empty:
#                 df = self.dataframe.sort_values(self.properties["number"], ascending=False)
#                 print()
#                 if not self.properties["hue"] is "":
#                     sns.barplot(data=df,
#                                 y=self.properties["y"],
#                                 x=self.properties["number"],
#                                 hue=self.properties["hue"],
#                                 ax=self.axes)
#                 else:
#                     sns.barplot(data=df,
#                                 y=self.properties["y"],
#                                 x=self.properties["number"],
#                                 ax=self.axes)
#         except (KeyError, TypeError):
#             Qw.QMessageBox.about(self, 'cannot plot', "One of the axes you have selected is not in your database")
#
#
# class DatePlot_canevas(MyMplCanvas):
#     """
#     the sub canvas for a Date plot
#     """
#     def __init__(self, layout=None, parent_layout=None, dataframe=None, properties=None, width=5, height=4, dpi=100):
#         super().__init__(layout=layout, parent_layout=parent_layout, dataframe=dataframe, properties=properties, width=width, height=height, dpi=dpi)
#         self.plot_it()
#
#     def plot_it(self):
#         """
#         print the plot
#         :return:
#         """
#         def myFormatter(x, pos):
#             return pd.to_datetime(x).strftime('%b-%Y')
#
#         try :
#             if not self.dataframe.empty:
#                 df = self.dataframe
#                 df[self.properties["time"]] = pd.DatetimeIndex(df[self.properties["time"]])
#
#                 if not self.properties["hue"] is "":
#                     df = df.groupby(by=[self.properties["hue"], pd.Grouper(key=self.properties["time"], freq="M")]).sum()
#                     df = df.reset_index()
#                     sns.tsplot(data=df,
#                                     time=self.properties["time"],
#                                     unit=self.properties["hue"],
#                                     condition=self.properties["hue"],
#                                     value=self.properties["number"],
#                                     ax=self.axes
#                                     )
#
#                 else:
#                     df = df.groupby(by=pd.Grouper(key=self.properties["time"], freq="M")).sum()
#                     df = df.reset_index()
#                     sns.tsplot(data=df,
#                                     time=self.properties["time"],
#                                     value=self.properties["number"],
#                                     ax=self.axes
#                                     )
#
#                 self.axes.xaxis.set_major_formatter(mpl.ticker.FuncFormatter(myFormatter))
#                 self.fig.autofmt_xdate()
#
#         except (KeyError, TypeError):
#             Qw.QMessageBox.about(self, 'cannot plot', "One of the axes you have selected is not in your database")
#
#         # if not self.dataframe.empty:
#         #     df = self.dataframe
#         #     df[self.properties["time"]] = pd.DatetimeIndex(df[self.properties["time"]])
#         #     df = df.groupby(by=[self.properties["hue"], pd.TimeGrouper(key=self.properties["time"], freq="M")]).sum()
#         #     df=df.reset_index()
#         #
#         #     ax = sns.tsplot(data=df,
#         #                     time=self.properties["time"],
#         #                     unit=self.properties["hue"],
#         #                     condition=self.properties["hue"],
#         #                     value=self.properties["number"],
#         #                     ax = self.axes
#         #                     )
#
#
#
#
#
