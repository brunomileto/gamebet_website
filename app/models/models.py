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
    matches = db.relationship('Match', backref='match_creator')

    def __init__(self, user, email, password, first_name, last_name, phone, cpf, birth_date):
        self.user = user
        self.password = password
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.cpf = cpf
        self.birth_date = birth_date

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

    def __init__(self, match_creator_id, competitor_id, game_name, platform, bet_value, match_creator_gametag,
                 competitor_gametag, comment, game_rules, game_mode, match_creator_username, competitor_username,
                 match_status):
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

    def __repr__(self):
        return str(self.id) + ' - ' + str(self.match_creator_username)

    def save(self):
        # inject self into db session
        db.session.add(self)

        # commit change and save the object
        db.session.commit()

        return self
