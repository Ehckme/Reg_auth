import flask
from flask import Flask, sessions
from flask_session import Session
from flask import render_template, url_for, make_response
from flask import request, redirect
from sqlalchemy import ForeignKey, String, Integer, CHAR
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import relationship, mapped_column
from sqlalchemy import create_engine, engine, Select, select
from sqlalchemy.orm import Session, session
from flask_sqlalchemy import SQLAlchemy

# import flask login
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user, current_user


# create an inheritance class from DeclarativeBase
class Base(DeclarativeBase):
    pass


# instan
db = SQLAlchemy(model_class=Base)

SESSION_TYPE = 'sqlalchemy'
app = Flask(__name__)

# Create a connection to the database using mysql and + pymysql
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/New_User_Database'
# config secrete key
app.config['SECRET_KEY'] = 'TooTopSecrete'

# initialize database app
db.init_app(app)

session = Session(app)

# create thee applicarion object
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


# Create a Table class using flask_sqlaclhemy
class Users(db.Model, UserMixin):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(30))
    password: Mapped[str] = mapped_column(CHAR(80))


with app.app_context():
    db.create_all()


# view route page for home
@app.route('/', methods=['GET'])
def home():
    return render_template('login.html')


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Users, int(user_id))
    # return Users.query.get(int(user_id))


# view route page for login
@app.route('/login', methods=['GET', 'POST'])
def login():

    mail = request.form.get('email', False)
    password = request.form.get('password', False)
    if request.method == 'POST':
        valid_user_email = Users.query.filter_by(email=mail).first_or_404()
        if valid_user_email:
            valid_password = Users.query.filter_by(password=password).first_or_404()
            if valid_password:
                login_user(valid_user_email)

                # return render_template('dashboard.html', user_name=Valid_user_email.username)
                return redirect(url_for('dashboard', user_username=valid_user_email.username))
    return render_template('login.html')


# view route page for Dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():

    return render_template('dashboard.html')


# view route page for sign up
@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    user_email = request.form.get('email', False)
    if request.method == 'POST':
        new_user = Users(
            username=request.form.get('username', False),
            email=request.form.get('email', False),
            password=request.form.get('password', False),
        )

        email_in_database = Users.query.filter_by(email=user_email).first()
        if email_in_database:
            return redirect(url_for('sign_up'))
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login', ))

    return render_template('sign_up.html')


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)
