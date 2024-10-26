import sqlite3
import pathlib
from os import environ as env

import simfin as sf

PROJ_PATH = pathlib.Path(__file__).parent.parent

# Set env of same name to override these value in testing
SIMFIN_API_KEY_PATH = PROJ_PATH / "simfin_api_key"
SIMFIN_API_KEY_FILE = 'simfin_api_key.txt'

SIMFIN_DATA_PATH = PROJ_PATH / 'simfin_data'

SQLITE_DB_PATH = PROJ_PATH / "app_data"
SQLITE_DB_FILE = "pinon_db.sqlite"

class ConfigX:

    def __init__(self):
        # SqlLite set up
        self.sqlite_db_file_path = env.get('SQLITE_DB_PATH', SQLITE_DB_PATH.absolute().as_posix()) + '/' + env.get('SQLITE_DB_FILE', SQLITE_DB_FILE)
        self.sql_connection = sqlite3.connect(self.sqlite_db_file_path)
        self.setup_db()

        # Simfin set up
        self.simfin_data_path = env.get('SIMFIN_DATA_PATH', SIMFIN_DATA_PATH.absolute().as_posix())
        sf.set_data_dir(self.simfin_data_path)
        print(f"Simfin data directory: {self.simfin_data_path}")
        api_key = env.get('SIMFIN_API_KEY_PATH', SIMFIN_API_KEY_PATH.absolute().as_posix()) + '/' + env.get('SIMFIN_API_KEY_FILE', SIMFIN_API_KEY_FILE)
        sf.load_api_key(SIMFIN_API_KEY_PATH / SIMFIN_API_KEY_FILE)

        print('Pinon initialized!')


    def setup_db(self):
        cursor = self.sql_connection.cursor()
        # cursor.execute("CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS peer_group (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, name TEXT, past_years_requested INTEGER)")
        cursor.execute("CREATE TABLE IF NOT EXISTS ticker (id INTEGER PRIMARY KEY AUTOINCREMENT, peer_group_id INTEGER, ticker TEXT, evaluate BOOLEAN, peer_group_weight INTEGER)")
        self.sql_connection.commit()

    def get_sql_connection(self):
        return self.sql_connection



# Export a singleton instance of this class
def get_config(_instance = ConfigX()):
    return _instance