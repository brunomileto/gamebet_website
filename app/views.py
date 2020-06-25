import json
import os
import datetime
import pprint

from flask import render_template, request, url_for, redirect, send_from_directory, jsonify, Response
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy import or_, and_

# App modules
from gamebet_website.app import app, lm
from gamebet_website.app.models.forms import LoginForm, RegisterForm, MatchCreationForm, InsertResults, GAME_CHOICES, \
    PLATFORM_CHOICES, BET_VALUE_CHOICES, RULES_CHOICES, GAME_MODE_CHOICES, MATCH_RESULT_CHOICES, GetMoneyForm, \
    match_winner_form
from gamebet_website.app.models.models import User, Match, Product, Sale, GetMoney
from gamebet_website.app.util import check_results
from gamebet_website.app.mercadopago import mercadopago


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
        wallet = 0
        # filter User out of database through username
        user_instance = User.query.filter_by(user=user).first()
        # filter User out of database through username
        user_by_email = User.query.filter_by(email=email).first()
        if user_instance or user_by_email:
            msg = 'Error: User exists!'

        else:

            pw_hash = senha  # bc.generate_password_hash(password)

            user_instance = User(user, email, pw_hash, name, last_name, phone, cpf, birth_date, wallet)
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
        print(user)
        if user.user == 'admin':
            if user.password == 'test':
                login_user(user)
                return redirect(url_for('admin_dashboard'))
            else:
                msg = 'Senha de administrador, incorreta. Por favor, tente novamente.'
        else:
            if user:
                if user.password == password:
                    login_user(user)
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

    return render_template('pages/game_room.html')
    # try:
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
    form = MatchCreationForm(request.form)
    msg = None
    current_user_wallet = User.query.filter_by(id=current_user.id).first()

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
                match_object = Match(match_creator_id, competitor_id, game_name, platform, bet_value,
                                     match_creator_gametag,
                                     competitor_gametag, comments, rules, game_mode, match_creator_username,
                                     competitor_username, match_status, match_creator_match_result,
                                     match_creator_match_creator_goals, match_creator_competitor_goals,
                                     match_creator_print,
                                     competitor_match_result, competitor_match_creator_goals,
                                     competitor_competitor_goals,
                                     competitor_print)
                match_object.save()
                matches_list = Match.query.filter_by(id=int(match_object.id)).first()

                if matches_list:
                    current_user_wallet.wallet = int(current_user_wallet.wallet) - int(bet_value)
                    current_user_wallet.save()
                    return redirect(url_for('game_room'))
                else:
                    msg = 'Partida não foi criada, cheque as informações inseridas'
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
    competitor_wallet_update = User.query.filter_by(id=current_user.id).first()
    competitor_wallet_update.wallet = int(competitor_wallet_update.wallet) - int(selected_match.bet_value)
    competitor_wallet_update.save()
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
            return redirect(url_for('match_history'))


        else:
            current_match.match_status = "Aguardando"
            current_match.save()

        return redirect(url_for('game_room'))

    return render_template('pages/insert_results.html', form=form)


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
        if actual_user_wallet >= 40:
            if actual_user_wallet > money_wanted > 40:
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
                msg = "Solicitação Não Aprovada. Você precisa ficar com ao menos R$50,00 em sua conta!"
                return redirect(url_for('get_money_function', msg=msg))

        else:
            print(actual_user_wallet)
            msg = "Solicitação Não Aprovada. Você não possui menos de R$50,00 em sua conta!"
            return redirect(url_for('get_money_function', msg=msg))
    return render_template('pages/get_money.html', form=form)


@login_required
@app.route('/historico_solicitações_retirada.html')
def get_money_history_function():
    orders = GetMoney.query.filter_by(user_id=current_user.id)

    return render_template('/pages/get_money_history.html', orders=orders)


@login_required
@app.route('/historico_partidas.html')
def match_history():
    matches = Match.query.filter(or_(Match.match_creator_id == int(current_user.id),
                                     Match.competitor_id == int(current_user.id))).filter(
        and_(Match.match_status != "Procurando", Match.match_status != "Aguardando",
             Match.match_status != "Em Análise", Match.match_status != "Em Partida"))

    return render_template('/pages/match_history.html', matches=matches)


@login_required
@app.route('/minha_carteira.html')
def user_wallet():
    shopping = Sale.query.filter_by(user_id=current_user.id)
    get_wallet = User.query.filter_by(id=current_user.id).first()
    wallet_value = get_wallet.wallet
    return render_template('/pages/wallet.html', shopping=shopping, wallet=wallet_value)


@login_required
@app.route('/comprar.html')
def product_list():
    products_list = Product.query.all()
    return render_template('/pages/products_list.html', products_list=products_list)


@app.route('/buy/<int:id_product>', methods=['GET', 'POST'])
def buy_product(id_product):
    if request.method == 'POST':
        product = Product.query.filter_by(id=id_product).first()
        function_return = mercadopago.payment(request, product=product)
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


# Return sitemap
@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'sitemap.xml')


