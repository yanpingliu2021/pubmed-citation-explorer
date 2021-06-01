#!/usr/bin/env python
from flask import Flask, render_template, request, jsonify
import psycopg2
import os
import pandas.io.sql as sqlio
import numpy as np
import logging
from wordcloud import WordCloud, STOPWORDS

# EB looks for an 'application' callable by default.
application = Flask(__name__)

np.set_printoptions(precision=2)

le_categories_Encdict = {'Article Keywords': 'keywords',
                         'Article Abstract':'abstract',
                         'Article Title': 'title',
                         'Chemicals Studied':'chemical_list'
                         }



#load database configs
if 'RDS_HOSTNAME' in os.environ:
    DATABASES = {
        'default': {
            'database_name': os.environ['RDS_DB_NAME'],
            'user': os.environ['RDS_USERNAME'],
            'password': os.environ['RDS_PASSWORD'],
            'host': os.environ['RDS_HOSTNAME'],
            'port': os.environ['RDS_PORT']
        }
    }

database_name = DATABASES['default']['database_name']
user = DATABASES['default']['user']
password = DATABASES['default']['password']
host = DATABASES['default']['host']
port = DATABASES['default']['port']

def get_data_from_rds(Category='keywords',Year=2020):
    connection = psycopg2.connect(user=user,
                                password=password,
                                host = host,
                                port = port,
                                database=database_name)
    connection.autocommit = True

    sql = f"select word, Y_{Year} from pubmed_{Category};"

    df = sqlio.read_sql_query(sql, connection)

    return df


@application.errorhandler(500)
def server_error(e):
    logging.exception('some eror')
    return """
    And internal error <pre>{}</pre>
    """.format(e), 500

@application.route("/", methods=['POST', 'GET'])
def index():

    return render_template('index.html',
                           imgSrc='static/images/keywords_2020.jpeg',
                           le_categories_Encdict = le_categories_Encdict)


# accepts either deafult values or user inputs
@application.route('/background_process', methods=['POST', 'GET'])
def background_process():
    if request.method == 'GET':
        Category = request.args.get('Category')
        Year = request.args.get('Year', type=int)
        filename = f'static/images/{Category}_{Year}.jpeg'
        if not os.path.exists(filename):
            freq_df = get_data_from_rds(Category, Year)
            # freq_df = get_data_from_rds()
            tuples = [tuple(x) for x in freq_df.values]
            stopwords = set(STOPWORDS)

            wordcloud = WordCloud(stopwords=stopwords,
                                width=1600,
                                height=800)\
                        .generate_from_frequencies(dict(tuples))

            wordcloud.to_image().save(filename)
    else:
        data = request.get_json()
        Category = data['Category']
        Year = data['Year']
        filename = f'static/images/{Category}_{Year}.jpeg'

    return jsonify({'image_file':filename})

# when running app locally
if __name__ == '__main__':
    application.debug = False
    application.run(host='0.0.0.0')