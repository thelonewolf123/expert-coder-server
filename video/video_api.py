import uuid

from db.database import db
from db.database import Video, File
from utils.file_handling import get_file_from_dropbox
from flask import request, jsonify, Blueprint


video_blueprint = Blueprint('video', __name__)


@video_blueprint.route('/api/videos', methods=['GET'])
def get_videos():
    video_obj = Video.query.all()
    result = []
    for video in video_obj:
        result.append(dict(title=video.title, id=video.uid))
    return jsonify(result)


@video_blueprint.route('/api/video', methods=['POST'])
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


@video_blueprint.route('/api/video/<id>', methods=['GET'])
def get_video_by_id(id):
    video_obj = Video.query.filter_by(uid=id).first()
    file_obj = File.query.filter_by(uid=video_obj.video_id).first()
    filepath = file_obj.filepath
    url = get_file_from_dropbox(filepath)
    return jsonify(url=url, title=video_obj.title, code_json=video_obj.code_json, id=video_obj.uid)