# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

import os
import pymysql

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

class Config():

	CSRF_ENABLED = True
	SECRET_KEY   = "77tgFCdrEEdv77554##@3"

	SQLALCHEMY_TRACK_MODIFICATIONS 	= False
	DEBUG = True

    # Local Database URI

	# SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:Bruno123456789@localhost/gamebetdb'

	# PythonAnywhere Database Config - Comment this when working localhost
	SQLALCHEMY_POOL_RECYCLE = 299
	SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{username}:{password}@{hostname}/{databasename}".format(
        username="gamebet",
        password="Bruno123456789",
        hostname="gamebet.mysql.pythonanywhere-services.com",
        databasename="gamebet$gamebetdb",
    )

