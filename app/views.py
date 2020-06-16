# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

# Python modules
import os

# Flask modules
from flask import render_template, request, url_for, redirect, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy import or_, and_

# App modules
from gamebet_website.app import app, lm
from gamebet_website.app.models.forms import LoginForm, RegisterForm, MatchCreationForm, InsertResults, GAME_CHOICES, PLATFORM_CHOICES, BET_VALUE_CHOICES, RULES_CHOICES, GAME_MODE_CHOICES, MATCH_RESULT_CHOICES
from gamebet_website.app.models.models import User, Match
from gamebet_website.app.models.user_data import user_session_data
from gamebet_website.app.util import check_results, send_email



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
@app.route('/cadastro.html', methods=['GET', 'POST'])
def register():
    # declare the Registration Form
    form = RegisterForm(request.form)
    print(form.errors)
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
                return redirect(url_for('game_room'))
            else:
                msg = "Wrong password. Please try again."
        else:
            msg = "Unknown username"

    return render_template('accounts/login.html', form=form, msg=msg)


# App main route + generic routing
@login_required
@app.route('/sala_de_jogo.html')
def game_room():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    content = None

    form = MatchCreationForm(request.form)
    msg = None

    return render_template('pages/game_room.html')
    # try:
    #     form = MatchCreationForm(request.form)
    #     return render_template('pages/game_room.html', form=form)
    #
    #
    # except:
    #
    #     return render_template('pages/error-404.html')


@login_required
@app.route('/criar_partida.html', methods=['GET', 'POST'])
def match_creation():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    content = None

    form = MatchCreationForm(request.form)
    msg = None

    if form.validate_on_submit():
        match_creator_id = current_user.id
        competitor_id = None
        game_name = dict(GAME_CHOICES).get(form.game_name.data)
        platform = dict(PLATFORM_CHOICES).get(form.platform.data)
        bet_value = dict(BET_VALUE_CHOICES).get(form.bet_value.data)
        match_creator_gametag = request.form.get('game_tag', type=str)
        competitor_gametag = None
        comments = request.form.get('comments', type=str)
        game_mode = dict(GAME_MODE_CHOICES).get(form.game_mode.data)
        rules = dict(RULES_CHOICES).get(form.rules.data)
        if rules == 'Escolha uma regra, se quiser:':
            rules = None
        match_creator_username = str(current_user.user)
        competitor_username = None
        match_creator_match_result = None
        match_creator_match_creator_goals = None
        match_creator_competitor_goals = None
        match_creator_print = None
        competitor_match_result = None
        competitor_competitor_goals = None
        competitor_match_creator_goals = None
        competitor_print = None
        match_status = 'Procurando'
        match_object = Match(match_creator_id, competitor_id, game_name, platform, bet_value, match_creator_gametag,
                             competitor_gametag, comments, rules, game_mode, match_creator_username,
                             competitor_username, match_status, match_creator_match_result,
                             match_creator_match_creator_goals, match_creator_competitor_goals, match_creator_print,
                             competitor_match_result, competitor_match_creator_goals, competitor_competitor_goals,
                             competitor_print)
        match_object.save()
        matches_list = Match.query.filter_by(id=int(match_object.id)).first()

        if matches_list:
            msg = "Partida Criada com sucesso"
            return redirect(url_for('game_room'))
        else:
            msg = 'Partida não foi criada, cheque as informações inseridas'
    print(form.errors)
    return render_template('pages/match_creation.html', form=form, msg=msg)
    # try:
    #     form = MatchCreationForm(request.form)
    #     return render_template('pages/game_room.html', form=form)
    #
    #
    # except:
    #
    #     return render_template('pages/error-404.html')


@app.route('/procurar_partida.html', methods=['GET', 'POST'])
def find_match():
    results = []
    available_matches = Match.query.filter_by(match_status='Procurando').filter(
        Match.match_creator_id != int(current_user.id))
    if request.method == 'POST':
        id = request.form['id']
        return redirect(url_for('accept_match', id=id))
    return render_template('/pages/find_match.html', available_matches=available_matches)


@login_required
@app.route('/aceitar_partida/<int:id>', methods=['GET', 'POST'])
def accept_match(id):
    match_desired = Match.query.filter_by(id=id)
    if request.method == 'POST':
        id = request.form['id']
        redirect(url_for('confirm_accept_match', id=id))
    return render_template('/pages/accept_match.html', match_desired=match_desired)


