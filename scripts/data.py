import os
import psycopg2
from configparser import ConfigParser
from scripts.get_submission import Response

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASYNC_DB_CREDENTIALS_PATH = os.path.join(BASE_DIR, "credentials", "database.ini")

def load_config(filename=ASYNC_DB_CREDENTIALS_PATH, section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)
    # get section, default to postgresql
    config = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            config[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
    return config

def connect(config):
    """ Connect to the PostgreSQL database server """
    try:
        # connecting to the PostgreSQL server
        with psycopg2.connect(**config) as conn:
            print('Connected to the PostgreSQL server.')
            return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)

def add_submission_to_db(async_submission: Response, error_text, str, seed_number: int):
    """ Insert multiple vendors into the vendors table  """
    ### DOUBLE CHECK WHICH VARIABLES YOU HAVE HERE ON PGADMIN
    sql = "INSERT INTO async_submissions.async_submissions(discord_id, discord_user, async_timestamp, valid_async, invalid_reason) VALUES(%s) RETURNING *"
    # ADD SEED_NUMBER, INITIAL, YTLIVE, STREAMING, AND SEED NOTIFICATIONS AS TABLE COLUMNS
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with  conn.cursor() as cur:
                # execute the INSERT statement
                cur.execute(sql, async_submission)
            # commit the changes to the database
            conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

if __name__ == '__main__':
    config = load_config()
    connect(config)