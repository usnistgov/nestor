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
   with pull_session(url="http://localhost:5006") as session:

#         session.document.roots[0].title.text = "Special Plot Title For A Specific User!"
        
        # generate a script to load the customized session
        script = server_session(session_id=session.id, url='http://localhost:5006')

        # use the script in the rendered page
        return render_template("bar.html", script=script, template="Flask")

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


if __name__ == '__main__':
    # runs app in debug mode
    app.run(debug=True)
    # app.run()
  