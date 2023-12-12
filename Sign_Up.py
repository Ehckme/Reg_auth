import flask
import requests

"""-------------    import working modules for Flask    --------------"""
from flask import Flask
from flask import render_template, url_for, session
from flask import request, redirect, flash

"""------------ import modules for sqlalchemy and flask-sqlaclhemy  ------------"""
from sqlalchemy import String, Integer, CHAR
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Session, sessionmaker
from flask_sqlalchemy import SQLAlchemy

"""----------   import modules for argon2-cffi password hashing -------"""
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

"""-----------  import modules for regular expressions  -----------"""
import re

"""------------ import modules for DNS and dns-resolver -------------"""
import dns.resolver

# import flask login
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user


# create an inheritance class from DeclarativeBase
class Base(DeclarativeBase):
    pass


sql_session = sessionmaker()

# instantiate database from sqlalchemy Base
db = SQLAlchemy(model_class=Base)

SESSION_TYPE = 'sqlalchemy'
app = Flask(__name__)

""" --------    Create a connection to the database using mysql and + pymysql   -----------"""

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/New_User_Database'

"""-----------  config secrete key  ---------"""

app.config['SECRET_KEY'] = 'TooTopSecrete'

engine = create_engine('mysql+pymysql://root:root@localhost/New_User_Database')
sess = Session(engine)

# initialize database app
db.init_app(app)

"""--------------   create the application object   ----------------"""

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

""" -------------   Load user from login_manager with their user id.    ---------------- 
"""


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Users, int(user_id))


""" --------------  Create a User Model, which is a table for Users with flask-sqlalchemy   ----------- 
"""


class Users(db.Model, UserMixin):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(30))
    password: Mapped[str] = mapped_column(CHAR(200))
    confirmed: Mapped[bool] = mapped_column(nullable=False, default=False)
    otp: Mapped[int] = mapped_column(nullable=True)


with app.app_context():
    db.create_all()

""" --------------- view route for home page.   -----------------  
"""


@app.route('/', methods=['GET'])
@login_required
def home():
    return render_template('dashboard.html')


""" -----------------   view route for login page.  --------------  
"""


@app.route('/login', methods=['GET', 'POST'])
def login():

    # Get user email and password from the user input from the form
    mail = request.form.get('email', False)
    password = request.form.get('password', False)

    if request.method == 'POST':

        # check email with regular expressions and display flash message
        if re.match(r"\S[^@]+\S+@[^@]+\S+[a-zA-Z]+\S+\.[^@]", mail):
            pass
        else:
            flash('invalid email')

        # Validate the database email with the user input email
        valid_user_email = Users.query.filter_by(email=mail).first()

        if valid_user_email:

            # instantiate PasswordHasher from argon2-cffi
            ph = PasswordHasher()
            hash = valid_user_email.password

            # Use the try block to catch the exception
            try:

                # Verify the hash in database with the user input password
                if ph.verify(hash, password):

                    if ph.check_needs_rehash(hash):
                        valid_user_email.password(valid_user_email, ph.hash(password))

                    # Check if user has confirmed email in database
                    is_confirmed = valid_user_email.confirmed

                    if is_confirmed == True:

                        # Login the user
                        login_user(valid_user_email)

                        # Display flash message
                        flash(f'You are logged in {valid_user_email.username}')
                        print(is_confirmed)
                        return redirect(url_for('dashboard', user_username=valid_user_email.username))
                    else:
                        flash('To start using our services, please confirm your email account with us! ')
                        return redirect(url_for('confirm'))
            except VerifyMismatchError:

                # Display a flash message
                flash('please enter correct password')
                return redirect(url_for('login'))
        else:

            # Display a flash message
            flash('please enter correct email')

    return render_template('login.html')


""" ------------    view route for dashboard page.  -----------------  
"""


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')


"""--------     create OTP code to use for confirming the user
    by importing and using the random module    ------------------

"""
import random


def random_otp():
    otp = ''.join([str(random.randint(0000, 9999)) for i in range(1)])
    return otp


OTP = random_otp()

""" -------------------     view route for sign_up page     -------------------------- 
"""


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():

    # Get user email, username and password from the user input from the form
    user_email = request.form.get('email', False)
    user_name = request.form.get('username', False)
    pass_word = request.form.get('password', False)

    # create a session containing the user's username
    session['username'] = request.form.get('username', False)

    if request.method == 'POST':

        # Use regular expressions to check email
        if re.match(r"\S[^@]+\S+@[^@]+\S+[a-zA-Z]+\S+\.[^@]", user_email):

            # instantiate PasswordHasher from argon2-cffi
            ph = PasswordHasher()
            hash = ph.hash(pass_word)

            # Get user input details from the form to add them to database
            new_user = Users(
                username=request.form.get('username', False),
                email=request.form.get('email', False),
                password=hash,
                otp=OTP,
            )
        else:
            flash('invalid email format')
            print('Invalid email Format')
            return redirect(url_for('sign_up'))

        # Check if the email entered is in the database
        email_in_database = Users.query.filter_by(email=user_email).first()

        if email_in_database:
            # Display flash message
            flash('Email already exists. ')
            print('Email already exists')
            return redirect(url_for('sign_up'))
        else:

            """-----------  Split domain from user_email input  -------------"""
            domain = user_email.split('@')[1]

            """---------    Check the existence of DNS domain
                and catch  the error with try-except method -----------------. 
            """
            try:
                dns_address = dns.resolver.resolve(f'{domain}', 'A')
                for dns_a in dns_address:
                    print('A record : ', dns_a.to_text())
                    db.session.add(new_user)
                    db.session.commit()

                    ###############################################################
                    ### The following is a block for sending email with smtplib ###
                    ###############################################################

                    """------------     import smtplib modules    ------------"""

                    import smtplib
                    from email.mime.multipart import MIMEMultipart
                    from email.mime.text import MIMEText

                    message = MIMEMultipart()

                    """ -------------   Send SMTP message to user_email input   ------------ """

                    message['To'] = user_email
                    message['From'] = 'ehckmedev@gmail.com'
                    message['Subject'] = 'CONFIRM'

                    title = '<b> CONFIRM OTP-CODE </b>'

                    message_text = MIMEText(
                        f''' Hello {user_name}, your OTP-Code is: {OTP} ''', 'html'
                    )
                    message.attach(message_text)

                    """ ----------- Sender infor email and app password ---------- """
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
                return redirect(url_for('sign_up', ))

    return render_template('sign_up.html', )


