# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""
from flask_login import LoginManager
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SelectField
from wtforms.validators import Email, DataRequired

from .validators import MyFloatField

login_manager = LoginManager()


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class RegisterForm(FlaskForm):
    name = StringField('Name')
    first_name = StringField('First_name', validators=[DataRequired()])
    last_name = StringField('Last_name', validators=[DataRequired()])
    phone = IntegerField('Phone', validators=[DataRequired()])
    cpf = IntegerField('cpf', validators=[DataRequired()])
    birth_date = StringField('Birth_date', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])


class MatchesForm(FlaskForm):
    game_name = SelectField('game', choices=[(""), ('FIFA19'), ('FIFA20'), ('FIFA21')], validators=[DataRequired()])
    platform = SelectField('platform', choices=[(""),('Xbox ONE'), ('Play Station 4')], validators=[DataRequired()])
    bet_value = MyFloatField('bet_value', validators=[DataRequired()])
    if str(platform) == 'PLAY STATION 4':
        game_tag = StringField('game_tag_psn', validators=[DataRequired()])
    else:
        game_tag = StringField('game_tag_xbox_live', validators=[DataRequired()])
    rules_comments = StringField('rules_comments', validators=[DataRequired()])
    game_mode = SelectField('game_mode', choices=[(""), ('Elencos Online'), ('Ultimate Team')], validators=[DataRequired()])
