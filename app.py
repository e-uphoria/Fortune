from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
import random

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(150), unique=True, nullable=False)
    birthdate = db.Column(db.Date, nullable=False)
    streak = db.Column(db.Integer, default=0)
    last_lucky_day = db.Column(db.Date)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        full_name = request.form['full_name']
        username = request.form['username']
        birthdate = datetime.strptime(request.form['birthdate'], '%Y-%m-%d').date()

        age = (datetime.utcnow().date() - birthdate).days // 365

        if age < 16:
            flash('You must be at least 16 years old to sign up.', 'danger')
            return redirect(url_for('signup'))

        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose another one.', 'danger')
            return redirect(url_for('signup'))

        new_user = User(full_name=full_name, username=username, birthdate=birthdate)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(username=username).first()

        if user:
            login_user(user)
            return redirect(url_for('fortune'))
        else:
            flash('Invalid username. Please try again.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/fortune')
@login_required
def fortune():
    return render_template('fortune.html', streak=current_user.streak, last_lucky_day=current_user.last_lucky_day, current_user=current_user)

@app.route('/spin', methods=['POST'])
@login_required
def spin():
    score = request.json.get('score', random.randint(0, 10))

    if 0 <= score <= 3:
        message = random.choice(["You might need a bit of luck today!", "You're going to have a bad day, so work hard."])
    elif 4 <= score <= 7:
        message = random.choice(["A decent day ahead, keep going!", "Good things come to those who wait."])
    else:
        message = random.choice(["Congratulations! It’s a lucky day!", "Success is inevitable today!"])

    user = current_user
    today = datetime.utcnow().date()

    if score >= 8:
        if user.last_lucky_day and user.last_lucky_day == today - timedelta(days=1):
            user.streak += 1
        else:
            user.streak = 1
        user.last_lucky_day = today
    else:
        user.streak = 0

    db.session.commit()

    return jsonify({
        "score": score,
        "message": message,
        "streak": user.streak,
        "last_lucky_day": user.last_lucky_day.strftime('%Y-%m-%d') if user.last_lucky_day else None
    })

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
