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

from .models import TagPlot
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
feature_names = ['Machines', 'Technicians']
# locally creates a page
@app.route('/bar')
def bar():
        current_feature_name = request.args.get('feature_name')
        if current_feature_name == None:
            current_feature_name = "Machines"
        if current_feature_name == 'Machines':
            with pull_session(url="http://localhost:5006/bars_mach") as session:
                # generate a script to load the customized session
                script = server_session(session_id=session.id, url='http://localhost:5006/bars_mach')
                # use the script in the rendered page
        if current_feature_name == 'Technicians':
            with pull_session(url="http://localhost:5006/bars_tech") as session:
                # generate a script to load the customized session
                script = server_session(session_id=session.id, url='http://localhost:5006/bars_tech')
                # use the script in the rendered page
        return render_template("bar.html", script=script, template="Flask", feature_names=feature_names,  current_feature_name=current_feature_name)
#             return render_template("bar.html", script=script, template="Flask")
        
# locally creates a page
@app.route('/node')
def node():
        current_feature_name = request.args.get('feature_name')
        if current_feature_name == None:
            current_feature_name = "Machines"
        if current_feature_name == 'Machines':
            with pull_session(url="http://localhost:5006/node_mach") as session:
                # generate a script to load the customized session
                script = server_session(session_id=session.id, url='http://localhost:5006/node_mach')
                # use the script in the rendered page
        if current_feature_name == 'Technicians':
            with pull_session(url="http://localhost:5006/node_tech") as session:
                # generate a script to load the customized session
                script = server_session(session_id=session.id, url='http://localhost:5006/node_tech')
                # use the script in the rendered page
        return render_template("node.html", script=script, template="Flask", feature_names=feature_names,  current_feature_name=current_feature_name)


# locally creates a page
@app.route('/flow')
def flow():    
        current_feature_name = request.args.get('feature_name')
        if current_feature_name == None:
            current_feature_name = "Machines"
        if current_feature_name == 'Machines':
            with pull_session(url="http://localhost:5006/flow_mach") as session:
                # generate a script to load the customized session
                script = server_session(session_id=session.id, url='http://localhost:5006/flow_mach')
                # use the script in the rendered page
        if current_feature_name == 'Technicians':
            with pull_session(url="http://localhost:5006/flow_tech") as session:
                # generate a script to load the customized session
                script = server_session(session_id=session.id, url='http://localhost:5006/flow_tech')
                # use the script in the rendered page
        return render_template("flow.html", script=script, template="Flask", feature_names=feature_names,  current_feature_name=current_feature_name)


# locally creates a page
@app.route('/help')
def help_page():
    return render_template('help.html')


if __name__ == '__main__':
    # runs app in debug mode
    from werkzeug.wsgi import DispatcherMiddleware
    from models import app as backend

    application = DispatcherMiddleware(app, {
        '/backend':     backend
    })
#         app.run(debug=True)
        # app.run()
  