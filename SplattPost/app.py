from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
import secrets
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ユーザーモデル
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    videos = db.relationship('Video', backref='owner', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)

# 動画モデル
class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    date_uploaded = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# コメントモデル
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    videos = current_user.videos
    comments = current_user.comments
    return render_template('dashboard.html', videos=videos, comments=comments)

@app.route('/upload', methods=['POST'])
@login_required
def upload():
    if 'file' not in request.files:
        return redirect(url_for('dashboard'))
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('dashboard'))
    filename = secrets.token_hex(8) + os.path.splitext(file.filename)[1]
    file.save(os.path.join('uploads', filename))
    new_video = Video(filename=filename, owner=current_user)
    db.session.add(new_video)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/comment', methods=['POST'])
@login_required
def comment():
    text = request.form['text']
    new_comment = Comment(text=text, author=current_user)
    db.session.add(new_comment)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/post_to_twitter', methods=['POST'])
@login_required
def post_to_twitter():
    # Twitter APIを使用して投稿するロジックをここに追加
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
