import boto3
import glob
# import nltk
# nltk.download('stopwords')
# !aws s3api create-bucket --bucket pubmed-baseline-xml --region us-east-1
import pubmed_parser as pp
import pandas as pd
import pandas as pd
import re, string
from nltk.corpus import stopwords
import psycopg2
from psycopg2 import Error, connect
from io import StringIO


database_name = 'baselinedb'
table_name = 'pubmed_raw'
user = "postgres"
password = "numsds498"
host = "pubmed-baseline.cxantjlnay5d.us-east-1.rds.amazonaws.com"
port = "5432"

## create database and table
#need to change security group in RDS to open port 5432
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

    # cursor.execute("drop table pubmed_raw")
    # connection.commit()
    # cursor.execute("""SELECT table_name FROM information_schema.tables
    #     WHERE table_schema = 'public'""")
    # cursor.fetchall()

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
    tokens = [x.lower().strip() for x in tokens if not re.search('\d+', x)]
    tokens = ';'.join(tokens)
    return tokens


# upload data to s3
S3_BUCKET_NAME = 'pubmed-baseline-xml'
files = sorted(glob.glob('../data/raw/*.xml.gz'))
for local_file_path in files:
    filename = local_file_path.split('/')[-1]
    print(f"upload file {local_file_path}")
    s3_connection = boto3.client("s3")
    try:
        s3_connection.upload_file(local_file_path, S3_BUCKET_NAME, filename)
        print("Upload Successful")
    except FileNotFoundError:
        print("The file was not found")



# function to copy df to rds
def copy_from_stringio(conn, df, table):
    """
    Here we are going save the dataframe in memory
    and use copy_from() to copy it to the table
    """
    # save dataframe to an in memory buffer
    buffer = StringIO()
    df.to_csv(buffer, header=False, sep='|', index=False)
    buffer.seek(0)

    cursor = conn.cursor()
    try:
        cursor.copy_from(buffer, table, sep="|")
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
        cursor.close()
        return 1
    print("copy_from_stringio() done")
    cursor.close()

# https://medium.com/analytics-vidhya/data-flow-between-python-aws-s3-bucket-aws-rds-243e38561bc2
# https://blog.dbi-services.com/loading-data-from-s3-to-aws-rds-for-postgresql/
# https://www.youtube.com/watch?v=RerDL93sBdY
# https://datascience-enthusiast.com/R/AWS_RDS_R_Python.html
# https://alexcodes.medium.com/upload-csv-files-to-postgresql-aws-rds-using-pythons-psycopg2-613992fcd7b


#upload data to rds
files = sorted(glob.glob('../data/raw/*.xml.gz'))
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

