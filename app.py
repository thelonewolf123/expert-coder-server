from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError
from dotenv import dotenv_values
import uuid
import dropbox
import os

config = dotenv_values()

# static_host = config.get('STATIC_HOST')
# if static_host == None:
#     static_host = os.environ.get('STATIC_HOST')

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

app = Flask(__name__, static_folder=static_folder, static_url_path='/')
if environment == 'development':
    CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['DROPBOX_TOKEN'] = dropbox_token
dbx = dropbox.Dropbox(app.config['DROPBOX_TOKEN'])

db = SQLAlchemy(app)


class Code(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(80), unique=True)
    code = db.Column(db.String(10000), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow())

    def __repr__(self):
        return f'{self.title}'


class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(80), unique=True)
    video_id = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100), nullable=False, unique=True)
    code_json = db.Column(db.String(100000), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow())

    def __repr__(self):
        return f'{self.title}'


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(80), unique=True)
    filename = db.Column(db.String(200), nullable=False)
    filepath = db.Column(db.String(2000), nullable=False)

    def __repr__(self):
        return f'{self.title}'


@app.route('/')
@app.route('/about')
@app.route('/videos')
@app.route('/code/<id>')
@app.route('/video/<id>/')
def index(id=1):
    return app.send_static_file('index.html')


@app.route('/api/code', methods=['POST'])
def code_post():
    code = request.json['code']
    title = request.json['title']
    uid = str(uuid.uuid4())
    code_obj = Code(uid=uid, code=code, title=title)
    db.session.add(code_obj)
    db.session.commit()
    return dict(code=code, title=title, id=code_obj.uid)


@app.route('/api/code/<id>', methods=['GET'])
def code_get(id):
    code_obj = Code.query.filter_by(uid=id).first()
    return dict(code=code_obj.code, title=code_obj.title, id=code_obj.uid)


@app.route('/api/video', methods=['POST'])
def add_video():
    if request.method == 'POST':
        video_id = request.json['video_id']
        title = request.json['title']
        code_json = request.json['code_json']
        uid = str(uuid.uuid4())
        try:
            video_obj = Video(uid=uid, video_id=video_id,
                              title=title, code_json=code_json)
            db.session.add(video_obj)
            db.session.commit()
            return dict(video_id=video_id, title=title, code_json=code_json, id=video_obj.uid)
        except Exception as e:
            print(e)
            return jsonify({"message": "Error adding video"}), 500


@app.route('/api/videos', methods=['GET'])
def get_videos():
    video_obj = Video.query.all()
    result = []
    for video in video_obj:
        result.append(dict(title=video.title, id=video.uid))
    return jsonify(result)


@app.route('/api/video/<id>', methods=['GET'])
def get_video_by_id(id):
    video_obj = Video.query.filter_by(uid=id).first()
    file_obj = File.query.filter_by(uid=video_obj.video_id).first()
    filepath = file_obj.filepath
    url = get_file_from_dropbox(filepath)
    return jsonify(url=url, title=video_obj.title, code_json=video_obj.code_json, id=video_obj.uid)


@app.route('/api/file', methods=['POST'])
def save_file():
    file = request.files['data']
    filename = request.form['fname']
    filepath = '/files/' + filename + '.webm'
    upload_file_to_dropbox(file, filepath)
    uid = str(uuid.uuid4())
    file_obj = File(uid=uid, filename=filename, filepath=filepath)
    db.session.add(file_obj)
    db.session.commit()
    return dict(filename=filename, filepath=filepath, id=file_obj.uid)


@app.route('/api/file/<id>', methods=['POST'])
def get_file(id):
    file_obj = File.filter_by(uid=id).first()
    url = get_file_from_dropbox(file_obj.filepath)
    return jsonify(dict(filename=file_obj.filename, filepath=file_obj.filepath, id=file_obj.uid, url=url))


def upload_file_to_dropbox(file_obj, filepath):
    try:
        dbx.files_upload(file_obj.read(), filepath,
                         mode=WriteMode('overwrite'))
    except ApiError as err:
        # This checks for the specific error where a user doesn't have
        # enough Dropbox space quota to upload this file
        if (err.error.is_path() and err.error.get_path().reason.is_insufficient_space()):
            print("ERROR: Cannot upload file; insufficient space.")
        elif err.user_message_text:
            print(err.user_message_text)
        else:
            print(err)


def get_file_from_dropbox(path):
    # generate a stream link for file download
    url = dbx.files_get_temporary_link(path).link
    return url


if __name__ == '__main__':
    app.run(debug=True)
