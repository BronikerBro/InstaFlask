from flask import Flask, request, Response, render_template, url_for, redirect, session, flash
from werkzeug.utils import secure_filename
import sqlite3
from db import db_init, db, db_drop,db_upgrade
from models import Img, User
from users.users  import users
import base64
import werkzeug
from sqlalchemy.exc import OperationalError

app = Flask(__name__)
app.register_blueprint(users, url_prefix="/users")
app.config['SECRET_KEY'] = b'das jkrhcfjklashjkfdhjkahfjhajk hswefajkhlefw'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///img.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db_drop(app)
# users: Tester1, asdfasdfasfd@gmail.com, 12345678
# users: Broniker Bro, nikita.tyagur.phone@gmail.com, 12345678
db_init(app)
# db_upgrade(app)
# connection = sqlite3.connect("quiz.db")
#
# cursor = connection.cursor()
# cursor.execute("DROP TABLE IF EXISTS connection_quiz_quest")
# cursor.execute("""
#     CREATE TABLE IF NOT EXISTS posts(
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         post TEXT NOT NULL,
#         likes INTEGER NOT NULL,
#         author TEXT NOT NULL,
#
#     )
# """)
def check_id():
    if session.get("user_id") == 0:
        return True

@app.route('/', methods=['GET','POST'])
def index():
    if not session.get("user_id"):
        session["user_id"] = 0
    try:
        if request.method == "GET":
            sorted = request.args.get('tpe')
            if sorted == "top":
                posts = Img.query.order_by(Img.post_liked.desc())
            else:
                posts = Img.query.order_by(Img.post_liked)
        else:
            posts = Img.query.order_by(Img.post_liked.desc())
        user_me = User.query.filter_by(id=session.get("user_id")).first()
        users_all = User.query.all()
        for post in posts:
            if post.likes == None:
                post.likes = 0
                db.session.commit()
    except OperationalError:
        return redirect(url_for("users.register"))
    return render_template("main.html", posts=posts, user_me=user_me, users_all=users_all)

@app.route('/upload', methods=['GET','POST'])
def upload():
    if check_id():
        return redirect(url_for("users.register"))
    if request.method == "POST":
        pic = request.files['pic']
        post_info = request.form.get('post_info')
        if not pic:
            flash('No pic uploaded!')
            return render_template('upload.html')
        filename = secure_filename(pic.filename)
        mimetype = pic.mimetype
        if not filename or not "image" in mimetype:
            flash('Bad upload!')
            return render_template('upload.html')
        img = pic.read()
        img = base64.b64encode(img).decode('utf8')
        img = Img(img=img, name=filename, mimetype=mimetype, user_id=session.get("user_id"), post_info = post_info )
        db.session.add(img)
        db.session.commit()
        if not session.get("user_id") == None:
            return redirect(url_for("users.profile", id = session.get("user_id")))
        else:
            return redirect(url_for("users.register"))
    return render_template('upload.html')

@app.route('/like/<int:id>/<frm>', methods=['GET','POST'])
def like(id, frm):
    if check_id():
        return redirect(url_for("users.register"))
    post = Img.query.filter_by(id=id).first()
    user_me = User.query.filter_by(id=session.get("user_id")).first()
    if post.post_liked == None:
        post.post_liked = ""
    if post.likes == None:
        post.likes = 0
    post.post_liked += ""
    lst = post.post_liked.split(",")
    if not ",("+str(user_me.id)+")" in lst:
        post.post_liked = post.post_liked + ",("+str(user_me.id)+")"
        post.likes += 1
        db.session.commit()
    if "("+str(user_me.id)+")" in lst:
        a = ",("+str(user_me.id)+")"
        post.post_liked = post.post_liked.replace(a, "")
        post.likes = post.likes-2
        db.session.commit()
    if frm == "users.profile":
        id = post.user_id
        return redirect(url_for(frm, id=id)+"/#"+str(post.id))
    elif frm == "index":
        return redirect("/#"+str(post.id))
    else:
        return redirect(url_for(frm))

@app.route('/delete_post/<int:id>', methods=['GET','POST'])
def delete_post(id):
    post = Img.query.filter_by(id=id).first()
    user_me = User.query.filter_by(id=session.get("user_id")).first()
    if user_me.id == post.user_id:
        db.session.delete(post)
        db.session.commit()
    return redirect(url_for('users.profile', id=post.user_id))

@app.route('/edit_post/<int:id>', methods=['GET','POST'])
def edit_post(id):
    post = Img.query.filter_by(id=id).first()
    user_me = User.query.filter_by(id=session.get("user_id")).first()
    if request.method == "POST":
        if user_me.id == post.user_id:
            post_info = request.form.get('post_info')
            pic = request.files['pic']
            if pic:
                filename = secure_filename(pic.filename)
                mimetype = pic.mimetype
                if not filename or not mimetype:
                    flash('Bad upload!')
                    return render_template("users/edit.html")
                post.img = base64.b64encode(pic.read()).decode('utf8')
            if post_info:
                post.post_info = post_info
            db.session.commit()
            return redirect(url_for("users.profile", id=post.user_id)+"/#"+str(post.id))
    if user_me.id == post.user_id:
        return render_template("edit.html", post=post)
    else:
        return redirect(url_for('users.profile', id=post.user_id))

@app.route('/search/', methods=['GET','POST'])
def search():
    if request.method == "POST":
        try:
            a = request.form.get("name_u")
            user = User.query.filter_by(name=a).first()
            return redirect(url_for("users.profile", id=user.id))
        except AttributeError:
            return render_template("no_found.html")
    else:
        return redirect(url_for("index"))
app.run(debug=True)