@login_required
@app.route('/partidas_em_aberto/<int:id>.html', methods=['GET', 'POST'])
def confirm_accept_match(id):
    selected_match = Match.query.filter_by(id=id).first()
    selected_match.competitor_id = current_user.id
    selected_match.competitor_username = current_user.user
    selected_match.match_status = "Em partida"
    selected_match.save()
    matches = Match.query.filter(
        or_(Match.match_creator_id == int(current_user.id), Match.competitor_id == int(current_user.id))).filter(
        or_(Match.match_status == "Em Partida", Match.match_status == "Aguardando"))
    if request.method == "POST":
        id = request.form['id']
        redirect(url_for('insert_results', id=id))
    return render_template('/pages/current_matches.html', matches=matches)


@login_required
@app.route('/partidas_em_aberto.html')
def current_matches():
    matches = Match.query.filter(
        or_(Match.match_creator_id == int(current_user.id), Match.competitor_id == int(current_user.id))).filter(
        or_(Match.match_status == "Em Partida", Match.match_status == "Aguardando"))
    if request.method == "POST":
        id = request.form['id']
        redirect(url_for('insert_results', id=id))
    return render_template('/pages/current_matches.html', matches=matches)


@login_required
@app.route('/inserir_resultados/<int:id>.html', methods=['GET', 'POST'])
def insert_results(id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    content = None

    current_match = Match.query.filter_by(id=id).first()
    form = InsertResults(request.form)

    if form.validate_on_submit():
        if int(current_user.id) == current_match.match_creator_id:
            match_creator_match_result = dict(MATCH_RESULT_CHOICES).get(form.match_result.data)
            match_creator_match_creator_goals = request.form.get('match_creator_goals', type=int)
            match_creator_competitor_goals = request.form.get('competitor_goals', type=int)
            match_creator_print = request.form.get('print', type=str)
            current_match.match_creator_match_result = match_creator_match_result
            current_match.match_creator_match_creator_goals = match_creator_match_creator_goals
            current_match.match_creator_competitor_goals = match_creator_competitor_goals
            current_match.match_creator_print = match_creator_print

        elif int(current_user.id) == current_match.competitor_id:
            competitor_match_result = dict(MATCH_RESULT_CHOICES).get(form.match_result.data)
            competitor_competitor_goals = request.form.get('match_creator_goals', type=int)
            competitor_match_creator_goals = request.form.get('competitor_goals', type=int)
            competitor_print = request.form.get('print', type=str)
            current_match.competitor_match_result = competitor_match_result
            current_match.competitor_competitor_goals = competitor_competitor_goals
            current_match.competitor_match_creator_goals = competitor_match_creator_goals
            current_match.competitor_print = competitor_print
        if current_match.match_creator_match_result is not None and current_match.match_creator_match_creator_goals \
                is not None and current_match.match_creator_competitor_goals is not None and \
                current_match.match_creator_print is not None and current_match.competitor_match_result is not None and \
                current_match.competitor_competitor_goals is not None and current_match.competitor_match_creator_goals \
                is not None and current_match.competitor_print is not None:
            current_match.match_status = "Em Análise"
            current_match.save()
            check_results(int(current_match.id))
            return redirect(url_for('insert_results'))
            print(form.errors)
            print('HEEE')

        else:
            current_match.match_status = "Aguardando"
            current_match.save()
        print(form.errors)
        print('HEEE')

        return redirect(url_for('game_room'))
    print(form.errors)
    print('HEEE')

    return render_template('pages/insert_results.html', form=form)


@login_required
@app.route('/historico_partidas.html')
def match_history():
    matches = Match.query.filter(or_(Match.match_creator_id == int(current_user.id),
                                               Match.competitor_id == int(current_user.id))).filter(
        and_(Match.match_status != "Procurando", Match.match_status != "Aguardando",
             Match.match_status != "Em Análise", Match.match_status != "Em Partida"))

    return render_template('/pages/match_history.html', matches=matches)


# Return sitemap
@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'sitemap.xml')


# Main Page
@app.route('/')
def home_page():
    return render_template('pages/index.html')


# @app.route('/<path>')
# def index(path):
#     if not current_user.is_authenticated:
#         return redirect(url_for('login'))
#
#     content = None
#     try:
#
#         # try to match the pages defined in -> pages/<input file>
#         return render_template('pages/' + path)
#
#     except:
#
#         return render_template('pages/error-404.html')
