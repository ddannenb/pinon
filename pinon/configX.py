import sqlite3
import pathlib
from os import environ as env

from matplotlib.table import table
from pandas.io.sql import table_exists

import configX

PROJ_PATH = pathlib.Path(__file__).parent.parent
SQLITE_DB_PATH = PROJ_PATH / "app_data"
SQLITE_DB_FILE = "pinon_db.sqlite"

USER_SCHEMA = {
    0: 'user',
    'name': 'TEXT'
}

PEER_GROUP_SCHEMA = {
    0: 'peer_group',
    'user_id': 'INTEGER',
    'name': 'TEXT',
    'past_years_requested': 'INTEGER'
}

env['SQLITE_DB_PATH'] = SQLITE_DB_PATH.absolute().as_posix()
env['SQLITE_DB_FILE'] = SQLITE_DB_FILE


class ConfigX:
    def __init__(self):
        self.sqlite_db_file_path = env['SQLITE_DB_PATH'] + '/' + env['SQLITE_DB_FILE']
        self.sql_connection = sqlite3.connect(self.sqlite_db_file_path)
        self.setup_db()

    def setup_db(self):
        cursor = self.sql_connection.cursor()
        # cursor.execute("CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS peer_group (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, name TEXT, past_years_requested INTEGER)")
        cursor.execute("CREATE TABLE IF NOT EXISTS ticker (id INTEGER PRIMARY KEY AUTOINCREMENT, peer_group_id INTEGER, ticker TEXT, evaluate BOOLEAN, peer_group_weight INTEGER)")
        self.sql_connection.commit()

    def create_user(self, **kwargs):
        return self.create(USER_SCHEMA, kwargs)

    def read_user(self, id):
        return self.read(USER_SCHEMA, id)

    def delete_user(self, id):
        return self.delete(USER_SCHEMA, id)

    def update_user(self, id, **kwargs):
        return self.update(USER_SCHEMA, id, kwargs)

    def create_peer_group(self, **kwargs):
        return self.create(PEER_GROUP_SCHEMA, kwargs)

    def read_peer_group(self, id):
        return self.read(PEER_GROUP_SCHEMA, id)

    def update_peer_group(self, id, **kwargs):
        return self.update(PEER_GROUP_SCHEMA, id, kwargs)


    def resolve_type(self, type, val):
        match type:
            case 'TEXT':
                return f"'{val}'"
            case 'INTEGER':
                return f"{val}"
            case 'BOOL':
                return 0 if val else 1
            case _:
                return f"{val}"

    def create(self, schema, values):
        table_name = schema[0]
        cols = ', '.join([c for c in values.keys()])
        vals = ', '.join([self.resolve_type(schema[k], values[k]) for k in values.keys()])
        sql = f"INSERT INTO {table_name}({cols}) VALUES ({vals}) RETURNING id;"
        cursor = self.sql_connection.cursor()
        cursor.execute(sql)
        res = cursor.fetchone()[0]
        self.sql_connection.commit()
        return res

    def read(self, schema, id):
        table_name = schema[0]
        cols_l = [c for c in list(schema.keys())[1:]]
        cols = ', '.join(cols_l)
        sql = f"SELECT {cols} FROM {table_name} WHERE id = {id};"
        cursor = self.sql_connection.cursor()
        cursor.execute(sql)
        res = cursor.fetchone()
        if res is None:
            return None
        else:
            return {k: v for (k, v) in zip(cols_l, res)}

    def update(self, schema, id, values):
        table_name = schema[0]
        sets_l = [f"{k} = {self.resolve_type(schema[k], values[k])}" for k in values.keys()]
        sets = ', '.join(sets_l)
        sql = f"UPDATE {table_name} SET {sets} WHERE id = {id}"
        cursor = self.sql_connection.cursor()
        cursor.execute(sql)
        self.sql_connection.commit()
        return cursor.rowcount

    def delete(self, schema, id):
        table_name = schema[0]
        sql = f"DELETE FROM {table_name} WHERE id={id};"
        cursor = self.sql_connection.cursor()
        cursor.execute(sql)
        self.sql_connection.commit()
        return cursor.rowcount
