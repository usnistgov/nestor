import holoviews as hv
import pandas as pd
from nestor.tagplots import tag_relation_net, color_opts
from pathlib import Path
import numpy as np
from itertools import product


class TagPlot:

    def __init__(self, data_file, tag_file):
        #         print('HELLO', str(data_file.absolute()))
        self.df = pd.read_csv(data_file, index_col=0)
        self.tag_df = pd.read_hdf(tag_file, key='tags')

        people = [
            'nathan_maldonado',
            # 'angie_henderson',
            'margaret_hawkins_dds',
            # "tommy_walter",
            "gabrielle_davis",
            # "cristian_santos",
        ]
        machs = [
            "A34",
            "B19",
            "A14",
        ]
        self.name_opt = {
            'mach': {'name': 'Machine',
                     'opts': machs},
            'tech': {'name': 'Technician',
                     'opts': people}
        }

        self.node_thres = [1, 10]

        # for network-based plot options
        self.weights = ['cosine', 'count']
        self.edge_thres = [20, 80]

    def filter_type_name(self, obj_type, obj_name):
        is_obj = self.df[obj_type].str.contains(obj_name, case=False).fillna(False)
        return is_obj

    def filter_tags(self, obj_type, obj_name, n_thres=10):
        is_obj = self.filter_type_name(obj_type, obj_name)

        assert 0 <= n_thres <= 100, 'percentiles must be between [0,100]'
        cts = self.tag_df.loc[is_obj, :].sum()
        upper = max(1, np.percentile(cts, 100 - n_thres))

        return self.tag_df.loc[is_obj, (cts >= upper).values]

    def net_dict(self, obj_type, func):
        hv_plots = {
            (self.name_opt[obj_type]['name'],
             name, weight, n_node, n_edge): func(
                obj_type,
                obj_name=name,
                weight=weight,
                n_thres=n_node,
                e_thres=n_edge
            ) for name, weight, n_node, n_edge in product(
            self.name_opt[obj_type]['opts'],
            self.weights,
            self.node_thres,
            self.edge_thres
        )}
        return hv_plots

    def hv_nodelink(self):
        kws = {
            'layout_kws': {'prog': 'neatopusher'},
        }

        def load_nodelink(obj_type, obj_name, n_thres=10, e_thres=80, weight='cosine'):
            tags = self.filter_tags(obj_type, obj_name, n_thres)
            elem = tag_relation_net(tags, name='Nodelink',
                                    similarity=weight,
                                    pct_thres=e_thres,
                                    **kws)
            return elem

        type_dict = {**self.net_dict('tech', load_nodelink),
                     **self.net_dict('mach', load_nodelink)}
        # print(type_dict)

        hmap = hv.HoloMap(type_dict,
                          kdims=[
                              'Data',
                              'Name',
                              'Weight',
                              'Top%',
                              'edge-cutoff',
                          ])

        return hmap

        # def load_person(obj_name, n_thres=1, e_thres=80, weight='cosine'):
        #     # retrieve filtered data
        #     tags = self.filter_tags('tech', obj_name, n_thres)
        #
        #     # generate ``hv.Overlay`` from ``nestor.tagplots`
        #     elem = tag_relation_net(tags, name=f'Tech. {obj_name}',
        #                             similarity=weight, pct_thres=e_thres, **kws)
        #     if kws['layout_kws']['pos'] is not None:
        #         kws['layout_kws']['pos'] = elem.get(elem.children[0]).I.nodes.data[['x', 'y']]
        #     return elem  # .cols(1)
        #
        #
        # def load_machine(obj_name, n_thres=1, e_thres=80, weight='cosine'):
        #     tags = self.filter_tags('mach', obj_name, n_thres)
        #     elem = tag_relation_net(tags, name=f'Machine: {obj_name}',
        #                             similarity=weight, pct_thres=e_thres, **kws)
        #     if kws['layout_kws']['pos'] is not None:
        #         kws['layout_kws']['pos'] = elem.get(elem.children[0]).I.nodes.data[['x', 'y']]
        #     return elem  # .cols(1)
        #
        # param_grid = {
        #     'tech': {
        #         'range': self.people,
        #         'func': load_person,
        #     },
        #     'mach': {
        #         'range': self.machs,
        #         'func': load_machine,
        #     }
        # }
        #
        # dmap = hv.DynamicMap(param_grid[obj_type]['func'],
        #                      cache_size=1,
        #                      kdims=['obj_name',
        #                             'n_thres',
        #                             'e_thres',
        #                             'weight']).options(framewise=True)
        # dmap = dmap.redim.values(obj_name=param_grid[obj_type]['range'],
        #                          n_thres=range(1, 20),
        #                          e_thres=range(15, 90),
        #                          weight=['cosine', 'count'])
        # return dmap

    def hv_bar(self, obj_type):

        temp = self.filter_tags('mach', 'A14', 5).drop(columns=['U']).sum()  # .rename(['class','tag_name'])#.reset_index()
        temp = temp.groupby(level=0).nlargest(5).reset_index(level=0, drop=True)

        temp = temp.reset_index()
        temp.columns = ['class', 'tag name', 'count']

        bar_kws = dict(color_index='class',
                       xrotation=90,
                       cmap=color_opts,
                       tools=['hover'])

        bars = hv.Bars(temp.sort_values('count', ascending=False),
                kdims=['tag name'], vdims=['count', 'class']).options(**bar_kws)

        return bars

################################
    def filter_df(self, obj_type, obj_name):
        is_obj = self.filter_type_name(obj_type, obj_name)
        return self.df[is_obj].head(50)

    def data_table(self, obj_type, obj_name):

        df = self.filter_df(obj_type, obj_name).loc[:, ['mach',
                                                        'date_received',
                                                        'issue',
                                                        'info',
                                                        'tech']]

        with open(Path('flaskDash')/'templates'/'includes'/'_data.html', 'w+') as fo:
            # \df =self.df.head(50)
            fo.write("<div style='overflow-y: scroll; height:600px;'>")
            df.to_html(fo, classes=['table table-striped'])
            fo.write("</div>")






