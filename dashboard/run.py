from flaskDash import app#, serve_bokeh_tags
import os
# from pathlib import Path
#
# data_dir = Path('..') / 'data' / 'sme_data'
# serve_bokeh_tags(data_dir)


app.secret_key = os.urandom(24)
app.run(debug=True)
