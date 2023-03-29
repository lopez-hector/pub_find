# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import sys
import base64
import io

import pandas as pd
from flask import render_template, request, session
import flask_login
from flask_login import login_required
from jinja2 import TemplateNotFound
from apps.app_utils import append_query
from apps.home import blueprint
from apps.chartjs_utils import grab_plot_and_data
import json
import random


@blueprint.route('/home', methods=['POST', 'GET'])
def home():
    print("Home Page!!!")
    print(request)
    render_args = {}
    return render_template('home/home.html', **render_args)


@blueprint.route('/index', methods=['POST', 'GET'])
# @login_required
def index():

    render_args = {'segment': 'index',
                   }

    if request.method == 'POST':

            mod_render_args = {'segment': 'index',
                               }
            mod_render_args = render_args | mod_render_args

            return render_template('home/index.html', **mod_render_args)

    return render_template('home/index.html', **render_args)


# , text_ans='YAYA', graph_ans=True
# , text_ans=None, graph_ans=None

@blueprint.route('/<template>')
# @login_required
def route_template(template):
    print('-' * 200)
    print('THIS IS THE TEMPLATE', template)

    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        if segment == 'index.html':
            return index()
        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):
    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment
    except:
        return None