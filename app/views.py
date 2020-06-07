# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

# Python modules
import os

# App modules
from app import app, lm
from app.forms import LoginForm, RegisterForm
from app.models import User
# Flask modules
from flask import render_template, request, url_for, redirect, send_from_directory
from flask_login import login_user, logout_user, current_user


# provide login manager with load_user callback
@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Logout username
@app.route('/logout.html')
def logout():
    logout_user()
    return redirect(url_for('index'))


# Register a new username
@app.route('/register.html', methods=['GET', 'POST'])
def register():
    # declare the Registration Form
    form = RegisterForm(request.form)
    msg = None
    if request.method == 'GET':
        return render_template('accounts/register.html', form=form, msg=msg)

    # check if both http method is POST and form is valid on submit
    if form.validate_on_submit():
        # assign form data to variables
        user = request.form.get('username', '', type=str)
        senha = request.form.get('password', '', type=str)
        email = request.form.get('email', '', type=str)
        name = request.form.get('first_name', '', type=str)
        last_name = request.form.get('last_name', '', type=str)
        phone = request.form.get('phone', '', type=str)
        cpf = request.form.get('cpf', '', type=str)
        birth_date = request.form.get('birth_date', '', type=str)
        # filter User out of database through username
        user_instance = User.query.filter_by(user=user).first()
        # filter User out of database through username
        user_by_email = User.query.filter_by(email=email).first()
        if user_instance or user_by_email:
            msg = 'Error: User exists!'

        else:

            pw_hash = senha  # bc.generate_password_hash(password)

            user_instance = User(user, email, pw_hash, name, last_name, phone, cpf, birth_date)

            user_instance.save()

            msg = 'User created, please <a href="' + url_for('login') + '">login</a>'

    else:
        msg = 'Input error'

    return render_template('accounts/register.html', form=form, msg=msg)


# Authenticate username
@app.route('/login.html', methods=['GET', 'POST'])
def login():
    # Declare the login form
    form = LoginForm(request.form)

    # Flask message injected into the page, in case of any errors
    msg = None

    # check if both http method is POST and form is valid on submit
    if form.validate_on_submit():

        # assign form data to variables
        username = request.form.get('username', '', type=str)
        password = request.form.get('password', '', type=str)

        # filter User out of database through username
        user = User.query.filter_by(user=username).first()

        if user:

            # if bc.check_password_hash(username.password, password):
            if user.password == password:
                login_user(user)
                return redirect(url_for('index'))
            else:
                msg = "Wrong password. Please try again."
        else:
            msg = "Unknown username"

    return render_template('accounts/login.html', form=form, msg=msg)


# App main route + generic routing
@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path>')
def index(path):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    content = None

    try:

        # try to match the pages defined in -> pages/<input file>
        return render_template('pages/' + path)

    except:

        return render_template('pages/error-404.html')


# Return sitemap
@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'sitemap.xml')
