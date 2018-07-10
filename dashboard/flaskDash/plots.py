import holoviews as hv
import pandas as pd
from nestor.tagplots import tag_relation_net, color_opts
from pathlib import Path
import numpy as np




class TagPlot:

    def __init__(self, data_file, tag_file):
        print('HELLO', str(data_file.absolute()))
        self.df = pd.read_csv(data_file)
        self.tag_df = pd.read_hdf(tag_file, key='tags')

        self.people = [
            'nathan_maldonado',
            'angie_henderson',
            'margaret_hawkins_dds',
            "tommy_walter",
            "gabrielle_davis",
            "cristian_santos",
        ]

        self.machs = [
            "A34"
            "B19"
            "A14"
        ]

    def filter_type_name(self, obj_type, obj_name):
        is_obj =self.df[obj_type].str.contains(obj_name, case=False).fillna(False)
        return is_obj

    def filter_tags(self, obj_type, obj_name, n_thres=10):
        is_obj = self.filter_type_name(obj_type, obj_name)

        assert 0 <= n_thres <= 100, 'percentiles must be between [0,100]'
        cts = self.tag_df.loc[is_obj, :].sum()
        upper = max(1,np.percentile(cts, 100 - n_thres))

        return self.tag_df.loc[is_obj, (cts >= upper).values]

    def hv_nodelink(self, obj_type):

        kws = {
            #     'pct_thres':80,
            #     'similarity':'cosine',
            # 'layout_kws': {'prog': 'neatopusher'},
            'padding': dict(x=(-1.05, 1.05), y=(-1.05, 1.05)),
        }

        def load_person(obj_name, n_thres=1, e_thres=80, weight='cosine'):
            tags = self.filter_tags('tech', obj_name, n_thres)
            elem = tag_relation_net(tags, name=f'Tech. {obj_name}',
                                    similarity=weight, pct_thres=e_thres, **kws)
            return elem  # .cols(1)


        def load_machine(obj_name, n_thres=1, e_thres=80, weight='cosine'):
            tags = self.filter_tags('mach', obj_name, n_thres)
            elem = tag_relation_net(tags, name=f'Machine: {obj_name}',
                                    similarity=weight, pct_thres=e_thres, **kws)
            return elem  # .cols(1)

        param_grid = {
            'tech': {
                'range': self.people,
                'func': load_person,
            },
            'mach': {
                'range': self.machs,
                'func': load_machine,
            }
        }

        dmap = hv.DynamicMap(param_grid[obj_type]['func'],
                             cache_size=1,
                             kdims=['obj_name',
                                    'n_thres',
                                    'e_thres',
                                    'weight']).options(framewise=True)
        dmap = dmap.redim.values(obj_name=param_grid[obj_type]['range'],
                                 n_thres=range(1, 20),
                                 e_thres=range(15, 90),
                                 weight=['cosine', 'count'])
        return dmap

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
    # def filter_df(self, obj_type, obj_name):
    #     is_obj = self.filter_type_name(obj_type, obj_name)
    #     return self.df[is_obj].head(50)

    # def data_table(self, obj_type, obj_name):
    #     load_path = Path('../..')/'data'/'sme_data'
    #     self.df = pd.read_csv(load_path/'MWOs_anon.csv')
    #     self.df =self.df.loc[:, ['mach', 'date_received', 'issue', 'info', 'tech']]
    #     if mask is not None:
    #         self.df =self.df.loc[self.df[mask['target']]==mask['value']].head(50)
    #     with open(Path('templates')/'includes'/'_data.html', 'w+') as fo:
    #         self.df =self.df.head(50)
    #         fo.write("<div style='overflow-y: scroll; height:600px;'>")
    #         self.df.to_html(fo, classes=['table table-striped'])
    #         fo.write("</div>")






