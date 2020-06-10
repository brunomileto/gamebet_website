# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

# Python modules
import os

# Flask modules
from flask import render_template, request, url_for, redirect, send_from_directory
from flask_login import login_user, logout_user, current_user

# App modules
from gamebet_website.app import app, lm
from gamebet_website.app.models.forms import LoginForm, RegisterForm, MatchesForm
from gamebet_website.app.models.models import User, Match
from gamebet_website.app.models.user_data import user_session_data
from gamebet_website.app.tebles import Results


# provide login manager with load_user callback
@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Logout username
@app.route('/logout.html')
def logout():
    logout_user()
    return redirect(url_for('home_page'))


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
        name = ""
        last_name = ""
        phone = None
        cpf = None
        birth_date = None
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
                user_session_data(current_user.id)
                return redirect(url_for('users_main_page'))
            else:
                msg = "Wrong password. Please try again."
        else:
            msg = "Unknown username"

    return render_template('accounts/login.html', form=form, msg=msg)


# Main Page
@app.route('/')
def home_page():
    return render_template('pages/index.html')


# App main route + generic routing
@app.route('/sala_jogos.html')
def users_main_page():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    content = None

    form = MatchesForm(request.form)
    msg = None

    return render_template('pages/game_room.html')
    # try:
    #     form = MatchesForm(request.form)
    #     return render_template('pages/game_room.html', form=form)
    #
    #
    # except:
    #
    #     return render_template('pages/error-404.html')


@app.route('/match_creation.html', methods=['GET', 'POST'])
def match_creation():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    content = None

    form = MatchesForm(request.form)
    msg = None

    if form.validate_on_submit():
        print('sssssssssssss')
        match_creator_id = current_user.id
        competitor_id = None
        game_name = request.form.get('game_name', type=str)
        platform = request.form.get('platform', type=str)
        bet_value = request.form.get('bet_value', type=int)
        match_creator_gametag = request.form.get('game_tag', type=str)
        competitor_gametag = None
        rules_comments = request.form.get('rules_comments', type=str)
        game_mode = request.form.get('game_mode', type=str)
        match_creator_username = str(current_user.user)
        competitor_username = None
        match_status = 'Aguardando'

        match_object = Match(match_creator_id, competitor_id, game_name, platform, bet_value, match_creator_gametag,
                             competitor_gametag, rules_comments, rules_comments, game_mode, match_creator_username,
                             competitor_username, match_status)
        match_object.save()
        matches_list = Match.query.filter_by(id=int(match_object.id)).first()
        print(matches_list)
        if matches_list:
            msg = "Partida Criada com sucesso"
            return redirect(url_for('users_main_page'))
        else:
            msg = 'Partida não foi criada, cheque as informações inseridas'
    print(form.errors)
    return render_template('pages/match_creation.html', form=form, msg=msg)
    # try:
    #     form = MatchesForm(request.form)
    #     return render_template('pages/game_room.html', form=form)
    #
    #
    # except:
    #
    #     return render_template('pages/error-404.html')


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


@app.route('/results')
def search_results():
    results = []
    available_matches = Match.query.filter_by(match_status='Aguardando')
    table = Results(available_matches)
    table.border = True
    return render_template('/pages/results.html', table=table)


# Return sitemap
@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'sitemap.xml')
