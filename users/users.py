from sqlalchemy.exc import IntegrityError
from flask import Blueprint, render_template, request, flash, url_for, redirect, session, current_app, Response
import sqlite3
from werkzeug.utils import secure_filename
import base64
from db import db
from models import User, Img

users = Blueprint("users", __name__, template_folder= "templates",  static_folder= "static")


def check_id():
    if session.get("user_id") == 0:
        return True

@users.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form.get('username')
        email_f = request.form.get('email')
        info = request.form.get('info')
        password = request.form.get('password')
        password_check = request.form.get('password_check')
        if len(password) < 8:
            flash('Password is too short!')
            return render_template("users/register.html")
        pic = request.files['pic']
        if not pic:
            flash('No pic uploaded!')
            return render_template("users/register.html")
        if not password == password_check:
            flash('Check your passwords again!')
            return render_template("users/register.html")
        filename = secure_filename(pic.filename)
        mimetype = pic.mimetype
        if not filename or not mimetype:
            flash('Bad upload!')
        try:
            logo = base64.b64encode(pic.read()).decode('utf8')
            user = User(logo = logo, mimetype = mimetype, name=username, info = info, email = email_f, password=password, followers=0)
            db.session.add(user)
            db.session.commit()
            session["user_id"] = user.id
            return redirect(url_for("users.profile", id = user.id))
        except IntegrityError:
            db.session.rollback()
            flash('Email or Username is already exists!')
            return render_template("users/register.html")
    return render_template("users/register.html")


@users.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            user = User.query.filter_by(email=email).first()
            if user.password == password:
                print(user.name)
                session["user_id"] = user.id
                return redirect(url_for("users.profile", id=user.id))
            else:
                flash('Email or password is incorrect!')
        except AttributeError:
            flash('Email or password is incorrect!')
    return render_template("users/login.html")


@users.route("/logout", methods=['GET', 'POST'])
def logout():
    if check_id():
        return redirect(url_for("users.register"))
    session["user_id"] = 0
    return redirect(url_for("index"))

@users.route("/delete", methods=['GET', 'POST'])
def delete():
    if check_id():
        return redirect(url_for("users.register"))
    user = User.query.filter_by(id=session.get("user_id")).first()
    posts = Img.query.filter_by(user_id=session.get("user_id"))
    for post in posts:
        db.session.delete(post)
        db.session.commit()
    db.session.delete(user)
    db.session.commit()
    session["user_id"] = 0
    return redirect(url_for("index"))

@users.route("/edit", methods=['GET', 'POST'])
def edit():
    if check_id():
        return redirect(url_for("users.register"))
    if request.method == "POST":
        try:
            user = User.query.filter_by(id=session.get("user_id")).first()
            username = request.form.get('username')
            info = request.form.get('info')
            pic = request.files['pic']
            if pic :
                filename = secure_filename(pic.filename)
                mimetype = pic.mimetype
                if not filename or not mimetype:
                    flash('Bad upload!')
                    return render_template("users/edit.html")
                user.logo = base64.b64encode(pic.read()).decode('utf8')
            if username:
                user.name = username
            if username:
                user.info = info
            db.session.commit()
            return redirect(url_for("users.profile", id=user.id))
        except IntegrityError:
            db.session.rollback()
            user = User.query.filter_by(id=session.get("user_id")).first()
            flash('This Username is already exists!')
            return render_template("users/edit.html", user=user)
    user = User.query.filter_by(id=session.get("user_id")).first()
    return render_template("users/edit.html", user=user)

@users.route("/profile/<int:id>/", methods=['GET', 'POST'])

def profile(id):
    if check_id():
        return redirect(url_for("users.register"))
    if session["user_id"] == None:
        return "Please login at first!"
    user = User.query.filter_by(id=id).first()
    user_me = User.query.filter_by(id=session.get("user_id")).first()
    posts = Img.query.filter_by(user_id=user.id)
    posts = list(posts)
    displ = "none"
    if session["user_id"] == user.id:
        displ = "inline"
    if posts == None:
        posts = []
    posts.reverse()
    if not user:
        return 'User Not Found!', 404
    flw = "inline"
    if user.id == session.get("user_id"):
        flw = "none"
    fol = {}
    if not user.id == user_me.id:
        if user_me.following == None:
            user_me.following = ""
        lst = user_me.following.split(",")
        if "("+str(user.id)+")" in lst:
            fol["btn"] = "secondary"
            fol["txt"] = "Stop following"
        if not "("+str(user.id)+")" in lst:
            fol["btn"] = "danger"
            fol["txt"] = "Follow"
    # return Response(user.logo, mimetype = user.mimetype)
    return render_template("users/profile.html", user=user, img=user.logo, posts = posts, displ= displ, flw=flw, fol=fol, user_me=user_me)

@users.route("/follow/<int:id>", methods=['GET', 'POST'])
def follow(id):
    if check_id():
        return redirect(url_for("users.register"))
    user = User.query.filter_by(id=id).first()
    user_me = User.query.filter_by(id=session.get("user_id")).first()
    if not user.id == user_me.id:
        if user_me.following == None:
            user_me.following = ""
        lst = user_me.following.split(",")
        if not "("+str(user.id)+")" in lst:
            user.followers += 1
            user_me.following = user_me.following + "("+str(user.id)+"),"
            db.session.commit()
        if "("+str(user.id)+")" in lst:
            user.followers -= 1
            a = "("+str(user.id)+"),"
            user_me.following = user_me.following.replace (a, ",")
            db.session.commit()
    return redirect(url_for("users.profile", id=user.id))
