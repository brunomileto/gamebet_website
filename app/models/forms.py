# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""
from flask_login import LoginManager
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, PasswordField, IntegerField, SelectField
from wtforms.validators import Email, DataRequired, InputRequired

login_manager = LoginManager(),
GAME_CHOICES = [('', "Escolha um jogo:"), ('1', 'FIFA19'), ('2', 'FIFA20'), ('3', 'FIFA21')]
PLATFORM_CHOICES = [('', "Escolha uma plataforma:"), ('1', 'XOne'), ('2', 'PS4')]
BET_VALUE_CHOICES = [('', "Escolha um valor de aposta:"), ('1', 5), ('2', 10), ('3', 15), ('4', 20)]
RULES_CHOICES = [('', "Escolha uma regra, se quiser:"), ('1', 'REGRA 1'), ('2', 'REGRA 2'), ('3', 'REGRA 3')]
GAME_MODE_CHOICES = [('', "Escolha um modo de jogo:"), ('1', 'Elencos Online 1'), ('2', 'Ultimate Team')]
MATCH_RESULT_CHOICES = [('', "Qual foi o Seu Resultado, na partida?"), ('1', 'Vitória'), ('2', 'Derrota'), ('3', 'Empate')]




class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class RegisterForm(FlaskForm):
    name = StringField('Name')
    # first_name = StringField('First_name', validators=[DataRequired()])
    # last_name = StringField('Last_name', validators=[DataRequired()])
    # phone = IntegerField('Phone', validators=[DataRequired()])
    # cpf = IntegerField('cpf', validators=[DataRequired()])
    # birth_date = StringField('Birth_date', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])


class MatchCreationForm(FlaskForm):

    game_name = SelectField('game', choices=GAME_CHOICES, validators=[DataRequired()])
    platform = SelectField('platform', choices=PLATFORM_CHOICES, validators=[DataRequired()])
    bet_value = SelectField('bet_value', choices=BET_VALUE_CHOICES, validators=[DataRequired()])
    game_tag = StringField('game_tag', validators=[DataRequired()])
    rules = SelectField('rules', choices=RULES_CHOICES)
    comments = StringField('comments')
    game_mode = SelectField('game_mode', choices=GAME_MODE_CHOICES, validators=[DataRequired()])


class InsertResults(FlaskForm):
    # match_result = StringField('match_result', validators=[DataRequired()])
    match_result = SelectField('match_result', choices=MATCH_RESULT_CHOICES, validators=[DataRequired()])
    match_creator_goals = IntegerField('match_creator_goals', validators=[InputRequired()])
    competitor_goals = IntegerField('competitor_goals', validators=[InputRequired()])
    print = StringField('print', validators=[DataRequired()])


class GetMoneyForm(FlaskForm):
    value_wanted = IntegerField('value_wanted', validators=[InputRequired()])


def match_winner_form(form, current_match_users):

    match_winner_choices = [('', 'Defina o Ganhador!'), ('1', str(current_match_users[0])),
                            ('2', str(current_match_users[1]))]

    class MatchWinnerForm(FlaskForm):
        match_winner = SelectField('match_winner', choices=match_winner_choices, validators=[DataRequired()])

    form = MatchWinnerForm(form)
    returned_list = [form, match_winner_choices]
    return returned_list
