import json
import os
import datetime
from datetime import date
import pprint

from flask import render_template, request, url_for, redirect, send_from_directory, jsonify, Response
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy import or_, and_
from brazilnum.cpf import validate_cpf

# App modules
from gamebet_website.app import app, lm
from gamebet_website.app.models.forms import LoginForm, RegisterForm, MatchCreationForm, InsertResults, GAME_CHOICES, \
    PLATFORM_CHOICES, BET_VALUE_CHOICES, RULES_CHOICES, GAME_MODE_CHOICES, MATCH_RESULT_CHOICES, GetMoneyForm, \
    match_winner_form, InsertGameTagForm, EditProfileForm, ChangeUserStatusForm, USER_STATUS_CHOICES
from gamebet_website.app.models.models import User, Match, Product, Sale, GetMoney, SiteFinance
from gamebet_website.app.util import check_results, save_image, basic_user_statistics, get_matches_data, site_finance, \
    site_seles, total_money_requests
from gamebet_website.app.mercadopago import mercadopago
from gamebet_website.app.configuration import basedir


# Return sitemap
@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'sitemap.xml')


# Main Page
@app.route('/')
def home_page():
    return render_template('pages/index.html')


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
    msg = None
    if request.method == 'GET':
        return render_template('accounts/register.html', form=form, msg=msg)
    # check if both http method is POST and form is valid on submit
    if form.validate_on_submit():
        # assign form data to variables
        user = request.form.get('username', '', type=str)
        password = request.form.get('password', '', type=str)
        email = request.form.get('email', '', type=str)
        wallet = 0
        profile_picture_url = "/static/profile_pictures/base/user.png"
        # filter User out of database through username
        user_instance = User.query.filter_by(user=user).first()
        # filter User out of database through username
        user_by_email = User.query.filter_by(email=email).first()

        if user_instance or user_by_email:
            msg = 'Error: User exists!'
        else:
            # pw_hash = bc.generate_password_hash(password)
            user_status = 'available'
            user_instance = User(user=user, email=email, password=password, wallet=wallet, user_status=user_status,
                                 profile_picture_url=profile_picture_url)
            user_instance.save()
            msg = 'Usuário criado, por favor <a href="' + url_for('login') + '">login</a>'
    else:
        msg = 'Erro ao inserir dados. Insira os dados corretos!'

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
        if user.user == 'admin':
            if user.password == 'test':
                login_user(user)
                return redirect(url_for('admin_dashboard'))
            else:
                msg = 'Senha de administrador, incorreta. Por favor, tente novamente.'
        else:
            if user:
                if user.user_status == 'excluded':
                    msg = 'Você foi expulso do sistema! Qualquer dúvida, entre em contato conosco.'
                else:
                    if user.password == password:
                        login_user(user)
                        return redirect(url_for('profile'))
                    else:
                        msg = "Senha incorreta. Por favor, tente novamente."
            else:
                msg = "Esse usuário não existe"
    return render_template('accounts/login.html', form=form, msg=msg)


# App main
@login_required
@app.route('/perfil.html', methods=['GET', 'POST'])
def profile():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    user_statistics = basic_user_statistics(current_user.id)
    actual_wallet_value = user_statistics[0]
    total_matches_played = user_statistics[1]
    total_ongoing_matches = user_statistics[2]
    # When user click on his picture, to change it, we get a POST method, that is handled bellow
    if request.method == 'POST':
        try:
            profile_picture_url = request.files['image2']
            save_directory_complete_path = basedir + "/static/profile_pictures/" + f'usuario_{current_user.user}'
            complete_path = os.path.join(save_directory_complete_path, str(current_user.user) + ".jpg")
            save_directory = "/static/profile_pictures/" + f'usuario_{current_user.user}' + "/" + str(current_user.user) \
                             + ".jpg"
            current_user.profile_picture_url = save_directory
            save_image(profile_picture_url, save_directory_complete_path, complete_path)
            current_user.save()
            return redirect(url_for('profile'))
        except Exception as err:
            print(err)
            return render_template('pages/error-404.html')
    return render_template('pages/profile.html', user_wallet=actual_wallet_value, total_matches=total_matches_played,
                           total_ongoing=total_ongoing_matches)


