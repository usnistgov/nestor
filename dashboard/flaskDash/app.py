# Author: Lela Bones
# This document creates the instance of the app and runs it

from flask import Flask, request, redirect, url_for, render_template
from werkzeug import secure_filename
import pandas as pd
import os, os.path
from pathlib import Path


UPLOAD_FOLDER = '/tmp/'
ALLOWED_EXTENSIONS = set(['csv'])

#creates table for dashboard
def data_table(mask=None):
    load_path = Path('data')
    df = pd.read_csv(load_path/'MWOs_anon.csv')
    df = df.loc[:, ['mach', 'date_received', 'issue', 'info', 'tech']]
    if mask is not None:
    	df = df.loc[df[mask['target']]==mask['value']].head(50)
    with open(Path('templates')/'includes'/'_data.html', 'w+') as fo:
        df = df.head(50)
        fo.write("<div style='overflow-y: scroll; height:600px;'>")
        df.to_html(fo, classes=['table table-striped'])
        fo.write("</div>")


# creates instance of the class Flask
app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

#locally creates a page
@app.route('/')
def index():
    #loads the template home
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


#locally creates a page
@app.route('/about')
def about():
    #load the template about
    return render_template('about.html')

#locally creates a page
@app.route('/dashboard')
def dashboard():
	data_table()  
	# TODO make this trigger with dropdown
    
    # load the template dashboard
	return render_template('dashboard.html')

#locally creates a page
@app.route('/bar')
def Bar():
    # load the template Bar Graph
	return render_template('bar.html')

#locally creates a page
@app.route('/node')
def Node():
    # load the template Node Graph
	return render_template('node.html')

#locally creates a page
@app.route('/flow')
def Flow():    
    # load the template Flow Graph
	return render_template('flow.html')

#locally creates a page
@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/flow')
def flow():
    return render_template('includes/_flow.html')
    
if __name__ == '__main__':
    #runs app in debug mode
    app.run(debug=True)
    
  