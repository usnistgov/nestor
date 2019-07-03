"""
author: Thurston Sexton
"""
from __future__ import unicode_literals

import calendar
from distutils.version import StrictVersion

import holoviews as hv
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from matplotlib.colors import ColorConverter

import nestor
nestorParams = nestor.CFG

color_opts = {  # TODO: make this tag-agnostic somehow?
        'P': 'crimson',
        'S': '#7ABC32',
        'I': '#4F81BD',
        'U': '#ffc000',
        'NA': 'gray',
        'X': 'black'
    }


def tag_relation_net(tag_df, name=None, kind='coocc',
                     layout=nx.spring_layout,  layout_kws=None,
                     padding=None, **node_adj_kws):
    """
    Explore tag relationships by create a Holoviews Graph Element. Nodes are tags
    (colored by classification), and edges occur only when those tags happen together.

    Parameters
    ----------
    tag_df :  pandas.DataFrame
        standard Nestor tag occurrence matrix. Multi-column with top-level containing
        tag classifications (named-entity NE) and 2nd level containing tags. Each row
        corresponds to a single event (MWO), with binary indicators (1-occurs, 0-does not).
    name : str
        what to name this tag relation element. Creates a Holoviews group "name".
    kind : str
        coocc :
            co-occurrence graph, where tags are connected if they occur in the same MWO,
            above the value calculated for pct_thres. Connects all types together.
        sankey :
            Directed "flow" graph, currently implemented with a (P) -> (I) -> (S) structure.
            Will require ``dag=True``. Alters default to ``similarity=count``
    layout : object (function), optional
        must take a graph object as input and output 2D coordinates for node locations
        (e.g. all networkx.layout functions). Defaults to ``networkx.spring_layout``
    layout_kws : dict, optional
        options to pass to networkx layout functions
    padding : dict, optional
        contains "x" and "y" specifications for boundaries. Defaults:
            ``{'x':(-0.05, 1.05), 'y':(-0.05, 1.05)}``
        Only valid if ``kind`` is 'coocc'.

    node_adj_kws :
        keyword arguments for ``nestor.tagtrees.tag_df_network``. Valid options are
            similarity : 'cosine' (default) or 'count'
            dag : bool, default='False', (True if ``kind='sankey'``)
            pct_thres : : int or None
                If int, between [0,100]. The lower percentile at which to
                threshold edges/adjacency.

    Returns
    -------
    graph: holoviews.Holomap or holoviews.Graph element, pending sankey or cooccurrence input.
    """
    try:
        import nestor.tagtrees
    except ImportError:
        print('The tag-relation network requires the use of our trees module! Import failed!')
        raise
    if name is None:
        name = 'Tag Net'
    adj_params = {
        'similarity': 'cosine',
    }

    graph_types = {
        'coocc':  hv.Graph,
        'sankey': hv.Sankey,
       }

    if kind is 'sankey':
        if node_adj_kws.get('dag', True) is False:
            import warnings
            warnings.warn('Sankey cannot be plotted with a co-occurrence net! Changing to DAG...')
        adj_params['similarity'] = 'count'
        adj_params.update(node_adj_kws)
        adj_params['dag'] = True
    else:
        assert kind is 'coocc', 'You have passed an invalid graph type!'
        adj_params.update(node_adj_kws)

    G, node_info, edge_info = nestor.tagtrees.tag_df_network(tag_df[['I', 'P', 'S']],
                                                             **adj_params)
    pos = pd.DataFrame(layout(G)).T.rename(columns={0: 'x', 1: 'y'})
    node_info = node_info.join(pos).reset_index().rename(columns={'index': 'tag'})

    nodes = hv.Nodes(node_info,
                     kdims=['x', 'y', 'tag'],
                     vdims=['NE', 'count'])

    # nodes = nodes.sort('NE').options(color_index='NE', cmap=opts, size='size')

    graph = graph_types[kind]((edge_info, nodes),
                     group=name, vdims='weight')
    ops = {
        'color_index': 'NE',
        'cmap': color_opts,
        'edge_color_index': 'weight',
        'edge_cmap': 'blues',
        #     'node_size' : 'count',  # wait for HoloViews `op()` functionality!
    }

    graph = graph.options(**ops)



    if kind is 'sankey':
        return graph
    else:
        text = hv.Labels(node_info, ['x', 'y'], 'tag', group=name).options(text_font_size='8pt',
                                                                       xoffset=0.015, yoffset=-0.015,
                                                                       text_align='left')
        if padding is None:
            padding = dict(x=(-1.05, 1.05), y=(-1.05, 1.05))
        return (graph*text).redim.range(**padding)