@login_required
@app.route('/editar_perfil.html', methods=['GET', 'POST'])
def profile_edit():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    # Converting MySQL row to dict
    current_user_data = {}
    for column in current_user.__table__.columns:
        current_user_data[column.name] = str(getattr(current_user, column.name))

    # Populating the form, with the data in dict form
    form = EditProfileForm(request.form, data=current_user_data)
    msg = None

    if form.validate_on_submit():
        # If already has data, show just only parameters. If not, show everything
        if current_user_data["first_name"]:
            phone = request.form.get('phone', '', type=str)
            xbox_gametag = request.form.get('xbox_gametag', '', type=str)
            psn_gametag = request.form.get('psn_gametag', '', type=str)
            bank_name = request.form.get('bank_name', '', type=str)
            bank_account = request.form.get('bank_account', '', type=str)
            bank_agency = request.form.get('bank_agency', '', type=str)

            current_user_db = User.query.filter_by(id=current_user.id).first()

            current_user_db.phone = phone
            current_user_db.xbox_gametag = xbox_gametag
            current_user_db.psn_gametag = psn_gametag
            current_user_db.bank_name = bank_name
            current_user_db.bank_account = bank_account
            current_user_db.bank_agency = bank_agency
            current_user_db.save()
            return redirect(url_for('profile'))
        else:
            first_name = request.form.get('first_name', '', type=str)
            last_name = request.form.get('last_name', '', type=str)
            phone = request.form.get('phone', '', type=str)
            cpf = request.form.get('cpf', '', type=str)
            rg = request.form.get('rg', '', type=str)
            birth_date = request.form.get('birth_date', '', type=str)
            xbox_gametag = request.form.get('xbox_gametag', '', type=str)
            psn_gametag = request.form.get('psn_gametag', '', type=str)
            bank_name = request.form.get('bank_name', '', type=str)
            bank_account = request.form.get('bank_account', '', type=str)
            bank_agency = request.form.get('bank_agency', '', type=str)

            # Check CPF
            if not validate_cpf(cpf):
                msg = "Informe um CPF válido"
                return render_template('pages/profile_edit.html', form=form, msg=msg)
            # Check age
            if int(datetime.datetime.now().year) - int(birth_date[6:]) < 5:
                msg = "Sua data de nascimento está incorreta"
                return render_template('pages/profile_edit.html', form=form, msg=msg)

            current_user_db = User.query.filter_by(id=current_user.id).first()
            current_user_db.first_name = first_name
            current_user_db.last_name = last_name
            current_user_db.phone = phone
            current_user_db.cpf = cpf
            current_user_db.rg = rg
            current_user_db.birth_date = birth_date
            current_user_db.xbox_gametag = xbox_gametag
            current_user_db.psn_gametag = psn_gametag
            current_user_db.bank_name = bank_name
            current_user_db.bank_account = bank_account
            current_user_db.bank_agency = bank_agency

            current_user_db.save()
            return redirect(url_for('profile'))
    return render_template('pages/profile_edit.html', form=form, msg=msg)


