#!/usr/bin/env python
#
# This file is part of Nestor. It is subject to the license terms in the file
# LICENSE.rst found in the top-level directory of this distribution.


from bokeh.server.server import Server
import holoviews as hv
from tornado.ioloop import IOLoop
from pathlib import Path
import sys, urllib, nestor
from nestor.tagplots import TagPlot
from itertools import product

nestorParams = nestor.CFG


def serve_bokeh_tags(hdfstore):
    projectsPath = Path.home() / '.nestor-tmp'
    projectsPath.mkdir(parents=True, exist_ok=True)
    # nestorPath = Path(__file__).parent.parent
    # databaseToCsv_mapping = openYAMLConfig_File(
    #     yaml_path=nestorPath / 'store_data' / 'csvHeader.yaml'
    # )

    # names = load_header_mapping()
    # tech = names['technician']['name']
    # mach = names['machine']['name']

    tagplot = TagPlot(hdfstore, cat_specifier='name', topn=10)

    renderer = hv.renderer('bokeh').instance(mode='server')

    server = Server({
        **{
            '/' + urllib.parse.quote_plus(name)+'.bars':
                renderer.app(tagplot.hv_bars(name).options(width=900))
            for name in tagplot.names
        },
        **{
            '/' + urllib.parse.quote_plus(name)+'.node':
                renderer.app(tagplot.hv_nodelink(name).options(width=900))
            for name in tagplot.names
        },
        **{
            '/' + urllib.parse.quote_plus(name)+'.flow':
                renderer.app(tagplot.hv_flow(name).options(width=900))
            for name in tagplot.names
        }

    }, port=5006, allow_websocket_origin=[
        "127.0.0.1:5000", 
        "localhost:5000", 
        "localhost:5006", 
        "0.0.0.0:5000", 
        "0.0.0.0:5006"                                     
    ])
    server.start()
    # server.show('/')
    loop = IOLoop.current()
    loop.start()

def main():
    file_loc = sys.argv[1]
    serve_bokeh_tags(file_loc)


if __name__ == '__main__':
    main()