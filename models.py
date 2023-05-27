from db import db
import datetime

class Img(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.Text, unique=False, nullable=False)
    name = db.Column(db.Text, nullable=False)
    mimetype = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, unique=False)
    post_info = db.Column(db.Text, nullable=False)
    post_liked = db.Column(db.Text)
    likes = db.Column(db.Integer, default=0)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    logo = db.Column(db.Text, unique=False, nullable=False)
    mimetype = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text, unique=True, nullable=False)
    info = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    followers = db.Column(db.Integer)
    following = db.Column(db.Text)