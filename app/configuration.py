# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

import os
from os import environ

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))


class DebugConfig():
    CSRF_ENABLED = True
    SECRET_KEY = "77tgFCdrEEdv77554##@3"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True

    # Local Database URI

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:Bruno123456789@localhost/gamebetdb'

    # PythonAnywhere Database DebugConfig - Comment this when working localhost
    # SQLALCHEMY_POOL_RECYCLE = 299
    # SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{username}:{password}@{hostname}/{databasename}".format(
    #     username="gamebet",
    #     password="Bruno123456789",
    #     hostname="gamebet.mysql.pythonanywhere-services.com",
    #     databasename="gamebet$gamebetdb",
    # )


class ProductionConfig(DebugConfig):
    DEBUG = False

    # Security
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600

    # PostgreSQL database
    SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}:{}/{}'.format(
        environ.get('APPSEED_DATABASE_USER', 'appseed'),
        environ.get('APPSEED_DATABASE_PASSWORD', 'appseed'),
        environ.get('APPSEED_DATABASE_HOST', 'db'),
        environ.get('APPSEED_DATABASE_PORT', 5432),
        environ.get('APPSEED_DATABASE_NAME', 'appseed')
    )


config_dict = {
    'Production': ProductionConfig,
    'Debug': DebugConfig
}
