import sqlite3
import pathlib
from os import environ as env

import simfin as sf

from pinon import Config

PROJ_PATH = pathlib.Path(__file__).parent.parent

# Set env of same name to override these value in testing
SIMFIN_API_KEY_PATH = PROJ_PATH / "simfin_api_key"
SIMFIN_API_KEY_FILE = 'simfin_api_key.txt'

SIMFIN_DATA_PATH = PROJ_PATH / 'simfin_data'

SQLITE_DB_PATH = PROJ_PATH / "app_data"
SQLITE_DB_FILE = "pinon_db.sqlite"


class ConfigX:

    def __init__(self):
        self.sql_init()
        self.db_init()

        # Simfin set up
        self.simfin_data_path = env.get('SIMFIN_DATA_PATH', SIMFIN_DATA_PATH.absolute().as_posix())
        sf.set_data_dir(self.simfin_data_path)
        print(f"Simfin data directory: {self.simfin_data_path}")
        api_key = env.get('SIMFIN_API_KEY_PATH', SIMFIN_API_KEY_PATH.absolute().as_posix()) + '/' + env.get(
            'SIMFIN_API_KEY_FILE', SIMFIN_API_KEY_FILE)
        sf.load_api_key(SIMFIN_API_KEY_PATH / SIMFIN_API_KEY_FILE)

        print('Pinon initialized!')

    def sql_init(self):
        self.sqlite_db_file_path = env.get('SQLITE_DB_PATH', SQLITE_DB_PATH.absolute().as_posix()) + '/' + env.get(
            'SQLITE_DB_FILE', SQLITE_DB_FILE)

    def get_sql_connection(self):
        return sqlite3.connect(self.sqlite_db_file_path)

    def db_init(self):
        sql_conn = self.get_sql_connection()
        cursor = sql_conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)")
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS peer_group (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, name TEXT, past_years_requested INTEGER)")
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS ticker (id INTEGER PRIMARY KEY AUTOINCREMENT, peer_group_id INTEGER, ticker TEXT, evaluate BOOLEAN, target BOOLEAN, peer_group_weight INTEGER)")
        sql_conn.commit()
        sql_conn.close()


# Static accessors to singleton instance
def config(_inst=ConfigX()):
    return _inst


def sql_connection():
    return config().get_sql_connection()
