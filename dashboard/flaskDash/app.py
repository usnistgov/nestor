# Author: Lela Bones
# This document creates the instance of the app and runs it

from flask import Flask, render_template
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
    #load the template dashboard
    return render_template('help.html')
    
if __name__ == '__main__':
    #runs app in debug mode
    app.run(debug=True)