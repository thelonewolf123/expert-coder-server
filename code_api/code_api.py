import uuid
import requests
import os

from flask import request, Blueprint
from db.database import db, Code
from dotenv import dotenv_values


code_blueprint = Blueprint('code_api', __name__)


@code_blueprint.route('/api/code', methods=['POST'])
def code_post():
    code = request.json['code']
    title = request.json['title']
    uid = str(uuid.uuid4())
    code_obj = Code(uid=uid, code=code, title=title)
    db.session.add(code_obj)
    db.session.commit()
    return dict(code=code, title=title, id=code_obj.uid)


@code_blueprint.route('/api/execute_code', methods=['POST'])
def code_execute():
    code = request.json['code']
    fileName = request.json['fileName']
    stdin = request.json['stdin']

    config = dotenv_values()

    run_python_api = config.get('RUN_PYTHON_API')
    if run_python_api == None:
        run_python_api = os.environ.get('RUN_PYTHON_API')

    req = requests.post(run_python_api, json={'code': code, 'fileName': fileName, 'stdin': stdin})
    response = req.json()

    return dict(output=response['output'], stderr=response['stderr'], error=response['error'])



@code_blueprint.route('/api/code/<id>', methods=['GET'])
def code_get(id):
    code_obj = Code.query.filter_by(uid=id).first()
    return dict(code=code_obj.code, title=code_obj.title, id=code_obj.uid)