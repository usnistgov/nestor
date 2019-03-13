#!/usr/bin/env python
#
# This file is part of Nestor. It is subject to the license terms in the file
# LICENSE.rst found in the top-level directory of this distribution.


from bokeh.server.server import Server
import holoviews as hv
from tornado.ioloop import IOLoop
import sys
from nestor.tagplots import TagPlot
from nestor.ui.taggingUI_app import openYAMLConfig_File


def serve_bokeh_tags(hdfstore):
    projectsPath = Path.home() / '.nestor-tmp'
    projectsPath.mkdir(parents=True, exist_ok=True)
    nestorPath = Path(__file__).parent.parent
    databaseToCsv_mapping = openYAMLConfig_File(
        yaml_path=nestorPath / 'store_data' / 'csvHeader.yaml'
    )

    names = load_header_mapping()
    tech = names['technician']['name']
    mach = names['machine']['name']

    tagplot = TagPlot(hdfstore, tech=tech, mach=mach)

    renderer = hv.renderer('bokeh').instance(mode='server')


    server = Server({
        '/bars_tech': renderer.app(tagplot.hv_bars(tech).options(width=900)),
        '/bars_mach': renderer.app(tagplot.hv_bars(mach).options(width=900)),
        '/node_tech': renderer.app(tagplot.hv_nodelink(tech).options(width=600, height=600)),
        '/node_mach': renderer.app(tagplot.hv_nodelink(mach).options(width=600, height=600)),
        '/flow_tech': renderer.app(tagplot.hv_flow(tech).options(width=900, height=600)),
        '/flow_mach': renderer.app(tagplot.hv_flow(mach).options(width=900, height=600)),
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