class TagPlot:
    """
    Central holder for holoviews dynamic-maps, to be served as a Bokeh App.
    """
    def __init__(self, data_file, cat_specifier='name', topn = 10):

        # cross-ref category with nestorParams
        possible_cats = list(nestorParams.datatype_search(cat_specifier))

        # load up the data
        self.df = pd.read_hdf(data_file, key='df')
        self.tag_df = pd.read_hdf(data_file, key='tags')
        # print(self.tag_df)
        self.names = [name for name in possible_cats
                 if name in self.df.columns.tolist()]

        self.name_opt = {
            name: {'name': nestorParams.datatypes[name],
                   'opts': self._get_cat_list(name, topn)}
            for name in self.names
        }
        # filtering tags by count
        # self.node_thres = range(1, 91, 10)
        self.node_thres = np.around(np.logspace(0, 1.5), decimals=1)

        # for network-based plot options
        self.weights = ['cosine', 'count']
        self.edge_thres = range(1, 91, 10)

        self.table = hv.Table(self.df)

    def _get_cat_list(self, col_name, topn):
        return (
            self.df[col_name]
            .str.split(', ', expand=True)
            .stack()
            .dropna()
            .value_counts()
            .index[:topn]  # top occurring
            .tolist()
        )

    def filter_type_name(self, obj_type, obj_name):
        """
        build a mask to filter data on
        Parameters
        ----------
        obj_type : class of object to filter on
        obj_name : sub-class/instance to filter on
        Returns
        -------
        pd.Series, mask for filtering df, tag_df.
        """
        is_obj = (
            self.df[obj_type]
            .str.contains(obj_name, case=False)
            .fillna(False)
        )
        return is_obj

    def filter_tags(self, obj_type, obj_name, n_thres=20):
        """
        apply filter to binary tag matrix (tag_df)
        Parameters
        ----------
        obj_type : passed to filter_type_name
        obj_name : passed to filter_type_name
        n_thres : only return nodes in the top ``n_thres`` percentile
        Returns
        -------
        pd.DataFrame, filtered binary tax matrix
        """
        is_obj = self.filter_type_name(obj_type, obj_name)

        assert 0 <= n_thres <= 100, 'percentiles must be between [0,100]'
        cts = self.tag_df.loc[is_obj, :].sum()
        top2 = set((  # 2 most-freq tags of each type
            cts
            .reset_index(name='cts')
            .groupby('level_0')
            .apply(lambda x: x.nlargest(2, columns=['cts']))
        )['level_1'].tolist())

        pct = max(1, cts.quantile((100 - n_thres)/100., interpolation='lower'))
        top_pct = set(
            cts[cts >= pct]
            .reset_index()['level_1']
            .tolist()
        )

        filt_set = (top2 | top_pct)-{'_untagged'}
        filt_tags = self.tag_df.loc[is_obj, (slice(None), filt_set)]

        return filt_tags

    def hv_nodelink(self, obj_type):
        """
        Generates a hv.DynamicMap with a nodelink representation of
        filtered tags.
        Parameters
        ----------
        obj_type : class of object to show
        Returns
        -------
        hv.DynamicMap
        """
        kws = {
            'layout_kws': {'prog': 'neatopusher'},
        }

        #
        def load_nodelink(obj_name, n_thres=10, e_thres=80, weight='cosine'):
            tags = self.filter_tags(obj_type, obj_name, n_thres)
            elem = tag_relation_net(tags, name='Nodelink',
                                    similarity=weight,
                                    pct_thres=e_thres,
                                    **kws)
            elem = elem.options({'Graph': dict(edge_line_width=1.5,
                                               edge_alpha=.3,
                                               node_line_color='white',
                                               xaxis=None, yaxis=None)})
            return (
                    elem.options(width=500, height=500) +
                    self.table.select(**{obj_type: obj_name}).options(width=1000)
            ).cols(1)

        dmap = hv.DynamicMap(load_nodelink,
                             #                              cache_size=1,
                             kdims=['obj_name',
                                    'n_thres',
                                    'e_thres',
                                    'weight']).options(framewise=True, title_format='')
        dmap = dmap.redim.values(obj_name=self.name_opt[obj_type]['opts'],
                                 n_thres=self.node_thres,
                                 e_thres=self.edge_thres,
                                 weight=self.weights)
        return dmap

    def hv_flow(self, obj_type):
        """
        Generates a hv.DynamicMap with a Sankey/flow representation of
        filtered tags.
        Parameters
        ----------
        obj_type : class of object to show
        Returns
        -------
        hv.DynamicMap
        """
        kws = {
            'kind':'sankey'
        }

        #
        def load_flow(obj_name, n_thres=10, weight='cosine'):
            tags = self.filter_tags(obj_type, obj_name, n_thres)
            elem = tag_relation_net(tags, name='Nodelink',
                                    similarity=weight,
                                    **kws)
            elem = elem.options({'Graph': dict(edge_line_width=1.5,
                                               edge_alpha=.3,
                                               edge_cmap='blues',
                                               node_line_color='white',
                                               xaxis=None, yaxis=None)})
            return (
                elem.options(width=800, height=500) +
                self.table.select(**{obj_type: obj_name}).options(width=1000)
            ).cols(1)

        dmap = hv.DynamicMap(load_flow,
                             #                              cache_size=1,
                             kdims=['obj_name',
                                    'n_thres',
                                    'weight']).options(framewise=True, title_format='')
        dmap = dmap.redim.values(obj_name=self.name_opt[obj_type]['opts'],
                                 n_thres=self.node_thres,
                                 weight=self.weights)
        return dmap


    def hv_bars(self, obj_type):
        """
        Generates a hv.DynamicMap with a bars/frequency representation of
        filtered tags.
        Parameters
        ----------
        obj_type : class of object to show
        Returns
        -------
        hv.DynamicMap
        """
        def load_bar(obj_name, n_thres=20, order='grouped'):
            filt_tags = self.filter_tags(obj_type, obj_name, n_thres)
            tags = (
                filt_tags
                # .drop(columns=['NA'], errors='ignore')
                .sum()
                .reset_index()
                .rename(columns={
                    'level_0': 'class',
                    'level_1': 'tag name',
                    0: 'count'
                })
                .groupby('class')
                .apply(lambda x: x.nlargest(10, columns=['count']))
                .reset_index(drop=True)
            )

            bar_kws = dict(color_index='class',
                           xrotation=90,
                           cmap=color_opts,
                           tools=['hover'],
                           line_color='w')
            if order != 'grouped':
                tags = tags.sort_values('count', ascending=False)

            bars = hv.Bars(tags,
                           kdims=['tag name'], vdims=['count', 'class']).options(**bar_kws)

            return (bars.options(width=800) +
                    self.table.select(**{obj_type: obj_name}).options(width=1000)).cols(1)

        dmap = hv.DynamicMap(load_bar,
                             kdims=['obj_name',
                                    'n_thres',
                                    'order']).options(framewise=True, title_format='')
        dmap = dmap.redim.values(obj_name=self.name_opt[obj_type]['opts'],
                                 n_thres=self.node_thres,
                                 order=['sorted', 'grouped'])
        return dmap


