import holoviews as hv
import pandas as pd
from nestor.tagplots import tag_relation_net, color_opts
from pathlib import Path
import numpy as np
# from itertools import product


class TagPlot:
    """
    Central holder for holoviews dynamic-maps, to be served as a Bokeh App.
    """
    def __init__(self, data_file, tag_file):

        # load up the data
        self.df = pd.read_csv(data_file, index_col=0)
        self.tag_df = pd.read_hdf(tag_file, key='tags')

        # set allowed technician options here
        # people = [
        #     'nathan_maldonado',
        #     'angie_henderson',
        #     'margaret_hawkins_dds',
        #     # "tommy_walter",
        #     "gabrielle_davis",
        #     "cristian_santos",
        # ]
        nplen = np.vectorize(len)
        people = np.unique(self.df.tech.str.split(', ', expand=True).fillna('').values)
        people = people[nplen(people) > 5]

        # set allowed machine options here.
        # machs = [
        #     "A34",
        #     "B19",
        #     "A14",
        # ]
        machs = self.df.mach[self.df.mach.str.contains('A\d|B\d', na=False)].sort_values().unique()

        # put it together with pretty names
        self.name_opt = {
            'mach': {'name': 'Machine',
                     'opts': machs},
            'tech': {'name': 'Technician',
                     'opts': people}
        }
        # filtering tags by count
        self.node_thres = range(1, 10)

        # for network-based plot options
        self.weights = ['cosine', 'count']
        self.edge_thres = range(1, 81, 10)

        # global table that gets filtered in other plots
        self.table = hv.Table(self.df[['mach',
                                       'date_received',
                                       'issue',
                                       'info',
                                       'tech']])

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
        is_obj = self.df[obj_type].str.contains(obj_name, case=False).fillna(False)
        return is_obj

    def filter_tags(self, obj_type, obj_name, n_thres=10):
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
        upper = max(1, np.percentile(cts, 100 - n_thres))

        return self.tag_df.loc[is_obj, (cts >= upper).values]

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
            return elem.options(width=500, height=500)
            # SOME KIND OF BUG!
            # return (elem.options(width=500, height=500) +
            #         self.table.select(**{obj_type: obj_name}).options(width=1000)).cols(1)

        dmap = hv.DynamicMap(load_nodelink,
                             #                              cache_size=1,
                             kdims=['obj_name',
                                    'n_thres',
                                    'e_thres',
                                    'weight']).options(framewise=True)
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
                                               node_line_color='white',
                                               xaxis=None, yaxis=None)})
            # return elem.options(width=800, height=500)
            # SOME KIND OF BUG!
            # return (elem.options(width=500, height=500) +
            #         self.table.select(**{obj_type: obj_name}).options(width=1000)).cols(1)

        dmap = hv.DynamicMap(load_flow,
                             #                              cache_size=1,
                             kdims=['obj_name',
                                    'n_thres',
                                    'weight']).options(framewise=True)
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
        def load_bar(obj_name, n_thres=10, order='grouped'):
            tags = self.filter_tags(obj_type, obj_name, n_thres).drop(columns=['U']).sum()
            tags = tags.groupby(level=0).nlargest(10).reset_index(level=0, drop=True)
            tags = tags.reset_index()
            tags.columns = ['class', 'tag name', 'count']

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
                             #                              cache_size=1,
                             kdims=['obj_name',
                                    'n_thres',
                                    'order']).options(framewise=True)
        dmap = dmap.redim.values(obj_name=self.name_opt[obj_type]['opts'],
                                 n_thres=range(1, 20),
                                 order=['grouped', 'sorted'])
#         curdoc().add_root(dmap)
        return dmap

######### DEPRECATED ##########
    # def filter_df(self, obj_type, obj_name):
    #     is_obj = self.filter_type_name(obj_type, obj_name)
    #     return self.df[is_obj].head(50)
    #
    # def data_table(self, obj_type, obj_name):
    #
    #     df = self.filter_df(obj_type, obj_name).loc[:, ['mach',
    #                                                     'date_received',
    #                                                     'issue',
    #                                                     'info',
    #                                                     'tech']]
    #
    #     with open(Path('flaskDash')/'templates'/'includes'/'_data.html', 'w+') as fo:
    #         # \df =self.df.head(50)
    #         fo.write("<div style='overflow-y: scroll; height:600px;'>")
    #         df.to_html(fo, classes=['table table-striped'])
    #         fo.write("</div>")
#################################


if __name__ == '__main__':
    from bokeh.server.server import Server
    from tornado.ioloop import IOLoop

    data_dir = Path('../..') / 'data' / 'sme_data'
    tagplot = TagPlot(data_dir / 'MWOs_anon.csv',
                      data_dir / 'binary_tags.h5')

    renderer = hv.renderer('bokeh').instance(mode='server')

    server = Server({
        '/bars_tech': renderer.app(tagplot.hv_bars('tech').options(width=900)),
        '/bars_mach': renderer.app(tagplot.hv_bars('mach').options(width=900)),
        '/node_tech': renderer.app(tagplot.hv_nodelink('tech').options(width=600, height=600)),
        '/node_mach': renderer.app(tagplot.hv_nodelink('mach').options(width=600, height=600)),
        '/flow_tech': renderer.app(tagplot.hv_flow('tech').options(width=900, height=600)),
        '/flow_mach': renderer.app(tagplot.hv_flow('mach').options(width=900, height=600)),
    }, port=5006, allow_websocket_origin=["127.0.0.1:5000"])
    server.start()
    # server.show('/')
    loop = IOLoop.current()
    loop.start()