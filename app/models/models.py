# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from gamebet_website.app import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(500))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    phone = db.Column(db.BIGINT)
    cpf = db.Column(db.BIGINT, unique=True)
    birth_date = db.Column(db.Date)
    wallet = db.Column(db.BIGINT)
    xbox_gametag = db.Column(db.String(120))
    psn_gametag = db.Column(db.String(120))
    matches = db.relationship('Match', backref='match_creator')

    def __init__(self, user, email, password, first_name, last_name, phone, cpf, birth_date, wallet, xbox_gametag,
                 psn_gametag):
        self.user = user
        self.password = password
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.cpf = cpf
        self.birth_date = birth_date
        self.wallet = wallet
        self.xbox_gametag = xbox_gametag
        self.psn_gametag = psn_gametag

    def __repr__(self):
        return str(self.id) + ' - ' + str(self.user)

    def save(self):
        # inject self into db session
        db.session.add(self)

        # commit change and save the object
        db.session.commit()


class Match(UserMixin, db.Model):
    __tablename__ = 'matches'

    id = db.Column(db.Integer, primary_key=True)
    match_creator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    competitor_id = db.Column(db.Integer)
    game_name = db.Column(db.String(120))
    platform = db.Column(db.String(120))
    bet_value = db.Column(db.Integer)
    match_creator_gametag = db.Column(db.String(120))
    competitor_gametag = db.Column(db.String(120))
    comment = db.Column(db.String(250))
    game_rules = db.Column(db.String(500))
    game_mode = db.Column(db.String(64))
    match_creator_username = db.Column(db.String(120))
    competitor_username = db.Column(db.String(120))
    match_status = db.Column(db.String(12))
    match_creator_match_result = db.Column(db.String(120))
    match_creator_match_creator_goals = db.Column(db.Integer)
    match_creator_competitor_goals = db.Column(db.Integer)
    match_creator_print = db.Column(db.String(500))
    competitor_match_result = db.Column(db.String(120))
    competitor_match_creator_goals = db.Column(db.Integer)
    competitor_competitor_goals = db.Column(db.Integer)
    competitor_print = db.Column(db.String(500))

    def __init__(self, match_creator_id, competitor_id, game_name, platform, bet_value, match_creator_gametag,
                 competitor_gametag, comment, game_rules, game_mode, match_creator_username, competitor_username,
                 match_status, match_creator_match_result, match_creator_match_creator_goals,
                 match_creator_competitor_goals, match_creator_print, competitor_match_result,
                 competitor_match_creator_goals, competitor_competitor_goals, competitor_print):
        self.match_creator_id = match_creator_id
        self.competitor_id = competitor_id
        self.game_name = game_name
        self.platform = platform
        self.bet_value = bet_value
        self.match_creator_gametag = match_creator_gametag
        self.competitor_gametag = competitor_gametag
        self.comment = comment
        self.game_rules = game_rules
        self.game_mode = game_mode
        self.match_creator_username = match_creator_username
        self.competitor_username = competitor_username
        self.match_status = match_status
        self.match_creator_match_result = match_creator_match_result
        self.match_creator_match_creator_goals = match_creator_match_creator_goals
        self.match_creator_competitor_goals = match_creator_competitor_goals
        self.match_creator_print = match_creator_print
        self.competitor_match_result = competitor_match_result
        self.competitor_match_creator_goals = competitor_match_creator_goals
        self.competitor_competitor_goals = competitor_competitor_goals
        self.competitor_print = competitor_print

    def __repr__(self):
        return str(self.id) + ' - ' + str(self.match_creator_username)

    def save(self):
        # inject self into db session
        db.session.add(self)

        # commit change and save the object
        db.session.commit()

        return self


class Product(UserMixin, db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(120), unique=True)
    product_value = db.Column(db.Integer)

    def __init__(self, product_name, product_value, user_id):
        self.product_name = product_name
        self.product_value = product_value

    def __repr__(self):
        return str(self.id) + ' - ' + str(self.product_name)

    def save(self):
        # inject self into db session
        db.session.add(self)

        # commit change and save the object
        db.session.commit()

        return self


class Sale(UserMixin, db.Model):
    __tablename__ = 'sales'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer)
    product_name = db.Column(db.String(120))
    product_value = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    user_username = db.Column(db.String(120))
    collection_id = db.Column(db.String(240), unique=True)
    collection_status = db.Column(db.String(120))
    payment_type = db.Column(db.String(120))
    merchant_order_id = db.Column(db.String(240), unique=True)
    preference_id = db.Column(db.String(240), unique=True)
    site_id = db.Column(db.String(64))
    processing_mode = db.Column(db.String(120))
    sale_date = db.Column(db.DateTime)

    def __init__(self, preference_id, product_id=None, product_name=None, product_value=None, user_id=None,
                 user_username=None, collection_id=None, collection_status=None,
                 payment_type=None, merchant_order_id=None, site_id=None, processing_mode=None, sale_date=None):
        self.product_id = product_id
        self.product_name = product_name
        self.product_value = product_value
        self.user_id = user_id
        self.user_username = user_username
        self.collection_id = collection_id
        self.collection_status = collection_status
        self.payment_type = payment_type
        self.merchant_order_id = merchant_order_id
        self.preference_id = preference_id
        self.site_id = site_id
        self.processing_mode = processing_mode
        self.sale_date = sale_date

    def __repr__(self):
        return str(self.id) + ' - ' + str(self.user_username)

    def save(self):
        # inject self into db session
        db.session.add(self)

        # commit change and save the object
        db.session.commit()

        return self

    def delete(self):
        db.session.delete(self)

        db.session.commit()

        return self

class GetMoney(UserMixin, db.Model):
    __tablename__ = 'get_money'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    user_username = db.Column(db.String(120))
    value_wanted = db.Column(db.BIGINT)
    order_date = db.Column(db.DateTime)
    order_status = db.Column(db.String(120))

    def __init__(self, user_id, user_username, value_wanted, order_date, order_status):
        self.user_id = user_id
        self.user_username = user_username
        self.value_wanted = value_wanted
        self.order_date = order_date
        self.order_status = order_status

    def __repr__(self):
        return str(self.id) + ' - ' + str(self.user_username)

    def save(self):
        # inject self into db session
        db.session.add(self)

        # commit change and save the object
        db.session.commit()

        return self