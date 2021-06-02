"""
upload files to s3 and load it to AWS RDS PostgreSQL database
# reference:
# https://www.youtube.com/watch?v=RerDL93sBdY
# https://alexcodes.medium.com/upload-csv-files-to-postgresql-aws-rds-using-pythons-psycopg2-613992fcd7b

"""
import glob
# import nltk
# nltk.download('stopwords')
# !aws s3api create-bucket --bucket pubmed-baseline-xml --region us-east-1
import pubmed_parser as pp
import pandas as pd
import re, string
from nltk.corpus import stopwords
import psycopg2
from psycopg2 import Error
import os
from utils import load_config, copy_from_stringio

# load database configurations
# S3_BUCKET_NAME = 'pubmed-baseline-xml'
database_name, table_name, user, password, host, port = load_config()

## create database and table
# note: in order to connect, we need to change the security
# group in RDS console to open port 5432
try:
    connection = psycopg2.connect(user=user,
                                  password=password,
                                  host = host,
                                  port = port)
    connection.autocommit = True
    # Create a cursor to perform database operations
    cursor = connection.cursor()

    # Print PostgreSQL details
    print("PostgreSQL server information")
    print(connection.get_dsn_parameters(), "\n")
    # Executing a SQL query
    cursor.execute("SELECT version();")
    # Fetch result
    record = cursor.fetchone()
    print("You are connected to - ", record, "\n")

    #Preparing query to create a database
    sql = f'''CREATE database {database_name}''';

    #Creating a database
    cursor.execute(sql)
    print("Database created successfully........")

    connection.close()
    cursor.close()

    # connect to the created database
    connection = psycopg2.connect(user=user,
                                password=password,
                                host = host,
                                port = port,
                                database=database_name)

    # SQL query to create a new table
    create_table_query = f'''CREATE TABLE {table_name}
        (title TEXT,
        abstract TEXT,
        journal TEXT,
        authors TEXT,
        pubdate INT,
        mesh_terms TEXT,
        chemical_list TEXT,
        keywords TEXT); '''
    # Execute a command: this creates a new table
    cursor = connection.cursor()
    cursor.execute(create_table_query)
    connection.commit()
    print("Table created successfully in PostgreSQL ")

    # cursor.execute(f"drop table {table_name}")
    # connection.commit()
    # cursor.execute("""SELECT table_name FROM information_schema.tables
    #     WHERE table_schema = 'public'""")
    # cursor.fetchall()
    cursor.execute(f"""SELECT count('*') FROM {table_name}""")
    cursor.fetchall()

except (Exception, Error) as error:
    print("Error while connecting to PostgreSQL", error)
finally:
    if (connection):
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")


# functions to clean citation records
def clean_doc(doc):
    #split document into individual words
    tokens=doc.split()
    re_punc = re.compile('[%s]' % re.escape(string.punctuation))
    # remove punctuation from each word
    tokens = [re_punc.sub('', w) for w in tokens]
    # remove remaining tokens that are not alphabetic
    tokens = [word for word in tokens if word.isalpha()]
    # filter out short tokens
    tokens = [word for word in tokens if len(word) > 4]
    #lowercase all words
    tokens = [word.lower() for word in tokens]
    # filter out stop words
    stop_words = set(stopwords.words('english'))
    tokens = [w for w in tokens if not w in stop_words]
    tokens = ' '.join(tokens)
    # word stemming
    # ps=PorterStemmer()
    # tokens=[ps.stem(word) for word in tokens]
    return tokens

def clean_chemical(doc):
    #split document into individual words
    tokens=re.split('[;|:]', doc)
    # remove the ID
    tokens = [x.lower().strip() for x in tokens if not re.search('\d+', x)]
    tokens = ';'.join(tokens)

    return tokens


# # upload data to s3
# import boto3
# files = sorted(glob.glob('../data/raw/*.xml.gz'), reverse=True)[:100]
# for local_file_path in files:
#     filename = local_file_path.split('/')[-1]
#     print(f"upload file {local_file_path}")
#     s3_connection = boto3.client("s3")
#     try:
#         s3_connection.upload_file(local_file_path, S3_BUCKET_NAME, filename)
#         print("Upload Successful")
#     except FileNotFoundError:
#         print("The file was not found")


