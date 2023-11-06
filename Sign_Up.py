import flask
from flask import Flask
from flask import render_template, url_for
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

app = Flask(__name__)

# Create a connection to the database using mysql and + pymysql
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/New_User_Database'
app.config['SECRET_KEY'] = 'TooTopSecrete'
db.init_app(app)

# create thee applicarion object
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int (user_id))


# Create a Table class using flask_sqlaclhemy
class Users(db.Model, UserMixin):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(30))
    password: Mapped[str] = mapped_column(CHAR(80))

with app.app_context():
    db.create_all()


# view route page for home
@app.route('/')
def home():
    return render_template('home.html')



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
        Valid_user_email = Users.query.filter_by(email=mail).first_or_404()
        if Valid_user_email:
            valid_password = Users.query.filter_by(password=password).first_or_404()
            if valid_password:
                login_user(Valid_user_email)
                next = flask.request.args.get('next')
                def url_has_allowed_host_and_scheme(url, allowed_hosts, require_https=False):
                    if url is not None:
                        url = url.strip()
                    if not url:
                        return False
                    if allowed_hosts is None:
                        allowed_hosts = set()
                    elif isinstance(allowed_hosts, str):
                        allowed_hosts = {allowed_hosts}
                        # Chrome treats \ completely as / in paths but it could be part of some
                        # basic auth credentials so we need to check both URLs.
                    return (
                            _url_has_allowed_host_and_scheme(url, allowed_hosts, require_https=require_https) and
                            _url_has_allowed_host_and_scheme(url.replace('\\', '/'), allowed_hosts,
                                                             require_https=require_https)
                    )
                # return render_template('dashboard.html', user_name=Valid_user_email.username)
                return redirect(url_for('dashboard', user_name=Valid_user_email.username))
    return render_template('login.html')


# view route page for Dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')


# view route page for sign up
@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        new_user = Users(
            username=request.form['username'],
            email=request.form['email'],
            password=request.form['password'],
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login', ))

    return render_template('sign_up.html')


if __name__ == '__main__':
    app.run(debug=True)
