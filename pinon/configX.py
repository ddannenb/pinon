import sqlite3
import pathlib
from os import environ as env

PROJ_PATH = pathlib.Path(__file__).parent.parent
SQLITE_DB_PATH = PROJ_PATH / "app_data"
SQLITE_DB_FILE = "pinon_db.sqlite"

env['SQLITE_DB_PATH'] = SQLITE_DB_PATH.absolute().as_posix()
env['SQLITE_DB_FILE'] = SQLITE_DB_FILE


class ConfigX:
    def __init__(self):
        self.sqlite_db_file_path = env['SQLITE_DB_PATH'] + '/' + env['SQLITE_DB_FILE']
        self.sql_connection = sqlite3.connect(self.sqlite_db_file_path)
        print(f"Changes: {self.sql_connection.total_changes}")