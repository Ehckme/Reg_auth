import flask
import requests
from flask import Flask
from flask import render_template, url_for, session
from flask import request, redirect
from sqlalchemy import String, Integer, CHAR
<<<<<<< HEAD
from sqlalchemy import create_engine
=======
from sqlalchemy import create_engine, select
>>>>>>> 295c9529c02880ca50f2bb4a3b2838c41d16412d
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Session, sessionmaker
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.types import Boolean
import dns.resolver

import dns.resolver

# import flask login
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user


# create an inheritance class from DeclarativeBase
class Base(DeclarativeBase):
    pass

sql_session = sessionmaker()
# instan
db = SQLAlchemy(model_class=Base)

SESSION_TYPE = 'sqlalchemy'
app = Flask(__name__)

# Create a connection to the database using mysql and + pymysql
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/New_User_Database'
# config secrete key
app.config['SECRET_KEY'] = 'TooTopSecrete'

engine = create_engine('mysql+pymysql://root:root@localhost/New_User_Database')
sess = Session(engine)
# initialize database app
db.init_app(app)

# create the application object
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


# Create a Table class using flask-sqlaclhemy
class Users(db.Model, UserMixin):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(30))
    password: Mapped[str] = mapped_column(CHAR(80))
    confirmed: Mapped[bool] = mapped_column(nullable=False, default=False)
    otp: Mapped[int] = mapped_column(nullable=True)


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
                is_confirmed = valid_user_email.confirmed
                if is_confirmed == True:
                    login_user(valid_user_email)
                    print(is_confirmed)
                    return redirect(url_for('dashboard', user_username=valid_user_email.username))
                else:
                    return redirect(url_for('confirm'))

                # return render_template('dashboard.html', user_name=Valid_user_email.username)

    return render_template('login.html')


# view route page for Dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():

    return render_template('dashboard.html')


""" create OTP code """
import random
def random_otp():
    otp = ''.join([str(random.randint(0000, 9999)) for i in range(1)])
    return otp
OTP = random_otp()


# view route page for sign up
@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    user_email = request.form.get('email', False)
    user_name = request.form.get('username', False)

    session['username'] = request.form.get('username', False)
    if request.method == 'POST':
        new_user = Users(
            username=request.form.get('username', False),
            email=request.form.get('email', False),
            password=request.form.get('password', False),
        )

        email_in_database = Users.query.filter_by(email=user_email).first()
        if email_in_database:
            print('Email already exists')
            return redirect(url_for('sign_up'))
        else:
            """ Split domain from user_email input"""
            domain = user_email.split('@')[1]

            """ Check the existence of domain
                and catch  the error with try-except method. 
            """
            try:
                dns_address = dns.resolver.resolve(f'{domain}', 'A')
                for dns_a in dns_address:
                    print('A record : ', dns_a.to_text())
                    db.session.add(new_user)
                    db.session.commit()

                    # send email
                    import smtplib
                    from email.mime.multipart import MIMEMultipart
                    from email.mime.text import MIMEText

                    message = MIMEMultipart()
                    """ Send SMTP message to user_email input """
                    message['To'] = user_email
                    message['From'] = 'ehckmedev@gmail.com'
                    message['Subject'] = 'CONFIRM'

                    title = '<b> CONFIRM OTP-CODE </b>'

                    messageText = MIMEText(
                        f''' Hello {user_name}, your OTP-Code is: {OTP}  ''', 'html'
                    )
                    message.attach(messageText)

                    """ Sender infor email and app password """
                    sender_email = 'ehckmedev@gmail.com'
                    app_password = 'iyjf yndm yoxb qysh'

                    server = smtplib.SMTP('smtp.gmail.com:587')
                    server.ehlo('Gmail')
                    server.starttls()
                    server.login(sender_email, app_password)

                    fromaddr = sender_email
                    toaddr = user_email
                    server.sendmail(fromaddr, toaddr, message.as_string())
                    server.quit()

                    return redirect(url_for('confirm', new_user=new_user.username))

            except dns.exception.DNSException:
                print('Invalid Email')
                return redirect(url_for('sign_up'))

    return render_template('sign_up.html')


@app.route('/confirm', methods=['GET', 'POST'])
def confirm():
    if request.method == 'POST':
        user_input_otp = request.form.get('otp', False)
        if user_input_otp != OTP:

            print('Invalid OTP pin')
        elif user_input_otp == OTP:
            print('Your OTP is: ', OTP)
            if 'username' in session:
                username = session['username']
                is_username_in_db = Users.query.filter_by(username=username).first_or_404()
                is_username_in_db.confirmed = True
                is_username_in_db.otp = OTP
                session['otp'] = OTP
                db.session.commit()
                return redirect(url_for('login', username=username))

    return render_template('confirm.html')


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    return render_template('reset_password.html')


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)