@login_required
@app.route('/criar_partida.html', methods=['GET', 'POST'])
def match_creation():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    form = MatchCreationForm(request.form)
    msg = None
    current_user_wallet = User.query.filter_by(id=current_user.id).first()
    if current_user.user_status == "blocked":
        return render_template('pages/match_creation.html', form=form, msg=msg)
    else:
        if int(current_user_wallet.wallet) < 5:
            msg = 'Você não possui saldo suficiente, compre mais créditos!'
        else:

            if form.validate_on_submit():
                bet_value = dict(BET_VALUE_CHOICES).get(form.bet_value.data)
                if int(current_user_wallet.wallet) < int(bet_value):
                    msg = 'Você não possui saldo suficiente, escolha uma aposta de menor valor!'
                else:
                    match_creator_id = current_user.id
                    competitor_id = None
                    game_name = dict(GAME_CHOICES).get(form.game_name.data)
                    platform = dict(PLATFORM_CHOICES).get(form.platform.data)
                    match_creator_gametag = request.form.get('game_tag', type=str)
                    if platform == 'XOne':
                        current_user_wallet.xbox_gametag = match_creator_gametag
                    else:
                        current_user_wallet.psn_gametag = match_creator_gametag
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
                    match_creation_date = date.today()
                    match_object = Match(match_creator_id, competitor_id, game_name, platform, bet_value,
                                         match_creator_gametag,
                                         competitor_gametag, comments, rules, game_mode, match_creator_username,
                                         competitor_username, match_status, match_creator_match_result,
                                         match_creator_match_creator_goals, match_creator_competitor_goals,
                                         match_creator_print,
                                         competitor_match_result, competitor_match_creator_goals,
                                         competitor_competitor_goals,
                                         competitor_print, match_creation_date)
                    match_object.save()

                    matches_list = Match.query.filter_by(id=int(match_object.id)).first()

                    if matches_list:
                        current_user_wallet.wallet = int(current_user_wallet.wallet) - int(bet_value)
                        current_user_wallet.save()
                        return redirect(url_for('profile'))
                    else:
                        msg = 'Partida não foi criada, cheque as informações inseridas'
        return render_template('pages/match_creation.html', form=form, msg=msg)
    # try:
    #     form = MatchCreationForm(request.form)
    #     return render_template('pages/profile.html', form=form)
    #
    #
    # except:
    #
    #     return render_template('pages/error-404.html')


@app.route('/procurar_partida.html', methods=['GET', 'POST'])
def find_match():
    available_matches = Match.query.filter_by(match_status='Procurando').filter(
        Match.match_creator_id != int(current_user.id))
    get_user_wallet = User.query.filter_by(id=current_user.id).first()
    if request.method == 'POST':
        id = request.form['id']
        selected_match = Match.query.filter_by(id=id).first()
        if int(get_user_wallet.wallet) < int(selected_match.bet_value):
            return redirect(url_for('product_list'))
        else:
            return redirect(url_for('accept_match', id=id))
    user_statistics = basic_user_statistics(current_user.id)
    actual_wallet_value = user_statistics[0]
    total_matches_played = user_statistics[1]
    total_ongoing_matches = user_statistics[2]

    return render_template('/pages/find_match.html', available_matches=available_matches,
                           user_wallet=actual_wallet_value, total_matches=total_matches_played,
                           total_ongoing_matches=total_ongoing_matches)


@login_required
@app.route('/aceitar_partida/<int:id>', methods=['GET', 'POST'])
def accept_match(id):
    match_desired = Match.query.filter_by(id=id)
    match_desired_2 = Match.query.filter_by(id=id).first()
    competitor = User.query.filter_by(id=current_user.id).first()
    if match_desired_2.platform == "XOne" and competitor.xbox_gametag is None:
        print('XBOX?')
        gametag = 'xbox'
    elif match_desired_2.platform == 'PS4' and competitor.psn_gametag is None:
        print('ENTROU')
        gametag = 'psn'
    else:
        gametag = 'none'
    if request.method == 'POST':
        id = request.form['id']
        redirect(url_for('current_matches', id=id))
    user_statistics = basic_user_statistics(current_user.id)
    actual_wallet_value = user_statistics[0]
    total_matches_played = user_statistics[1]
    total_ongoing_matches = user_statistics[2]

    return render_template('/pages/accept_match.html', match_desired=match_desired, gametag=gametag, match_id=id,
                           competitor_xbox=competitor.xbox_gametag, competitor_psn=competitor.psn_gametag,
                           competitor_id=competitor.id, user_wallet=actual_wallet_value,
                           total_matches=total_matches_played, total_ongoing=total_ongoing_matches)


