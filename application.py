from flask import Flask
from flask_cors import CORS
from dotenv import dotenv_values
from db.database import db
from video.video_api import video_blueprint
from files.file_api import file_blueprint
from code_api.code_api import code_blueprint

import os

config = dotenv_values()

static_folder = config.get('STATIC_FOLDER')
if static_folder == None:
    static_folder = os.environ.get('STATIC_FOLDER')

dropbox_token = config.get('DROPBOX_TOKEN')
if dropbox_token == None:
    dropbox_token = os.environ.get('DROPBOX_TOKEN')

database_uri = config.get('DATABASE_URI')
if database_uri == None:
    database_uri = os.environ.get('DATABASE_URI')

environment = config.get('FLASK_ENV')
if environment == None:
    environment = os.environ.get('FLASK_ENV')

run_python_api = config.get('RUN_PYTHON_API')
if run_python_api == None:
    run_python_api = os.environ.get('RUN_PYTHON_API')

app = Flask(__name__, static_folder=static_folder, static_url_path='/')

if environment == 'development':
    CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['DROPBOX_TOKEN'] = dropbox_token
app.config['RUN_PYTHON_API'] = run_python_api

db.init_app(app)

app.register_blueprint(video_blueprint)
app.register_blueprint(file_blueprint)
app.register_blueprint(code_blueprint)


@app.route('/')
@app.route('/about')
@app.route('/videos')
@app.route('/code/<id>')
@app.route('/video/<id>/')
def index(id=None):
    return app.send_static_file('index.html')



if __name__ == '__main__':
    app.run(debug=True)
