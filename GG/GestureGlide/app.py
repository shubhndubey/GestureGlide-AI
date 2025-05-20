import pickle
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with a strong secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' 

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route('/')
def home():
    return render_template('base.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials, please try again.')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user is None:
            user = User(username=username, password=password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Username already exists, please choose another.')
    return render_template('signup.html')

@app.route('/index')
@login_required
def index():
    return render_template('index.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/about')
def about():
    return render_template('about.html')


import subprocess
import os
import webbrowser
import socket
import time

def wait_for_port(host, port, timeout=15):
    start_time = time.time()
    while time.time() - start_time < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.connect((host, port))
                return True
            except ConnectionRefusedError:
                time.sleep(0.5)
    return False

@app.route('/launch_math_solver')
def launch_math_solver():
    script_path = r"C:\Users\ASUS\Desktop\GG\main1_refactored_streamlit.py"
    subprocess.Popen(["streamlit", "run", script_path], shell=True)
    if wait_for_port('localhost', 8501):
        webbrowser.open_new_tab("http://localhost:8501")
        return "Launched Math Solver"
    else:
        return "Streamlit app failed to launch in time."

@app.route('/launch_emotion_detector')
def launch_emotion_detector():
    script_path = r"C:\Users\ASUS\Desktop\GG\emotion_detector_streamlit.py"
    subprocess.Popen(["streamlit", "run", script_path], shell=True)
    if wait_for_port('localhost', 8502):
        webbrowser.open_new_tab("http://localhost:8502")
        return "Launched Emotion Detector"
    else:
        return "Streamlit app failed to launch in time."



if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure database is created
    app.run(debug=True)