@login_required
@app.route('/confirmar_partida/<int:id>.html', methods=['GET', 'POST'])
def confirm_accept_match(id):
    selected_match = Match.query.filter_by(id=id).first()
    competitor = User.query.filter_by(id=current_user.id).first()

    selected_match.competitor_id = current_user.id
    selected_match.competitor_username = current_user.user

    if selected_match.platform == 'XOne':
        selected_match.competitor_gametag = competitor.xbox_gametag
    else:
        selected_match.competitor_gametag = competitor.psn_gametag

    selected_match.match_status = "Em partida"
    selected_match.save()

    competitor.wallet = int(competitor.wallet) - int(selected_match.bet_value)
    competitor.save()

    matches = Match.query.filter(
        or_(Match.match_creator_id == int(current_user.id), Match.competitor_id == int(current_user.id))).filter(
        or_(Match.match_status == "Em Partida", Match.match_status == "Aguardando"))
    if request.method == "POST":
        id = request.form['id']
        redirect(url_for('insert_results', id=id))
    user_statistics = basic_user_statistics(current_user.id)
    actual_wallet_value = user_statistics[0]
    total_matches_played = user_statistics[1]
    total_ongoing_matches = user_statistics[2]

    return render_template('/pages/current_matches.html', matches=matches, user_wallet=actual_wallet_value,
                           total_matches=total_matches_played, total_ongoing=total_ongoing_matches)


#


@login_required
@app.route('/gametag.html/<int:match_id>/<int:competitor_id>/<gametag>.html', methods=['GET', 'POST'])
def insert_competitor_gametag(match_id, competitor_id, gametag):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    competitor = User.query.filter_by(id=competitor_id).first()
    selected_match = Match.query.filter_by(id=match_id).first()
    form = InsertGameTagForm(request.form)
    print('pelomenosaqui')
    if form.validate_on_submit():
        print('foi?')
        if selected_match.platform == 'XOne':
            print('talvez aqui')
            competitor.xbox_gametag = request.form.get('gametag', type=str)
            competitor.save()
            return redirect(url_for('accept_match', id=match_id))
        else:
            print('ouaqui?')
            competitor.psn_gametag = request.form.get('gametag', type=str)
            competitor.save()
            return redirect(url_for('accept_match', id=match_id))
    print('aqui?')
    print(form.errors)
    return render_template('pages/insert_competitor_gametag.html', form=form, match_id=match_id, user_id=competitor_id)


@login_required
@app.route('/partidas_em_aberto.html')
def current_matches():
    matches = Match.query.filter(
        or_(Match.match_creator_id == int(current_user.id), Match.competitor_id == int(current_user.id))).filter(
        or_(Match.match_status == "Em Partida", Match.match_status == "Aguardando"))
    if request.method == "POST":
        id = request.form['id']
        redirect(url_for('insert_results', id=id))
    user_statistics = basic_user_statistics(current_user.id)
    actual_wallet_value = user_statistics[0]
    total_matches_played = user_statistics[1]
    total_ongoing_matches = user_statistics[2]

    return render_template('/pages/current_matches.html', matches=matches, user_wallet=actual_wallet_value,
                           total_matches=total_matches_played, total_ongoing=total_ongoing_matches)


