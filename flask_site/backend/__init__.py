# -*- coding: utf-8 -*-

"""
"""

__author__ = 'lijingang'


from flask import Flask, render_template

from flask_site.ext.db import db
from flask_site.backend.config import config
from flask_site.backend.newsmth.views import score as newsmth_score


app = Flask(__name__)

app.config.from_object(config['dev'])

app.register_blueprint(newsmth_score.mod)

db.init_app(app)


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404



