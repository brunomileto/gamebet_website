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
    # first_name = StringField('First_name', validators=[DataRequired()])
    # last_name = StringField('Last_name', validators=[DataRequired()])
    # phone = IntegerField('Phone', validators=[DataRequired()])
    # cpf = IntegerField('cpf', validators=[DataRequired()])
    # birth_date = StringField('Birth_date', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])


class MatchCreationForm(FlaskForm):
    game_name = StringField('game')
    platform = StringField('platform')
    # game_name = SelectField('game', choices=[(""), ('FIFA19'), ('FIFA20'), ('FIFA21')])
    # platform = SelectField('platform', choices=[(""),('Xbox ONE'), ('Play Station 4')])
    bet_value = IntegerField('bet_value', validators=[DataRequired()])
    if str(platform) == 'PLAY STATION 4':
        game_tag = StringField('game_tag_psn', validators=[DataRequired()])
    else:
        game_tag = StringField('game_tag_xbox_live', validators=[DataRequired()])
    rules_comments = StringField('rules_comments', validators=[DataRequired()])
    # game_mode = SelectField('game_mode', choices=[(""), ('Elencos Online'), ('Ultimate Team')])
    game_mode = StringField("game_mode")


class InsertResults(FlaskForm):
    # match_id = IntegerField('match_id')
    # game_name = StringField('game_name')
    # bet_value = IntegerField('bet_value')
    # match_creator_gametag = StringField('match_creator_gametag')
    # competitor_gametag = StringField('competitor_gametag')
    # comment = StringField('comment')
    # game_rules = StringField('game_rules')
    # match_creator_username = StringField('match_creator_username')
    # competitor_username = StringField('competitor_username')
    # match_status = StringField('match_status')
    match_result = StringField('match_result', validators=[DataRequired()])
    match_creator_goals = IntegerField('match_creator_goals', validators=[DataRequired()])
    competitor_goals = IntegerField('competitor_goals', validators=[DataRequired()])
    print = StringField('print', validators=[DataRequired()])
    # competitor_match_result = StringField('competitor_match_result')
    # competitor_match_creator_goals = IntegerField('competitor_match_creator_goals')
    # competitor_competitor_goals = IntegerField('competitor_competitor_goals')
    # competitor_print = StringField('competitor_print')

# class MatchCompetitorInsertResults(Table):
#     id = Col('Id')
#     match_id = Col('Id - Partida')
#     game_name = Col('Nome Jogo')
#     bet_value = Col('Valor Aposta')
#     match_creator_gametag = Col('gametag Criador Partida')
#     competitor_gametag = Col('gametag Competidor')
#     comment = Col('Comentários')
#     game_rules = Col('Regras')
#     match_creator_username = Col('Nome Usuário Criador Partida')
#     competitor_username = Col('Nome Usuário Competidor')
#     match_status = Col('Status da Partida')
#     match_creator_match_result = Col('Resultado Partida: V, D, E', show=False)
#     match_creator_match_creator_goals = Col('Quantos Gols você Fez?', show=False)
#     match_creator_competitor_goals = Col('Quantos Gols seu adversário fez?', show=False)
#     match_creator_print = Col('Link Print', show=False)
#     competitor_match_result = Col('Resultado Partida: V, D, E', show=True)
#     competitor_match_creator_goals = Col('Quantos Gols seu adversário fez?', show=True)
#     competitor_competitor_goals = Col('Quantos Gols você Fez?', show=True)
#     competitor_print = Col('Link Print', show=True)
#     match_accepting = ButtonCol('Inserir Resultados', 'match_results', url_kwargs=dict(id='id'))
