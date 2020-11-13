# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import render_template
from jinja2 import TemplateNotFound

from app import app


@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path>')
def index(path):
    try:
        return render_template(path)
    except TemplateNotFound:
        return render_template('page-404.html'), 404


@app.route('/reports/<path>')
def report(path):
    return render_template('report.html', path=path), 200

@app.route('/liveness_check')
def liveness_check():
    return 'yes'


@app.route('/readiness_check')
def readiness_check():
    return 'yes'