@login_required
@app.route('/inserir_resultados/<int:id>.html', methods=['GET', 'POST'])
def insert_results(id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    current_match = Match.query.filter_by(id=id).first()
    form = InsertResults(request.form)

    if form.validate_on_submit():
        if request.files:
            if int(current_user.id) == current_match.match_creator_id:
                match_creator_match_result = dict(MATCH_RESULT_CHOICES).get(form.match_result.data)
                match_creator_match_creator_goals = request.form.get('match_creator_goals', type=int)
                match_creator_competitor_goals = request.form.get('competitor_goals', type=int)
                match_creator_print = request.files['image']

                save_directory_complete_path = basedir + "/static/uploads/" + f'partida_{current_match.id}'
                complete_path = os.path.join(save_directory_complete_path,
                                             str(current_match.match_creator_gametag) + ".jpg")
                save_directory = "uploads/" + f'partida_{current_match.id}' + "/" + str(
                    current_match.match_creator_gametag) + ".jpg"

                current_match.match_creator_match_result = match_creator_match_result
                current_match.match_creator_match_creator_goals = match_creator_match_creator_goals
                current_match.match_creator_competitor_goals = match_creator_competitor_goals
                current_match.match_creator_print = save_directory
                save_image(match_creator_print, save_directory_complete_path, complete_path)

            elif int(current_user.id) == current_match.competitor_id:
                competitor_match_result = dict(MATCH_RESULT_CHOICES).get(form.match_result.data)
                competitor_competitor_goals = request.form.get('match_creator_goals', type=int)
                competitor_match_creator_goals = request.form.get('competitor_goals', type=int)
                competitor_print = request.files['image']

                save_directory_complete_path = basedir + "/static/uploads/" + f'partida_{current_match.id}'
                complete_path = os.path.join(save_directory_complete_path,
                                             str(current_match.competitor_gametag) + ".jpg")
                save_directory = "uploads/" + f'partida_{current_match.id}' + "/" + str(
                    current_match.competitor_gametag) + ".jpg"

                current_match.competitor_match_result = competitor_match_result
                current_match.competitor_competitor_goals = competitor_competitor_goals
                current_match.competitor_match_creator_goals = competitor_match_creator_goals
                current_match.competitor_print = save_directory
                save_image(competitor_print, save_directory_complete_path, complete_path)

            if current_match.match_creator_match_result is not None and current_match.match_creator_match_creator_goals \
                    is not None and current_match.match_creator_competitor_goals is not None and \
                    current_match.match_creator_print is not None and current_match.competitor_match_result is not None and \
                    current_match.competitor_competitor_goals is not None and current_match.competitor_match_creator_goals \
                    is not None and current_match.competitor_print is not None:
                current_match.match_status = "Em Análise"
                current_match.save()
                check_results(int(current_match.id))
                return redirect(url_for('match_history'))

            else:
                current_match.match_status = "Aguardando"
                current_match.save()

        return redirect(url_for('profile'))
    print(form.errors)
    return render_template('pages/insert_results.html', form=form, current_user_id=current_user.id,
                           current_match_match_creator_id=current_match.match_creator_id,
                           current_match_competitor_id=current_match.competitor_id)


@login_required
@app.route('/historico_partidas.html')
def match_history():
    matches = Match.query.filter(or_(Match.match_creator_id == int(current_user.id),
                                     Match.competitor_id == int(current_user.id))).filter(
        and_(Match.match_status != "Procurando", Match.match_status != "Aguardando",
             Match.match_status != "Em Análise", Match.match_status != "Em Partida"))
    user_statistics = basic_user_statistics(current_user.id)
    actual_wallet_value = user_statistics[0]
    total_matches_played = user_statistics[1]
    total_ongoing_matches = user_statistics[2]

    return render_template('/pages/match_history.html', matches=matches, user_wallet=actual_wallet_value,
                           total_matches=total_matches_played, total_ongoing=total_ongoing_matches)


@login_required
@app.route('/minha_carteira.html')
def user_wallet():
    shopping = Sale.query.filter_by(user_id=current_user.id)
    get_wallet = User.query.filter_by(id=current_user.id).first()
    wallet_value = get_wallet.wallet
    user_statistics = basic_user_statistics(current_user.id)
    actual_wallet_value = user_statistics[0]
    total_matches_played = user_statistics[1]
    total_ongoing_matches = user_statistics[2]

    return render_template('/pages/wallet.html', shopping=shopping, wallet=wallet_value,
                           user_wallet=actual_wallet_value, total_matches=total_matches_played,
                           total_ongoing=total_ongoing_matches)


@login_required
@app.route('/solicitar_retirada.html', methods=['GET', 'POST'])
def get_money_function():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    msg = None
    actual_user = User.query.filter_by(id=current_user.id).first()
    actual_user_wallet = int(actual_user.wallet)
    form = GetMoneyForm(request.form)

    if form.validate_on_submit():
        money_wanted = request.form.get('value_wanted', type=int)
        if actual_user_wallet > 0:
            order_date = datetime.datetime.now()
            order_status = "Em Análise"
            new_order_request = GetMoney(user_id=current_user.id, user_username=current_user.user,
                                         value_wanted=money_wanted, order_date=order_date,
                                         order_status=order_status)
            new_order_request.save()
            get_orders = GetMoney.query.filter_by(user_id=current_user.id)
            actual_user.wallet = actual_user.wallet - money_wanted
            actual_user.save()
            return redirect(url_for('get_money_history_function', get_orders=get_orders))

        else:
            print(actual_user_wallet)
            msg = "Solicitação Não Aprovada. Você não possui saldo!"
            return redirect(url_for('get_money_function', msg=msg))
    return render_template('pages/get_money.html', form=form, msg=msg)


@login_required
@app.route('/historico_solicitações_retirada.html')
def get_money_history_function():
    orders = GetMoney.query.filter_by(user_id=current_user.id)

    return render_template('/pages/get_money_history.html', orders=orders)


@login_required
@app.route('/comprar.html')
def product_list():
    products_list = Product.query.all()
    user_statistics = basic_user_statistics(current_user.id)
    actual_wallet_value = user_statistics[0]
    total_matches_played = user_statistics[1]
    total_ongoing_matches = user_statistics[2]

    return render_template('/pages/products_list.html', products_list=products_list, user_wallet=actual_wallet_value,
                           total_matches=total_matches_played, total_ongoing=total_ongoing_matches)


@app.route('/buy/<int:id_product>', methods=['GET', 'POST'])
def buy_product(id_product):
    if request.method == 'POST':
        product = Product.query.filter_by(id=id_product).first()
        current_user_id = current_user.id
        function_return = mercadopago.payment(request, product=product, current_user_id=current_user_id)
        product_url = function_return[0]
        preference_id = function_return[1]['response']['id']
        product_id = function_return[1]['response']['items'][0]['id']
        product_name = function_return[1]['response']['items'][0]['title']
        product_value = function_return[1]['response']['items'][0]['unit_price']
        user_id = current_user.id
        user_username = current_user.user
        new_sale = Sale(user_id=user_id, user_username=user_username, preference_id=preference_id,
                        product_id=product_id, product_value=product_value, product_name=product_name)
        new_sale.save()
        return redirect(product_url)


# Main Page
@app.route('/resultado_compra.html', methods=['GET'])
def mercado_pago_return():
    """
    TODO: Check what to do when the user closes the page and does not get redirect back
    :return:
    """
    return_data = request.args.to_dict()
    print(return_data)
    if return_data:
        try:
            collection_status = return_data['collection_status']
            return render_template('pages/payment_result.html', collection_status=collection_status)
        except Exception as err:
            print(err)
    else:

        return render_template('pages/perfil.html')

    return render_template('pages/payment_result.html', collection_status=collection_status)


@app.route('/test.html', methods=['GET', 'POST'])
def test():
    if request.method == "POST":

        return_data = request.args.to_dict()
        returned_data = mercadopago.get_payment_info(return_data)
        payment_info = returned_data[0]
        preference_id = returned_data[1]
        user_id = returned_data[2]

        this_sale = Sale.query.filter_by(preference_id=preference_id).first()

        print(this_sale)
        if payment_info['response']['status'] == 'approved':

            this_sale.collection_status = 'aprovado'
            this_sale.collection_id = str(payment_info['response']['id'])
            this_sale.sale_date = datetime.datetime.now()

            add_user_wallet = User.query.filter_by(id=user_id).first()
            actual_user_wallet_value = int(add_user_wallet.wallet)
            add_user_wallet.wallet = actual_user_wallet_value + int(this_sale.product_value)
            add_user_wallet.save()

        elif payment_info['response']['status'] == 'in_process':
            this_sale.collection_status = 'processando'

        elif payment_info['response']['status'] == 'rejected':
            this_sale.collection_status = 'rejeitado'

        else:
            this_sale.collection_status = payment_info['response']['status']

        this_sale.save()

    status_code = Response(status=200)

    return status_code


@app.route('/<path>')
def index(path):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    # if current_user.user == 'admin':
    #     if current_user.password == 'test':
    #         return render_template('dashboard/' + path)
    else:
        try:

            # try to match the pages defined in -> pages/<input file>
            return render_template('pages/' + path)

        except:

            return render_template('pages/error-404.html')


@login_required
@app.route('/dashboard.html', methods=['GET', 'POST'])
def admin_dashboard():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    elif not current_user.user == 'admin':
        return render_template('/perfil.html')
    else:
        # Data base queries
        opened_matches = Match.query.filter_by(match_status='Procurando')
        ongoing_matches = Match.query.filter_by(match_status='Em partida')
        on_analyzes = Match.query.filter_by(match_status='Em Análise')
        finalized_matches = Match.query.filter(and_(Match.match_status != "Procurando",
                                                    Match.match_status != "Aguardando",
                                                    Match.match_status != "Em Análise",
                                                    Match.match_status != "Em Partida"))
        all_matches = Match.query.all()
        users_list = User.query.filter(User.user != "Admin").all()
        finance_data = SiteFinance.query.all()
        approved_sales = Sale.query.filter_by(collection_status='approved').all()
        approved_money_requests = GetMoney.query.filter_by(order_status='Aprovado').all()


        # Call get data functions
        match_creation_chart = get_matches_data(all_matches)
        opened_matches_chart = get_matches_data(opened_matches)
        ongoing_matches_chart = get_matches_data(ongoing_matches)
        finalized_matches_chart = get_matches_data(finalized_matches)

        total_commission = site_finance(finance_data)

        total_sales = site_seles(approved_sales)

        money_requests = total_money_requests(approved_money_requests)

        if request.method == "POST":
            id = request.form['id']
            redirect(url_for('match_winner', id=id))

        return render_template('dashboard/dashboard.html', opened_matches=opened_matches, users_list=users_list,
                               ongoing_matches=ongoing_matches, on_analyzes=on_analyzes, all_matches=all_matches,
                               finalized_matches=finalized_matches,
                               match_creation_labels=match_creation_chart[0],
                               match_creation_results=match_creation_chart[1],
                               ongoing_matches_labels=ongoing_matches_chart[0],
                               ongoing_matches_results=ongoing_matches_chart[1],
                               opened_matches_labels=opened_matches_chart[0],
                               opened_matches_results=opened_matches_chart[1],
                               finalized_matches_labels=finalized_matches_chart[0],
                               finalized_matches_results=finalized_matches_chart[1],
                               total_commission=total_commission, total_sales=total_sales,
                               total_money_requests=money_requests)


@app.route('/admin_dashboard_finance.html')
def admin_dashboard_finance():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if current_user.user == 'admin':
        if current_user.password == 'test':
            return render_template('dashboard/dashboard_finance.html')
    else:
        return render_template('pages/error-404.html')


@login_required
@app.route('/dashboard_finance1.html', methods=['GET', 'POST'])
def dashboard_finance():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    elif not current_user.user == 'admin':
        return render_template('/perfil.html')

    return render_template('dashboard/dashboard_finance.html')


@login_required
@app.route('/ganhador_partida/<int:id>.html', methods=['GET', 'POST'])
def match_winner(id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    elif not current_user.user == 'admin':
        return render_template('/perfil.html')
    current_match = Match.query.filter_by(id=id).first()

    match_creator = current_match.match_creator_gametag
    competitor = current_match.competitor_gametag
    match_creator_print_path = current_match.match_creator_print
    competitor_print_path = current_match.competitor_print
    current_match_users = [match_creator, competitor]
    form_function_return = match_winner_form(request.form, current_match_users)
    form = form_function_return[0]
    match_winner_choices = form_function_return[1]

    if request.method == 'POST':

        if form.validate_on_submit():
            match_winner_analyzed = dict(match_winner_choices).get(form.match_winner.data)
            current_match.match_status = match_winner_analyzed

            if current_match.platform == 'XOne':
                user_winner = User.query.filter_by(xbox_gametag=match_winner_analyzed).first()

                site_commission = int(current_match.bet_value * 2) * 0.1

                user_winner.wallet = user_winner.wallet + current_match.bet_value * 2 - site_commission
                user_winner.save()

                new_commission = SiteFinance(match_id=current_match.id, match_bet_value=current_match.bet_value,
                                             match_total_value=current_match.bet_value * 2,
                                             commission_value=site_commission,
                                             match_winner_user=current_match.match_creator_username)
                new_commission.save()

            elif current_match.platform == 'PS4':

                user_winner = User.query.filter_by(psn_gametag=match_winner_analyzed).first()

                site_commission = int(current_match.bet_value * 2) * 0.1

                user_winner.wallet = user_winner.wallet + 2 * current_match.bet_value - site_commission
                user_winner.save()

                new_commission = SiteFinance(match_id=current_match.id, match_bet_value=current_match.bet_value,
                                             match_total_value=current_match.bet_value * 2,
                                             commission_value=site_commission,
                                             match_winner_user=current_match.match_creator_username)
                new_commission.save()

            current_match.save()
            return redirect(url_for('admin_dashboard'))
        return render_template('dashboard/match_winner.html', form=form, id=id, match_creator_gametag=match_creator,
                               competitor_gametag=competitor, match_creator_print_path=match_creator_print_path,
                               competitor_print_path=competitor_print_path)

    return url_for('match_winner', form=form, id=id, match_creator_gametag=match_creator, competitor_gametag=competitor)


@login_required
@app.route('/mudar_status_usuario/<int:id>.html', methods=['GET', 'POST'])
def change_user_status(id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    elif not current_user.user == 'admin':
        return render_template('/perfil.html')
    user = User.query.filter_by(id=id).first()
    form = ChangeUserStatusForm(request.form)
    if form.validate_on_submit():
        print('entrou?')
        new_user_status = dict(USER_STATUS_CHOICES).get(form.user_status.data)

        if new_user_status == 'Bloquear':
            user.user_status = 'blocked'
            print(user.user_status)
        elif new_user_status == 'Excluir':
            user.user_status = 'excluded'
            print(user.user_status)

        else:
            user.user_status = 'available'
            print(user.user_status)

        user.save()
        return redirect(url_for('admin_dashboard'))
    print(form.errors)
    return render_template('dashboard/change_user_status.html', form=form, id=id, username=user.user)


@login_required
@app.route('/editar_partida_aberta/<int:id>.html', methods=['GET', 'POST'])
def edit_matches(id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    elif not current_user.user == 'admin':
        return render_template('/perfil.html')

    current_match = Match.query.filter_by(id=id).first()

    current_match_data = {}
    for column in current_match.__table__.columns:
        current_match_data[column.name] = str(getattr(current_match, column.name))

    form = MatchCreationForm(request.form, data=current_match_data)
    msg = None
    if form.validate_on_submit():
        # phone = request.form.get('phone', '', type=str)
        # xbox_gametag = request.form.get('xbox_gametag', '', type=str)
        # psn_gametag = request.form.get('psn_gametag', '', type=str)
        # bank_name = request.form.get('bank_name', '', type=str)
        # bank_account = request.form.get('bank_account', '', type=str)
        # bank_agency = request.form.get('bank_agency', '', type=str)
        #
        # current_user_db = User.query.filter_by(id=current_user.id).first()
        #
        # current_user_db.phone = phone
        # current_user_db.xbox_gametag = xbox_gametag
        # current_user_db.psn_gametag = psn_gametag
        # current_user_db.bank_name = bank_name
        # current_user_db.bank_account = bank_account
        # current_user_db.bank_agency = bank_agency
        #
        # current_user_db.save()

        return redirect(url_for('profile'))

    print(form.errors)
    return render_template('dashboard/edit_matches.html', form=form, msg=msg)
