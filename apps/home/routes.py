# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import os

ROOT_DIRECTORY = './appel'
MODEL_ROOT = './instructorXL_model'

os.environ['ROOT_DIRECTORY'] = ROOT_DIRECTORY
os.environ['MODEL_ROOT'] = MODEL_ROOT

from flask import render_template, request, redirect, url_for
from jinja2 import TemplateNotFound
from apps.home import blueprint
import os
from src.main import get_model, get_answers, initialize_docstore
from src.embedding_utils import embed_queries
import modal

FILE_DIRECTORY = os.path.join(ROOT_DIRECTORY, 'pdfs')
EMB_DIR = os.path.join(ROOT_DIRECTORY, 'embeddings')
CITATIONS_FILE = os.path.join(ROOT_DIRECTORY, 'citations.json')
DOCS_FILE = os.path.join(ROOT_DIRECTORY, 'docs')
INDEX_DIRECTORY = os.path.join(ROOT_DIRECTORY, 'index')


@blueprint.route('/', methods=['POST', 'GET'])
def route_to_index():
    return redirect(url_for('home_blueprint.index'))


def get_question_embeddings(queries):
    model = get_model()
    question_embeddings = embed_queries(queries, model)

    return question_embeddings


@blueprint.route('/index', methods=['POST', 'GET'])
def index():
    # grab docs if exists, update if pdfs added/deleted, initialize if doesn't exist
    docs, model = initialize_docstore(force_rebuild=True)

    render_args = {'none': 'none'}

    if request.method == 'POST':

        queries = [request.form['user_query']]

        print('embedding')
        f = modal.Function.lookup("PubFind_2", "get_question_embedding")
        question_embeddings = f.call(queries, MODEL_ROOT)
        # del model
        print(queries)
        print('getting answers')
        answers = get_answers(docs, queries, question_embeddings)

        print(answers[0].formatted_answer)

        mod_render_args = {'text_ans': answers[0].answer,
                           'question': queries[0],
                           'references': answers[0].references,
                           'context_ids': list(answers[0].passages.keys()),
                           'contexts': list(answers[0].passages.values())}

        for k in mod_render_args:
            render_args[k] = mod_render_args[k]

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
