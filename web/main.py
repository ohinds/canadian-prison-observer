# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os

from flask import Flask, Markup, render_template
from jinja2 import TemplateNotFound
import yaml

app = Flask(__name__)
app.config['SECRET_KEY'] = 'oasdkjcoitrjjagsljksjdajs'


@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path>')
def index(path):
    if path == 'data.html':
        return data()

    try:
        return render_template(path)
    except TemplateNotFound:
        return render_template('page-404.html'), 404


@app.route('/reports/<path>')
def report(path):
    return render_template('report.html', path=path), 200


@app.route('/data/<path>')
def data(path='national-proportions-interactive'):
    _OBSERVABLE_IDS = {
        'National Proportions': 'the-whole-pie-canada',
        'Compare Within Province Over Time': 'graphs-within-province',
        'Compare Provinces Over Time': 'graphs-by-province',
        'Compare Provinces In A Year': 'across-province-bar-charts',
    }

    if not path.endswith('-interactive'):
        return render_template('page-404.html'), 404

    title = path.replace('-interactive', '').replace('-', ' ').title()

    if title not in _OBSERVABLE_IDS:
        return render_template('page-404.html'), 404

    observable_id = _OBSERVABLE_IDS[title]
    return render_template('data.html', title=title, observable_id=observable_id), 200


@app.route('/glossary.html')
def glossary():
    terms = yaml.safe_load(open(os.path.join('static', 'assets', 'txt', 'glossary.yaml')))
    print(terms)
    term_html = ''
    for term in sorted(terms):
        term_html += f'<dt>{term}</dt><dd>{terms[term]}</dd>'

    return render_template('glossary.html', terms=Markup(term_html))


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
