# Author: Lela Bones
# This document creates the instance of the app and runs it

from flask import Flask, render_template
import pandas as pd
import tablib
import os, os.path
from pathlib import Path

#creates table for dashboard
def data_table():
    load_path = Path('data')
    dataset = tablib.Dataset()
    with open(os.path.join(load_path, 'full_tech_names.csv')) as f:
        dataset.csv = f.read()

        save_path =  Path('data')/templates/includes
        completeName = os.path.join(save_path, '_data.html')
        df = open(completeName, "w+")
        df.write("<div class='table-responsive pre-scrollable'>")
        df.write("<table class='table table-striped'>")
        df.write(dataset.html[7:])
        df.write("</table>")
        df.write("</div>") 
        df.close()

# creates instance of the class Flask
app = Flask(__name__)

#locally creates a page
@app.route('/')
def index():
    #loads the template home
    return render_template('home.html')

#locally creates a page
@app.route('/about')
def about():
    #load the template about
    return render_template('about.html')

#locally creates a page
@app.route('/dashboard')
def dashboard():
    #load the template dashboard
    return render_template('dashboard.html')

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
    
  