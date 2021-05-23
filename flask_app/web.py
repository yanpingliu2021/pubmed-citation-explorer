#!/usr/bin/env python
from flask import Flask, render_template, request, jsonify
import numpy as np
import logging

# EB looks for an 'application' callable by default.
application = Flask(__name__)

np.set_printoptions(precision=2)

#Model features
le_categories_Encdict = {'Article Keywords': 'keywords',
                        #  'Article Abstract':'abstract',
                         'Article Title': 'title',
                        #  'Medical Subject Headings':'mesh_terms',
                         'Chemicals Studied':'chemical_list'
                         }


@application.errorhandler(500)
def server_error(e):
    logging.exception('some eror')
    return """
    And internal error <pre>{}</pre>
    """.format(e), 500

@application.route("/", methods=['POST', 'GET'])
def index():

    return render_template('index.html',
                           imgSrc='static/images/titles_1976.png',
                           le_categories_Encdict = le_categories_Encdict)


# accepts either deafult values or user inputs
@application.route('/background_process', methods=['POST', 'GET'])
def background_process():
    if request.method == 'GET':
        Category = request.args.get('Category')
        Year = request.args.get('Year', type=int)
        filename = f'static/images/{Category}_{Year}.png'
    else:
        data = request.get_json()
        Category = data['Category']
        Year = data['Year']
        filename = f'static/images/{Category}_{Year}.png'

    return jsonify({'image_file':filename})

# when running app locally
if __name__ == '__main__':
    application.debug = False
    application.run()