# auth.py
from werkzeug.security import generate_password_hash
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required,current_user
from .models import User
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/')
def index():     
   return redirect(url_for('auth.login'))

@auth.route('/login')
def login():
    if not current_user.is_authenticated:
        return render_template('login.html')
    if(current_user.get_urole()=='Admin'):
        return redirect(url_for('main.profile'))
    elif(current_user.get_urole()=='Vendor'):
        return redirect(url_for('vendor.index'))
    

@auth.route('/error')
def error():
   return ("Error You dont have permission")
@auth.route('/login', methods=['POST'])
def login_post():
    uid = request.form.get('vid')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(user_id=uid).first()

    # check if user actually exists
    # take the user supplied password, hash it, and compare it to the hashed password in database
    if not user or not check_password_hash(user.password, password): 
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login')) # if user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    session['uname'] = user.user_id
    if(user.role=='Admin'):
        return redirect(url_for('main.profile'))
    elif(user.role=='Vendor'):        
        return redirect(url_for('vendor.index'))
    

#@auth.route('/signup')
#def signup():
#    return render_template('signup.html')
#
#@auth.route('/signup', methods=['POST'])
#def signup_post():
#
#    uid = request.form.get('vid')
#    name = request.form.get('name')
#    password = request.form.get('password')
#
#    user = User.query.filter_by(user_id=uid).first() # if this returns a user, then the email already exists in database
#
#    if user: # if a user is found, we want to redirect back to signup page so user can try again  
#        flash('Vendor ID already exists')
#        return redirect(url_for('auth.signup'))
#
#    # create new user with the form data. Hash the password so plaintext version isn't saved.
#    new_user = User(user_id=uid, name=name, password=generate_password_hash(password, method='sha256'),role="admin")
#
#    # add the new user to the database
#    db.session.add(new_user)
#    db.session.commit()
#
#    return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
