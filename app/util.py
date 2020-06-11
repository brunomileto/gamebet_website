# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from flask import json, url_for, jsonify, render_template
from jinja2 import TemplateNotFound
# from app import app

# from .models import Usuarios
from gamebet_website.app import app, db, bc # mail
from gamebet_website.app.models.models import Match
# from .common import *
from sqlalchemy import desc, or_
import hashlib
# from flask_mail import Message
import re
from flask import render_template

import os
import datetime
import time
import random


def check_results(match_id):
    match_for_check = Match.query.filter_by(id=match_id).first()

    if match_for_check.match_creator_match_result == 'E' and match_for_check.competitor_match_result == "E":
        match_for_check.match_status = 'EMPATE = CORRETO'
        match_for_check.save()
    else:
        match_for_check.match_status = 'ERRO - ALGUEM LANÇOU DIFERENTE'
        match_for_check.save()

    if match_for_check.match_creator_match_result == 'V' and match_for_check.competitor_match_result == "D":
        match_for_check.match_status = 'VITORIA CRIADOR = CORRETO'
        match_for_check.save()

    elif match_for_check.match_creator_match_result == 'D' and match_for_check.competitor_match_result == "V":
        match_for_check.match_status = 'VITORIA COMPETIDOR = CORRETO'
        match_for_check.save()
    else:
        match_for_check.match_status = 'ERRO - ALGUEM LANÇOU DIFERENTE'
        match_for_check.save()



# build a Json response
def response(data):
    return app.response_class(response=json.dumps(data),
                              status=200,
                              mimetype='application/json')


def g_db_commit():
    db.session.commit()


def g_db_add(obj):
    if obj:
        db.session.add(obj)


def g_db_del(obj):
    if obj:
        db.session.delete(obj)
