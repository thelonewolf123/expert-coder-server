from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


db = SQLAlchemy()


class Code(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(80), unique=True)
    code = db.Column(db.String(10000), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow())

    def __repr__(self):
        return f'{self.title}'

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(80), unique=True)

    title = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow())
    
    correct_code = db.Column(db.String(10000), nullable=False)
    starting_code = db.Column(db.String(10000), nullable=False)
    expected_output = db.Column(db.String(10000), nullable=False)
    test_inputs =  db.Column(db.String(10000), nullable=False)

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