#u pload the last 100 xml files to rds
files = sorted(glob.glob('../data/raw/*.xml.gz'), reverse=True)[:100]
for idx, f in enumerate(files):
    print(f"parse file no{idx}:{f.split('/')[-1]}")
    parsed_articles = pp.parse_medline_xml(f,
                                        year_info_only=True,
                                        nlm_category=True,
                                        author_list=False)
    df = pd.DataFrame.from_dict(parsed_articles)\
        .filter(items=['title', 'abstract', 'journal', 'authors', 'pubdate', 'mesh_terms',
                       'publication_types', 'chemical_list', 'keywords', 'country'])
    df = df[df['publication_types'].str.lower().str.contains("journal article")].reset_index(drop=True)
    df = df[df['country'].str.lower().str.contains("united states")].reset_index(drop=True)
    df = df[df['title'] != ''].reset_index(drop=True)
    df['pubdate'] = df['pubdate'].astype(int)
    df.drop(columns=['publication_types', 'country'], inplace=True)
    print(f"total records in dataframe: {df.shape[0]}")
    df['title'] = df['title'].apply(lambda x: clean_doc(x))
    df['abstract'] = df['abstract'].apply(lambda x: clean_doc(x))
    df['keywords'] = df['keywords'].apply(lambda x: clean_doc(x))
    df['mesh_terms'] = df['mesh_terms'].apply(lambda x: clean_chemical(x))
    df['chemical_list'] = df['chemical_list'].apply(lambda x: clean_chemical(x))
    df = df[df['pubdate']>=2011].reset_index(drop=True)

    try:
        connection = psycopg2.connect(user=user,
                                    password=password,
                                    host = host,
                                    port = port,
                                    database=database_name)
        connection.autocommit = True
        cursor = connection.cursor()

        cursor.execute(f"Select count(*) FROM {table_name}")
        before_n = cursor.fetchall()[0][0]
        print(f"table records before upload: {before_n}")

        copy_from_stringio(connection,df,table_name)
        cursor.execute(f"Select count(*) FROM {table_name}")
        after_n = cursor.fetchall()[0][0]
        print(f"table records after upload: {after_n}")
        print(f"incremental table records after upload: {after_n-before_n}")

    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if (connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")



#upload additional files to RDS for years from 2011 to 2020
files = sorted(glob.glob('../data/raw/*.xml.gz'), reverse=True)[100:]
for idx, f in enumerate(files):
    print(f"parse file no{idx}:{f.split('/')[-1]}")
    parsed_articles = pp.parse_medline_xml(f,
                                        year_info_only=True,
                                        nlm_category=True,
                                        author_list=False)
    df = pd.DataFrame.from_dict(parsed_articles)\
        .filter(items=['title', 'abstract', 'journal', 'authors', 'pubdate', 'mesh_terms',
                       'publication_types', 'chemical_list', 'keywords', 'country'])
    df = df[df['publication_types'].str.lower().str.contains("journal article")].reset_index(drop=True)
    df = df[df['country'].str.lower().str.contains("united states")].reset_index(drop=True)
    df = df[df['title'] != ''].reset_index(drop=True)
    df['pubdate'] = df['pubdate'].astype(int)
    df.drop(columns=['publication_types', 'country'], inplace=True)
    df['title'] = df['title'].apply(lambda x: clean_doc(x))
    df['abstract'] = df['abstract'].apply(lambda x: clean_doc(x))
    df['keywords'] = df['keywords'].apply(lambda x: clean_doc(x))
    df['mesh_terms'] = df['mesh_terms'].apply(lambda x: clean_chemical(x))
    df['chemical_list'] = df['chemical_list'].apply(lambda x: clean_chemical(x))
    df = df[df['pubdate']>=2011].reset_index(drop=True)
    print(f"total records in dataframe: {df.shape[0]}")
    if df.shape[0] == 0:
        continue
    for yr in sorted(df['pubdate'].unique().tolist()):
        yr_df = df.loc[df['pubdate'] == yr].reset_index(drop=True)
        f_path = f'../data/processed/pubmed_baseline_{yr}.parquet'
        if os.path.exists(f_path):
            tmp_df = pd.read_parquet(f_path)
            com_df = yr_df.append(tmp_df).drop_duplicates().reset_index(drop=True)
            com_df.to_parquet(f_path, index=False)
            # print(com_df.shape)
        else:
            yr_df.to_parquet(f_path, index=False)


files = sorted(glob.glob('../data/processed/*.parquet'))
for _, f in enumerate(files):
    print(f"import file:{f.split('/')[-1]}")

    df = pd.read_parquet(f)

    try:
        connection = psycopg2.connect(user=user,
                                    password=password,
                                    host = host,
                                    port = port,
                                    database=database_name)
        connection.autocommit = True
        cursor = connection.cursor()

        cursor.execute(f"Select count(*) FROM {table_name}")
        before_n = cursor.fetchall()[0][0]
        print(f"table records before upload: {before_n}")

        copy_from_stringio(connection,df,table_name)
        cursor.execute(f"Select count(*) FROM {table_name}")
        after_n = cursor.fetchall()[0][0]
        print(f"table records after upload: {after_n}")
        print(f"incremental table records after upload: {after_n-before_n}")

    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if (connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")


#check database storage
connection = psycopg2.connect(user=user,
                            password=password,
                            host = host,
                            port = port,
                            database=database_name)
connection.autocommit = True
cursor = connection.cursor()
cursor.execute(f"SELECT pg_size_pretty(pg_database_size('{database_name}'));")
cursor.fetchone()
cursor.execute(f"SELECT pg_size_pretty( pg_total_relation_size('{table_name}') );;")
cursor.fetchone()
cursor.close()
connection.close()