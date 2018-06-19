# Author: Lela Bones
# This document creates the instance of the app and runs it

from flask import Flask, render_template
import pandas as pd
import tablib
import os, os.path


# creates instance of the class Flask
app = Flask(__name__)

#loading in dataset
dataset = tablib.Dataset()
with open(os.path.join(os.path.dirname(__file__),'mine_vocab_1g.csv')) as f:
    dataset.csv = f.read()
    
    save_path = '/home/msid/ltb3/TagApp/nestor/dashboard/flaskDash/templates/includes/'
    completeName = os.path.join(save_path, '_data.html')
    df = open(completeName, "w+")
    df.write("<div class='table-responsive pre-scrollable'>")
    df.write("<table class='table table-striped'>")
    df.write(dataset.html[7:])
    df.write("</table>")
    df.write("</div>") 
    df.close()
    
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
    
if __name__ == '__main__':
    #runs app in debug mode
    app.run(debug=True)
    
  