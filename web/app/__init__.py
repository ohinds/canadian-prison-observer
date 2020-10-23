# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import Flask
app = Flask(__name__)
app.config['TESTING'] = True
app.config['SECRET_KEY'] = 'oasdkjcoitrjjagsljksjdajs'

from app import views