_pandas_18 = StrictVersion(pd.__version__) >= StrictVersion('0.18')


def tagyearplot(tag_df, year=None, how='sum', vmin=None, vmax=None, cmap='Reds',
                linewidth=1, linecolor=None,
                monthlabels=calendar.month_abbr[1:], monthticks=True, ax=None,
                **kwargs):
    """
    Plot a timeseries of (binary) tag occurrences as a calendar heatmap over weeks in the year.
    any columns passed will be explicitly plotted as rows, with each week in the year as a column.
    By default, occurences are summed, not averaged, but this aggregation over weeks may be any
    valid option for the `pandas.Dataframe.agg()` method.

    adapted from:
    'Martijn Vermaat' 14 Feb 2016
    'martijn@vermaat.name'
    'https://github.com/martijnvermaat/calmap'

    Parameters
    ----------
    tag_df :  pandas.DataFrame
        standard Nestor tag occurrence matrix. Multi-column with top-level containing
        tag classifications (named-entity NE) and 2nd level containing tags. Each row
        corresponds to a single event (MWO), with binary indicators (1-occurs, 0-does not).
    year : integer
        Only data indexed by this year will be plotted. If `None`, the first
        year for which there is data will be plotted.
    how : string
        Method for resampling data by day. If `None`, assume data is already
        sampled by day and don't resample. Otherwise, this is passed to Pandas
        `Series.resample`.
    vmin, vmax : floats
        Values to anchor the colormap. If `None`, min and max are used after
        resampling data by day.
    cmap : matplotlib colormap name or object
        The mapping from data values to color space.
    linewidth : float
        Width of the lines that will divide each day.
    linecolor : color
        Color of the lines that will divide each day. If `None`, the axes
        background color is used, or 'white' if it is transparent.
    monthlabels : list
        Strings to use as labels for months, must be of length 12.
    monthticks : list or int or bool
        If `True`, label all months. If `False`, don't label months. If a
        list, only label months with these indices. If an integer, label every
        n month.
    ax : matplotlib Axes
        Axes in which to draw the plot, otherwise use the currently-active
        Axes.
    kwargs : other keyword arguments
        All other keyword arguments are passed to matplotlib `ax.pcolormesh`.
    Returns
    -------
    ax : matplotlib Axes
        Axes object with the calendar heatmap.
    """
    if year is None:
        year = tag_df.index.sort_values()[0].year

    if how is None:
        # Assume already sampled by day.
        by_day = tag_df
    else:
        # Sample by day.
        if _pandas_18:
            by_day = tag_df.resample('W').agg(how)
        else:
            by_day = tag_df.resample('W', how=how)

    # Min and max per day.
    if vmin is None:
        vmin = by_day.min().min()
    if vmax is None:
        vmax = by_day.max().max()

    if ax is None:
        ax = plt.gca()

    if linecolor is None:
        linecolor = ax.get_facecolor()

        if ColorConverter().to_rgba(linecolor)[-1] == 0:
            linecolor = 'white'

    # Filter on year.
    by_day = by_day[by_day.index.year == year]
    dat_names = by_day.columns

    pd.options.mode.chained_assignment = None  # default='warn'
    by_day['week'] = by_day.index.week

    # Add missing days.
    by_day = by_day.reindex(
        pd.date_range(start=str(year), end=str(year + 1), freq='W')[:-1])
    # There may be some days assigned to previous year's last week or
    # next year's first week. We create new week numbers for them so
    # the ordering stays intact and week/day pairs unique.
    by_day.loc[(by_day.index.month == 1) & (by_day.week > 50), 'week'] = 0
    by_day.loc[(by_day.index.month == 12) & (by_day.week < 10), 'week'] \
        = by_day.week.max() + 1

    plot_data = by_day[dat_names].transpose().fillna(0)

    # Draw heatmap.
    kwargs['linewidth'] = linewidth
    kwargs['edgecolors'] = linecolor
    ax.pcolormesh(plot_data,
                  # vmin=vmin, vmax=vmax,
                  cmap=cmap, **kwargs)
    # Limit heatmap to our data.
    ax.set(xlim=(0, plot_data.shape[1]), ylim=(0, plot_data.shape[0]))

    # Square cells.
    ax.set_aspect('equal')

    # Remove spines and ticks.
    for side in ('top', 'right', 'left', 'bottom'):
        ax.spines[side].set_visible(False)
    ax.xaxis.set_tick_params(which='both', length=0)
    ax.yaxis.set_tick_params(which='both', length=0)

    # Get indices for monthlabels.
    if monthticks is True:
        monthticks = range(len(monthlabels))
    elif monthticks is False:
        monthticks = []
    elif isinstance(monthticks, int):
        monthticks = range(len(monthlabels))[monthticks // 2::monthticks]

    ax.set_xlabel('')
    # ax.set_xticks([by_day.ix[datetime.date(year, i + 1, 15)].week for i in monthticks])

    ax.set_xticks([pd.Timestamp('{}/15/{}'.format(i, year)).week - 1.5 for i in range(1, 13)])
    ax.set_xticklabels([monthlabels[i] for i in monthticks], ha='center')

    ax.set_ylabel('')
    ax.yaxis.set_ticks_position('right')
    ax.set_yticks([dat_names.shape[0] - i - .5 for i in range(dat_names.shape[0])])
    ax.set_yticklabels(dat_names[::-1], rotation='horizontal',
                       va='center')

    return ax


def tagcalendarplot(tag_df, how='sum', yearlabels=True, yearascending=True, yearlabel_kws=None,
                    subplot_kws=None, gridspec_kws=None, fig_kws=None, **kwargs):
    """
    Plot a timeseries of (binary) tag occurrences as a calendar heatmap over weeks in the year.
    any columns passed will be explicitly plotted as rows, with each week in the year as a column.
    By default, occurences are summed, not averaged, but this aggregation over weeks may be any
    valid option for the `pandas.Dataframe.agg()` method.


    This function  will separate out multiple years within the data as multiple calendars. The
    plotting has been heavily modified/altered/normalized, but the original version appeared here:


    adapted from:
     'Martijn Vermaat' 14 Feb 2016
     'martijn@vermaat.name'
     'https://github.com/martijnvermaat/calmap'

    Parameters
    ----------
    tag_df :  pandas.DataFrame
        standard Nestor tag occurrence matrix. Multi-column with top-level containing
        tag classifications (named-entity NE) and 2nd level containing tags. Each row
        corresponds to a single event (MWO), with binary indicators (1-occurs, 0-does not).
    how : string
        Method for resampling data by day. If `None`, assume data is already
        sampled by day and don't resample. Otherwise, this is passed to Pandas
        `Series.resample`.
    yearlabels : bool
       Whether or not to draw the year for each subplot.
    yearascending : bool
       Sort the calendar in ascending or descending order.
    yearlabel_kws : dict
       Keyword arguments passed to the matplotlib `set_ylabel` call which is
       used to draw the year for each subplot.
    subplot_kws : dict
        Keyword arguments passed to the matplotlib `add_subplot` call used to
        create each subplot.
    gridspec_kws : dict
        Keyword arguments passed to the matplotlib `GridSpec` constructor used
        to create the grid the subplots are placed on.
    fig_kws : dict
        Keyword arguments passed to the matplotlib `figure` call.
    kwargs : other keyword arguments
        All other keyword arguments are passed to `yearplot`.
    Returns
    -------
    fig, axes : matplotlib Figure and Axes
        Tuple where `fig` is the matplotlib Figure object `axes` is an array
        of matplotlib Axes objects with the calendar heatmaps, one per year.

    """
    yearlabel_kws = yearlabel_kws or {}
    subplot_kws = subplot_kws or {}
    gridspec_kws = gridspec_kws or {}
    fig_kws = fig_kws or {}

    years = np.unique(tag_df.index.year)
    if not yearascending:
        years = years[::-1]

    fig, axes = plt.subplots(nrows=len(years), ncols=1, squeeze=False,
                             subplot_kw=subplot_kws,
                             gridspec_kw=gridspec_kws, **fig_kws)
    axes = axes.T[0]

    # We explicitely resample by day only once. This is an optimization.
    if how is None:
        by_day = tag_df
    else:
        if _pandas_18:
            by_day = tag_df.resample('W').agg(how)
        else:
            by_day = tag_df.resample('W', how=how)
            # normalize to unit norm
    by_day = by_day / np.sqrt(np.square(by_day).sum(axis=0))

    ylabel_kws = dict(
        fontsize=32,
        color=kwargs.get('fillcolor', 'xkcd:wheat'),
        fontweight='bold',
        fontname='Arial',
        ha='center')
    ylabel_kws.update(yearlabel_kws)

    max_weeks = 0

    for year, ax in zip(years, axes):
        tagyearplot(by_day, year=year, how=None, ax=ax, **kwargs)
        max_weeks = max(max_weeks, ax.get_xlim()[1])

        if yearlabels:
            ax.set_ylabel(str(year), **ylabel_kws)

    # In a leap year it might happen that we have 54 weeks (e.g., 2012).
    # Here we make sure the width is consistent over all years.
    for ax in axes:
        ax.set_xlim(0, max_weeks)

    # Make the axes look good.
    plt.tight_layout()

    return fig, axes