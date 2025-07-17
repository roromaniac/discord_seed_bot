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

def add_submission_to_db(discord_id, discord_name, async_time_timestamp, stream_key, initial_notif, yt_live_notif, streaming_notif, seed_notif, seed_number):
    """ Insert a new vendor into the vendors table """
    sql = """INSERT INTO async_submissions.async_submissions(discord_id, discord_name, async_time_timestamp, stream_key, initial_notif, yt_live_notif, streaming_notif, seed_notif, seed_number)
             VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING discord_id, discord_name, seed_number;"""
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                # execute the INSERT statement with dummy data
                cur.execute(sql, (discord_id, discord_name, async_time_timestamp, stream_key, initial_notif, yt_live_notif, streaming_notif, seed_notif, seed_number))
                # get the generated id back
                rows = cur.fetchone()
                if rows:
                    some_sort_of_id = rows[0]
                # commit the changes to the database
                conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

def query_database(sql, params=None):
    """ Execute a SQL query on the database """
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                if params:
                    cur.execute(sql, params)
                else:
                    cur.execute(sql)
                conn.commit()
                rows = cur.fetchall()
                return rows
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return None