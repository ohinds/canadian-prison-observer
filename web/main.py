# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import Flask, render_template
from jinja2 import TemplateNotFound

app = Flask(__name__)
app.config['SECRET_KEY'] = 'oasdkjcoitrjjagsljksjdajs'


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


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
