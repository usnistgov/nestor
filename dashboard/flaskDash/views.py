# Author: Lela Bones
# This document creates the instance of the app and runs it

from flask import Flask, request, redirect, url_for, render_template
from werkzeug import secure_filename
import pandas as pd
import holoviews as hv
from bokeh.embed import components, server_document
import os, os.path
from pathlib import Path
from .plots import TagPlot

hv.extension('bokeh')
renderer = hv.renderer('bokeh')
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
@app.route('/bar')
def Bar():
    # load the template Bar Graph
    tagplot = TagPlot(data_dir/'MWOs_anon.csv', data_dir/'binary_tags.h5')
    bars = tagplot.hv_bar('tech')
    bars = bars.options(height=300, width=600)
    plot = hv.renderer('bokeh').get_plot(bars).state
    script, div = components(plot)
    # load the template Node Graph
    return render_template('bar.html', the_div=div, the_script=script)


# locally creates a page
@app.route('/node')
def Node():
    print(str(data_dir/'MWOs_anon.csv'))
    tagplot = TagPlot(data_dir/'MWOs_anon.csv', data_dir/'binary_tags.h5')
    dmap = tagplot.hv_nodelink('tech')
    dmap = dmap.options(height=500, width=500, xaxis=None, yaxis=None, title_format='{label}')
    plot = renderer.server_doc(dmap)#.state
    script, div = components(plot)
    # load the template Node Graph
    return render_template('node.html', the_div=div, the_script=script)


# locally creates a page
@app.route('/flow')
def Flow():    
    # load the template Flow Graph
    return render_template('flow.html')


# locally creates a page
@app.route('/help')
def help_page():
    return render_template('help.html')


@app.route('/flow')
def flow():
    return render_template('includes/_flow.html')


if __name__ == '__main__':
    # runs app in debug mode
    app.run(debug=True)
    # app.run()
  