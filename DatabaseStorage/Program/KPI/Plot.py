import matplotlib.pyplot as plt
import matplotlib.pylab as pylab
import seaborn as sns


def barPlot(dataframe, filter, on, x, y, hue=None):
    data = dataframe[(dataframe[on].isin(filter))].sort_values(by=[x], ascending=False)
    return sns.barplot(y=y, x=x, hue=hue, data=data)