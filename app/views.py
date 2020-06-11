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
from sqlalchemy import or_, and_

# App modules
from gamebet_website.app import app, lm
from gamebet_website.app.models.forms import LoginForm, RegisterForm, MatchCreationForm, InsertResults
from gamebet_website.app.models.models import User, Match
from gamebet_website.app.models.user_data import user_session_data
from gamebet_website.app.tables import SearchMatchTable, AcceptMatch, ShowCurrentAcceptedMaches, ShowHistoric
from gamebet_website.app.util import check_results


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


# App main route + generic routing
@app.route('/sala_jogos.html')
def users_main_page():
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
        game_name = request.form.get('game_name', type=str)
        platform = request.form.get('platform', type=str)
        bet_value = request.form.get('bet_value', type=int)
        match_creator_gametag = request.form.get('game_tag', type=str)
        competitor_gametag = None
        rules_comments = request.form.get('rules_comments', type=str)
        game_mode = request.form.get('game_mode', type=str)
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
        match_status = 'Aguardando'
        match_object = Match(match_creator_id, competitor_id, game_name, platform, bet_value, match_creator_gametag,
                             competitor_gametag, rules_comments, rules_comments, game_mode, match_creator_username,
                             competitor_username, match_status, match_creator_match_result,
                             match_creator_match_creator_goals, match_creator_competitor_goals, match_creator_print,
                             competitor_match_result, competitor_match_creator_goals, competitor_competitor_goals,
                             competitor_print)
        match_object.save()
        matches_list = Match.query.filter_by(id=int(match_object.id)).first()
        if matches_list:
            msg = "Partida Criada com sucesso"
            return redirect(url_for('users_main_page'))
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


@app.route('/partidas_disponiveis')
def search_matches():
    results = []
    available_matches = Match.query.filter_by(match_status='Aguardando').filter(
        Match.match_creator_id != int(current_user.id))
    table = SearchMatchTable(available_matches)
    table.border = True
    return render_template('/pages/search_matches.html', table=table)


@app.route('/aceitar_partida/<int:id>', methods=['GET', 'POST'])
def accept_match(id):
    new_selected_match = Match.query.filter_by(id=id)
    table = AcceptMatch(new_selected_match)
    table.border = True
    return render_template('/pages/accept_match.html', table=table)


@app.route('/accept_match/<int:id>', methods=['GET', 'POST'])
def confirm_accepted_match(id):
    selected_match = Match.query.filter_by(id=id).first()
    selected_match.competitor_id = current_user.id
    selected_match.competitor_username = current_user.user
    selected_match.match_status = "Em partida"
    selected_match.save()
    new_selected_match = Match.query.filter_by(id=id)
    table = AcceptMatch(new_selected_match)
    table.border = True
    return render_template('/pages/accept_match.html', table=table)


@app.route('/partidas_em_aberto')
def current_accepted_matches():
    current_match = Match.query.filter(
        or_(Match.match_creator_id == int(current_user.id), Match.competitor_id == int(current_user.id))).filter(
        or_(Match.match_status == "Em Partida", Match.match_status == "Aguardando"))
    table = ShowCurrentAcceptedMaches(current_match)
    table.border = True
    return render_template('/pages/current_accepted_matches.html', table=table)


@app.route('/inserir_resultados/<int:id>', methods=['GET', 'POST'])
def insert_results(id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    content = None

    current_match = Match.query.filter_by(id=id).first()
    form = InsertResults(request.form)

    if form.validate_on_submit():
        if int(current_user.id) == current_match.match_creator_id:
            match_creator_match_result = request.form.get('match_result', type=str)
            match_creator_match_creator_goals = request.form.get('match_creator_goals', type=int)
            match_creator_competitor_goals = request.form.get('competitor_goals', type=int)
            match_creator_print = request.form.get('print', type=str)
            current_match.match_creator_match_result = match_creator_match_result
            current_match.match_creator_match_creator_goals = match_creator_match_creator_goals
            current_match.match_creator_competitor_goals = match_creator_competitor_goals
            current_match.match_creator_print = match_creator_print

        elif int(current_user.id) == current_match.competitor_id:
            competitor_match_result = request.form.get('match_result', type=str)
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
            return render_template(url_for('users_main_page'))
        else:
            current_match.match_status = "Aguardando"
            current_match.save()
        return redirect(url_for('users_main_page'))
    return render_template('pages/insert_results.html', form=form)


# @app.route('/insert_results/<int:id>', methods=['GET', 'POST'])
# def show_match_results(id):
#     current_match = Match.query.filter_by(id=id).first()
#     match_id = id
#     game_name = current_match.game_name
#     if int(current_user.id) == current_match.match_creator_id:
#         match_creator_match_result = request.form.get('match_result', type=str)
#         match_creator_match_creator_goals = request.form.get('match_creator_goals', type=str)
#         match_creator_competitor_goals = request.form.get('competitor_goals', type=str)
#         match_creator_print = request.form.get('print', type=str)
#     elif int(current_user.id) == current_match.competitor_id:
#         competitor_match_result = request.form.get('match_result', type=str)
#         competitor_competitor_goals = request.form.get('match_creator_goals', type=int)
#         competitor_match_creator_goals = request.form.get('competitor_goals', type=int)
#         competitor_print = request.form.get('print', type=str)
#
#     bet_value = current_match.bet_value
#     match_creator_gametag = current_match.match_creator_gametag
#     competitor_gametag = current_match.competitor_gametag
#     comment = current_match.comment
#     game_rules = current_match.game_rules
#     match_creator_username = current_match.match_creator_username
#     competitor_username = current_match.competitor_username
#     match_status = current_match.match_status
#
#     match_results_object = MatchChecker(match_id, game_name, bet_value, match_creator_gametag, competitor_gametag,
#                                         comment, game_rules, match_creator_username, competitor_username, match_status,
#                                         match_creator_match_result, match_creator_match_creator_goals,
#                                         match_creator_competitor_goals, match_creator_print, competitor_match_result,
#                                         competitor_match_creator_goals, competitor_competitor_goals, competitor_print)
#     match_results_object.save()
#     current_match_checker = MatchChecker.query.filter_by(match_id=id)
#     insert_results_table_object = InsertResults(current_match_checker).do_the_table(int(current_match.match_creator_id),
#                                                                                     int(current_match.competitor_id))
#
#     insert_results_table_object.border = True
#     return render_template('/pages/insert_results.html', table=insert_results_table_object)


@app.route('/historic')
def user_historic():
    available_matches = Match.query.filter(or_(Match.match_creator_id == int(current_user.id),
                                               Match.competitor_id == int(current_user.id))).filter(
        and_(Match.match_status != "Aguardando", Match.match_status != "Aguardando",
            Match.match_status != "Em Análise", Match.match_status != "Em Partida"))
    table = ShowHistoric(available_matches)
    table.border = True
    return render_template('/pages/user_historic.html', table=table)


# Return sitemap
@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'sitemap.xml')


# Main Page
@app.route('/')
def home_page():
    return render_template('pages/index.html')


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