""" --------------  view route for confirm page ------------------  
"""


@app.route('/confirm', methods=['GET', 'POST'])
def confirm():
    if request.method == 'POST':
        user_input_otp = request.form.get('otp', False)

        if user_input_otp != OTP:
            flash('Invalid OTP code')
            print('Invalid OTP code')
            print('Your OTP is: ', OTP)
        elif user_input_otp == OTP:
            print('Your OTP is: ', OTP)

            if 'username' in session:
                username = session['username']
                is_username_in_db = Users.query.filter_by(username=username).first()
                is_username_in_db.confirmed = True
                is_username_in_db.otp = OTP
                session['otp'] = OTP
                db.session.commit()
                flash('Account successfully confirmed, \n please login with your credentials.')
                return redirect(url_for('login', username=username))

    return render_template('confirm.html')


""" --------------  view route for account_recovery page    -----------------  
"""


@app.route('/account_recovery', methods=['GET', 'POST'])
def account_recovery():
    email_to_recover = request.form.get('email', False)
    check_recovery_email = Users.query.filter_by(email=email_to_recover).first()

    # create a session containing the user's username from email
    session['user_from_email'] = check_recovery_email.username

    if request.method == 'POST':
        if check_recovery_email:

            """ --------------- Split domain from user_email input  ----------------"""
            domain = email_to_recover.split('@')[1]

            """ --------------- Check the existence of DNS domain
                and catch  the error with try-except method.    ---------------------- 
            """
            try:
                dns_address = dns.resolver.resolve(f'{domain}', 'A')
                for dns_a in dns_address:
                    print('A record : ', dns_a.to_text())

                    ###############################################################
                    ### The following is a block for sending email with smtplib ###
                    ###############################################################

                    """------------     import smtplib modules    ------------"""

                    import smtplib
                    from email.mime.multipart import MIMEMultipart
                    from email.mime.text import MIMEText

                    message = MIMEMultipart()
                    """ -------------   Send SMTP message to user_email input   -------------- """
                    message['To'] = email_to_recover
                    message['From'] = 'ehckmedev@gmail.com'
                    message['Subject'] = 'CONFIRM'

                    # title = '<b> CONFIRM OTP-CODE </b>'

                    message_text = MIMEText(
                        f''' Hello {check_recovery_email.username}, your OTP-Code is: {OTP}  ''', 'html'
                    )
                    message.attach(message_text)

                    """ -------------   Sender info email and app password  ------------ """
                    sender_email = 'ehckmedev@gmail.com'
                    app_password = 'iyjf yndm yoxb qysh'

                    server = smtplib.SMTP('smtp.gmail.com:587')
                    server.ehlo('Gmail')
                    server.starttls()
                    server.login(sender_email, app_password)

                    fromaddr = sender_email
                    toaddr = email_to_recover
                    server.sendmail(fromaddr, toaddr, message.as_string())
                    server.quit()

                    return redirect(url_for('otp_reset', ))

            except dns.exception.DNSException:
                flash('Invalid email')
                print('Invalid Email')

            print(email_to_recover)

            return redirect(url_for('otp_reset'))
        else:
            flash('Email does not exist')
            print('Email does not exist')
    return render_template('account_recovery.html')


""" --------------- view route for otp_reset page   ------------------  
"""


@app.route('/otp_reset', methods=['GET', 'POST'])
def otp_reset():
    if request.method == 'POST':
        user_input_otp = request.form.get('otp', False)
        if user_input_otp != OTP:

            print('Invalid OTP code')
            flash('Invalid OTP code')
        elif user_input_otp == OTP:
            print('Your OTP is: ', OTP)
            flash('Email confirmed.')
            return redirect(url_for('reset_password', ))

    flash('To varify it is you?! ')
    return render_template('otp_reset.html')


""" ---------------     view route for reset_password page      ---------------  
"""


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':

        # Get user's new password, and confirm password from the user input from the form
        new_password = request.form.get('new_password', False)
        confirm_new_password = request.form.get('confirm_new_password', False)

        if new_password == confirm_new_password:
            if 'user_from_email' in session:
                ph = PasswordHasher()
                hash = ph.hash(confirm_new_password)
                user_from_email = session['user_from_email']
                print(user_from_email)
                user_reset_pw = Users.query.filter_by(username=user_from_email).first()
                user_reset_pw.password = hash
                db.session.commit()
                flash('Password  changed successfully. ')
            return redirect(url_for('login', email=user_from_email))
        else:
            print('Password do not match. Enter matching passwords')
            flash('Password do not match. Enter matching passwords')

    return render_template('reset_password.html')


""" ---------------     view route for logout page      ----------------  
"""


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)
