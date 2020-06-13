from flask_table import Table, Col, ButtonCol
from flask_login import current_user


class SearchMatchTable(Table):
    id = Col('Id')
    match_creator_id = Col('Id - Criador Partida')
    competitor_id = Col('Id - Competidor')
    game_name = Col('Nome Jogo')
    # platform = Col('Nome da Plataforma')
    # bet_value = Col('Valor Aposta')
    # match_creator_gametag = Col('gametag Criador Partida')
    # competitor_gametag = Col('gametag Competidor')
    # comment = Col('Comentários')
    # game_rules = Col('Regras')
    # game_mode = Col('Modo de Jogo')
    # match_creator_username = Col('Nome Usuário Criador Partida')
    # competitor_username = Col('Nome Usuário Competidor')
    # match_status = Col('Status da Partida')
    match_accepting = ButtonCol('Aceitar', 'accept_match', url_kwargs=dict(id='id'))


class AcceptMatch(Table):
    id = Col('Id')
    match_creator_id = Col('Id - Criador Partida')
    competitor_id = Col('Id - Competidor')
    game_name = Col('Nome Jogo')
    platform = Col('Nome da Plataforma')
    bet_value = Col('Valor Aposta')
    match_creator_gametag = Col('gametag Criador Partida')
    competitor_gametag = Col('gametag Competidor')
    comment = Col('Come ntários')
    game_rules = Col('Regras')
    game_mode = Col('Modo de Jogo')
    match_creator_username = Col('Nome Usuário Criador Partida')
    competitor_username = Col('Nome Usuário Competidor')
    match_status = Col('Status da Partida')
    match_accepting = ButtonCol('Aceitar', 'confirm_accept_match', url_kwargs=dict(id='id'))


class ShowCurrentAcceptedMaches(Table):
    id = Col('Id')
    match_creator_id = Col('Id - Criador Partida')
    competitor_id = Col('Id - Competidor')
    game_name = Col('Nome Jogo')
    platform = Col('Nome da Plataforma')
    bet_value = Col('Valor Aposta')
    match_creator_gametag = Col('gametag Criador Partida')
    competitor_gametag = Col('gametag Competidor')
    comment = Col('Comentários')
    game_rules = Col('Regras')
    game_mode = Col('Modo de Jogo')
    match_creator_username = Col('Nome Usuário Criador Partida')
    competitor_username = Col('Nome Usuário Competidor')
    match_status = Col('Status da Partida')
    match_accepting = ButtonCol('Inserir Resultados', 'insert_results', url_kwargs=dict(id='id'))


class ShowHistoric(Table):
    id = Col('Id')
    match_creator_id = Col('Id - Criador Partida')
    competitor_id = Col('Id - Competidor')
    game_name = Col('Nome Jogo')
    platform = Col('Nome da Plataforma')
    bet_value = Col('Valor Aposta')
    match_creator_gametag = Col('gametag Criador Partida')
    competitor_gametag = Col('gametag Competidor')
    comment = Col('Comentários')
    game_rules = Col('Regras')
    game_mode = Col('Modo de Jogo')
    match_creator_username = Col('Nome Usuário Criador Partida')
    competitor_username = Col('Nome Usuário Competidor')
    match_status = Col('Status da Partida')
