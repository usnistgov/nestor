# Author: Lela Bones
# This document creates the instance of the app and runs it

from flask import Flask, request, redirect, url_for, render_template
from werkzeug import secure_filename
import pandas as pd
import holoviews as hv
from bokeh.embed import server_document
from bokeh.server.server import Server
import os, os.path
from pathlib import Path
from bokeh.themes import Theme
from tornado.ioloop import IOLoop

# from tornado.ioloop import IOLoop
# from tornado.platform.asyncio import AnyThreadEventLoopPolicy
# import asyncio
# asyncio.set_event_loop_policy(AnyThreadEventLoopPolicy())

# from .models import TagPlot
from bokeh.client import pull_session
from bokeh.embed import server_session
hv.extension('bokeh')

# renderer = renderer.instance(mode='server')
UPLOAD_FOLDER = '/tmp/'
ALLOWED_EXTENSIONS = set(['csv'])

data_dir = Path('..')/'data'/'sme_data'
print(str(data_dir))
# creates table for dashboard

""" TODO 
from bokeh.embed import server_document
from bokeh.server.server import Server

renderer = hv.renderer('bokeh')
app = renderer.app(plot)
server = Server({'/': app}, port=5006)
server.start()
html = server_document()
"""

# creates instance of the class Flask
app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# locally creates a page
@app.route('/')
def index():
    # loads the template home
    return render_template('home.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('index'))
    return """
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    <p>%s</p>
    """ % "<br>".join(os.listdir(app.config['UPLOAD_FOLDER'],))


# locally creates a page
@app.route('/about')
def about():
    # load the template about
    return render_template('about.html')


# locally creates a page
@app.route('/dashboard')
def dashboard():
    # data_table()
    # TODO make this trigger with dropdown

    # load the template dashboard
    return render_template('dashboard.html')

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
        
        server = remderer.app(dmap)
    
# locally creates a page
@app.route('/bar', methods=['GET'])
def bar():
#     # load the template Bar Graph
#     tagplot = TagPlot(data_dir/'MWOs_anon.csv', data_dir/'binary_tags.h5')
#     bars = tagplot.hv_bars('mach')
#     bars = bars.options(height=300, width=600)
#     plot = hv.renderer('bokeh').get_plot(bars).state
#     script, div = components(plot)
#     # load the template Node Graph
#     tagplot.data_table('mach', 'A14')

#     return render_template('bar.html', the_div=div, the_script=script)
    # pull a new session from a running Bokeh serve
#    with pull_session(url="http://localhost:5006") as session:

#         session.document.roots[0].title.text = "Special Plot Title For A Specific User!"
        
        # generate a script to load the customized session
        script = server_document('http://localhost:5006/bkapp')

        # use the script in the rendered page
        return render_template("bar.html", script=script, template="Flask")

def bk_worker():
    server.start()
    server.io_loop.start()

        
# locally creates a page
# @app.route('/node', methods=['GET'])
# def node():
#     # print(str(data_dir/'MWOs_anon.csv'))
#     tagplot = TagPlot(data_dir/'MWOs_anon.csv', data_dir/'binary_tags.h5')
#     hmap = tagplot.hv_nodelink()
#     hmap = hmap.options(height=500, width=500, xaxis=None, yaxis=None, title_format='{label}')

#     renderer = hv.renderer('bokeh')#.instance(mode='server')

#     # app = renderer.app(dmap)
#     # loop = IOLoop.instance()
#     # loop.start()
#     # server = Server({'/':app}, port=0)
#     # server.start()
#     # html = server_document()

#     plot = renderer.get_plot(hmap).state
#     # div = renderer.static_html(hmap)
#     # plot.title = 'Nodelink Diagram'
#     script, div = components(plot)

#     # load the template Node Graph
#     return render_template('node.html', the_div=div, the_script=script)
#     # return render_template('node.html', the_script=html)


# locally creates a page
@app.route('/flow')
def flow():    
    # load the template Flow Graph
    return render_template('flow.html')


# locally creates a page
@app.route('/help')
def help_page():
    return render_template('help.html')

from threading import Thread
Thread(target=bk_worker).start()

if __name__ == '__main__':
    # runs app in debug mode
    app.run(debug=True)
    # app.run()
  