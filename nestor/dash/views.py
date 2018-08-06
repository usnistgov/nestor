# Author: Lela Bones
# This document creates the instance of the app and runs it

import holoviews as hv
import os, os.path
from pathlib import Path
from bokeh.client import pull_session
from bokeh.embed import server_session
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from flask import send_from_directory
import io
import base64
hv.extension('bokeh')

app_location = Path(__file__).parent

app = Flask(__name__, template_folder=app_location/'templates')

# renderer = renderer.instance(mode='server')

print("making directory '.nestor-tmp'")
UPLOAD_FOLDER = Path.home()/'.nestor-tmp'
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = set(['csv', 'h5'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
FILES = []

from nestor.dash.models import DataModel
data_model = DataModel()

hostname='localhost'
# data_dir = Path('..') / 'data' / 'sme_data'
# df = pd.read_csv(data_dir  / 'MWOs_anon.csv')
# tf = pd.read_hdf(data_dir / 'binary_tags.h5')

def data_table(self):
    
        df = self.loc[:, ['mach',
                          'date_received',
                          'issue',
                          'info',
                          'tech']]
        with open(Path('flaskDash')/'templates'/'includes'/'_data.html', 'w+') as fo:
            # \df =self.df.head(50)
            fo.write("<div style='overflow-y: scroll; height:600px;'>")
            df.to_html(fo, classes=['table table-striped'])
            fo.write("</div>")
    
# locally creates a page
@app.route('/')
def index():
    # loads the template home
    return render_template('home.html')




def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # save_loc = Path(app.root_path)/app.config['UPLOAD_FOLDER']/filename
            save_loc = app.config['UPLOAD_FOLDER']/filename
            # print(save_loc)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file.close()
            FILES.append(filename)

            data_model.set_data_location(save_loc)
            proc = data_model.serve_data()

            # return render_template('upload.html', filename=FILES)
    return render_template('upload.html', filename=FILES)

from flask import send_from_directory

# locally creates a page
@app.route('/about')
def about():
    # load the template about
    return render_template('about.html')


# locally creates a page
@app.route('/dashboard')
def dashboard():
    # problems = tf.P.sum().sort_values(ascending=False)[:10]
    # probGraph = problems.plot(kind='bar', title = "Problem Tags")
    # probGraph.set_xlabel("Aliases")
    # probGraph.set_ylabel("Occurence")
    # data_table(df)
    return render_template('dashboard.html')


# assigns the feature names for the dropdown
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
            with pull_session(url='http://localhost:5006/node_tech') as session:
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


def main():
    app.secret_key='super secret key'
    app.run(port=5000, debug=True, host='0.0.0.0')


if __name__ == '__main__':
    # runs app in debug mode
        main()
        # app.run()
  