import os
from io import StringIO
from psycopg2 import Error

def load_config():
    if 'RDS_HOSTNAME' in os.environ:
        DATABASES = {
            'default': {
                'database_name': os.environ['RDS_DB_NAME'],
                'user': os.environ['RDS_USERNAME'],
                'password': os.environ['RDS_PASSWORD'],
                'host': os.environ['RDS_HOSTNAME'],
                'port': os.environ['RDS_PORT'],
                'table_name': os.environ['RDS_TB_NAME']
            }
        }

    database_name = DATABASES['default']['database_name']
    table_name = DATABASES['default']['table_name']
    user = DATABASES['default']['user']
    password = DATABASES['default']['password']
    host = DATABASES['default']['host']
    port = DATABASES['default']['port']

    return (database_name,table_name,user,password,host,port)


# function to copy df to rds
def copy_from_stringio(conn, df, table):
    """
    Here we are going save the dataframe in memory
    and use copy_from() to copy it to the table
    """
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