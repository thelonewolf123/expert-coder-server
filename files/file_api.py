import uuid
import os
import ffmpeg

from db.database import db
from db.database import File
from utils.file_handling import get_file_from_dropbox
from flask import request, jsonify, Blueprint
from utils.file_handling import get_file_from_dropbox, upload_file_to_dropbox


file_blueprint = Blueprint('file', __name__)


@file_blueprint.route('/api/file', methods=['POST'])
def save_file():
    file = request.files['data']
    filename = request.form['fname']
    filepath = '/files/' + filename + '.mp4'
    input_file = f'./upload/{str(uuid.uuid4())}.mp4'
    output_file = f'./upload/{str(uuid.uuid4())}_outut.mp4'
    file.save(input_file)
    ffmpeg.input(input_file).output(output_file).run()
    if os.path.exists(input_file):
        os.remove(input_file)
    upload_file_to_dropbox(open(output_file, 'rb'), filepath)
    if os.path.exists(output_file):
        os.remove(output_file)
    uid = str(uuid.uuid4())
    file_obj = File(uid=uid, filename=filename, filepath=filepath)
    db.session.add(file_obj)
    db.session.commit()
    return dict(filename=filename, filepath=filepath, id=file_obj.uid)


@file_blueprint.route('/api/file/<id>', methods=['POST'])
def get_file(id):
    file_obj = File.filter_by(uid=id).first()
    url = get_file_from_dropbox(file_obj.filepath)
    return jsonify(dict(filename=file_obj.filename, filepath=file_obj.filepath, id=file_obj.uid, url=url))