# Main Page
@app.route('/')
def home_page():
    return render_template('pages/index.html')


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
            current_sale = Sale.query.filter_by(preference_id=return_data['preference_id']).first()
            current_sale.collection_id = return_data['collection_id']
            current_sale.collection_status = return_data['collection_status']
            current_sale.payment_type = return_data['payment_type']
            current_sale.merchant_order_id = return_data['merchant_order_id']
            current_sale.preference_id = return_data['preference_id']
            current_sale.site_id = return_data['site_id']
            current_sale.processing_mode = return_data['processing_mode']
            current_sale.collection_status = return_data['collection_status']
            current_sale.sale_date = datetime.datetime.now()
            current_sale.save()

            collection_status = return_data['collection_status']

            add_user_wallet = User.query.filter_by(id=current_sale.user_id).first()
            actual_user_wallet_value = add_user_wallet.wallet
            new_user_wallet_value = actual_user_wallet_value + current_sale.product_value
            add_user_wallet.wallet = new_user_wallet_value
            add_user_wallet.save()

            return render_template('pages/payment_result.html', collection_status=collection_status)
        except Exception as err:
            print(err)
    else:
        # ->> What to do if the user closes the redirect page. Put here! <<-

        # mercadopago.receive_payment_info(request, return_data)

        # RETURN ERROR 101 - THE RETURN_DATA['PREFERENCE_ID'] IS EMPTY!

        return render_template('pages/buy_error.html')
    return render_template('pages/payment_result.html', collection_status=collection_status)


@app.route('/test.html', methods=['GET', 'POST'])
def test():
    result = mercadopago.get_payment_info(req=request)
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


@app.route('/admin_dashboard.html')
def admin_dashboard():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if current_user.user == 'admin':
        if current_user.password == 'test':
            return render_template('dashboard/dashboard_finance.html')
    else:
        return render_template('pages/error-404.html')


@login_required
@app.route('/dashboard.html', methods=['GET', 'POST'])
def admin_dashboard_users():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    elif not current_user.user == 'admin':
        return render_template('/sala_de_jogo.html')
    else:
        opened_matches = Match.query.filter_by(match_status='Procurando')
        ongoing_matches = Match.query.filter_by(match_status='Em partida')
        on_analyzes = Match.query.filter_by(match_status='Em Análise')
        finalized_matches = Match.query.filter(and_(Match.match_status != "Procurando",
                                                    Match.match_status != "Aguardando",
                                                    Match.match_status != "Em Análise",
                                                    Match.match_status != "Em Partida"))
        users_list = User.query.all()

        all_users = User.query.all()
        result_dict = {}
        labels = []
        results = []
        for user in all_users:
            labels.append(user.user)
            count = Match.query.filter_by(match_creator_username=user.user).count()
            results.append(count)

        # json_labels = jsonify({'labels': labels})
        # json_results = jsonify({'results': results})
        a = json.dumps(labels)
        b = jsonify(results)
        print(a)
        print(b)
        if request.method == "POST":
            id = request.form['id']
            redirect(url_for('match_winner', id=id))

        return render_template('dashboard/dashboard.html', labels=labels, results=results, opened_matches=opened_matches,
                               ongoing_matches=ongoing_matches, on_analyzes=on_analyzes,
                               finalized_matches=finalized_matches, users_list=users_list)


@login_required
@app.route('/ganhador_partida/<int:id>.html', methods=['GET', 'POST'])
def match_winner(id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    elif not current_user.user == 'admin':
        return render_template('/sala_de_jogo.html')
    current_match = Match.query.filter_by(id=id).first()
    match_creator = current_match.match_creator_gametag
    competitor = current_match.competitor_gametag
    current_match_users = [match_creator, competitor]
    form_function_return = match_winner_form(request.form, current_match_users)
    form = form_function_return[0]
    match_winner_choices = form_function_return[1]
    if request.method == 'POST':
        if form.validate_on_submit():
            match_winner_analyzed = dict(match_winner_choices).get(form.match_winner.data)
            current_match.match_status = match_winner_analyzed
            current_match.save()
            return redirect(url_for('admin_dashboard_users'))
        return render_template('dashboard/match_winner.html', form=form, id=id)

    return url_for('match_winner', form=form, id=id)


@login_required
@app.route('/data.html', methods=['GET', 'POST'])
def data():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    elif not current_user.user == 'admin':
        return render_template('/sala_de_jogo.html')

    all_users = User.query.all()
    result_dict = {}
    labels = []
    results = []
    for user in all_users:

        labels.append(user.user)
        count = Match.query.filter_by(match_creator_username=user.user).count()
        results.append(count)

    json_labels = jsonify({'labels': labels})
    json_results = jsonify({'results': results})

    return jsonify({'labels': labels, 'results': results})



@login_required
@app.route('/dashboard_finance.html', methods=['GET', 'POST'])
def dashboard_finance():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    elif not current_user.user == 'admin':
        return render_template('/sala_de_jogo.html')

    return render_template('dashboard/dashboard_finance.html')
