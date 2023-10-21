from flask import Flask
from flask import render_template, url_for
from flask import request, redirect
from sqlalchemy import ForeignKey, String, Integer, CHAR
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import relationship, mapped_column
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from flask_sqlalchemy import SQLAlchemy


# create an inheritance class from DeclarativeBase
class Base(DeclarativeBase):
    pass

# instan
db = SQLAlchemy(model_class=Base)

app = Flask(__name__)

# Create a connection to the database using mysql and + pymysql
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/New_User_Database'
db.init_app(app)

# Create a Table class using flask_sqlaclhemy
class Users(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(30))
    password: Mapped[str] = mapped_column(CHAR(30))

with app.app_context():
    db.create_all()


# view route page for home
@app.route('/')
def home():
    return render_template('home.html')

# view route page for login
@app.route('/login')
def login():
    return render_template('login.html')

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
