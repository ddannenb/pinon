import sqlite3
import pathlib
from os import environ as env

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

    def create_user(self, name):
        return self.create(USER_SCHEMA, {'name':name})
        # cursor = self.sql_connection.cursor()
        # sql = f"INSERT into user(name) VALUES ('{name}') RETURNING id"
        # cursor.execute(sql)
        # res = cursor.fetchone()[0]
        # self.sql_connection.commit()
        # return res

    def read_user(self, id):
        return self.read(USER_SCHEMA, id)
        # cursor = self.sql_connection.cursor()
        # sql = f"SELECT name FROM user WHERE id={id};"
        # cursor.execute(sql)
        # res = cursor.fetchone()
        # if res is None:
        #     return None
        # else:
        #     return {'name': res[0]}

    def delete_user(self, id):
        cursor = self.sql_connection.cursor()
        sql = f"DELETE FROM user WHERE id={id};"
        cursor.execute(sql)
        self.sql_connection.commit()
        return cursor.rowcount

    def update_user(self, id, name):
        return self.update(USER_SCHEMA, {'name': name})
        # cursor = self.sql_connection.cursor()
        # sql = f"UPDATE user SET name='{name}' WHERE id={id};"
        # cursor.execute(sql)
        # self.sql_connection.commit()
        # return cursor.rowcount

    def create_peer_group(self, user_id, name, past_years_requested):
        return self.create(configX.PEER_GROUP_SCHEMA, {'user_id': user_id, 'name': name, 'past_years_requested': past_years_requested})
        # cursor = self.sql_connection.cursor()
        # sql = f"INSERT into peer_group(user_id, name, past_years_requested) VALUES ('{user_id}', '{name}', '{past_years_requested}') RETURNING id"
        # cursor.execute(sql)
        # res = cursor.fetchone()[0]
        # self.sql_connection.commit()
        # return res

    def read_peer_group(self, id):
        return self.read(configX.PEER_GROUP_SCHEMA, id)
        # cursor = self.sql_connection.cursor()
        # sql = f"SELECT name, past_years_requested FROM peer_group WHERE id={id};"
        # cursor.execute(sql)
        # res = cursor.fetchone()
        # if res is None:
        #     return None
        # else:
        #     return {'name': res[0], 'past_years_requested': res[1]}

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
        cursor = self.sql_connection.cursor()
        table_name = schema[0]
        cols = ', '.join([c for c in values.keys()])
        vals = ', '.join([self.resolve_type(schema[k], values[k]) for k in values.keys()])
        sql = f"INSERT INTO {table_name}({cols}) VALUES ({vals}) RETURNING id"
        cursor.execute(sql)
        res = cursor.fetchone()[0]
        self.sql_connection.commit()
        return res

    def read(self, schema, id):
        cursor = self.sql_connection.cursor()
        table_name = schema[0]
        cols_l = [c for c in list(schema.keys())[1:]]
        cols = ', '.join(cols_l)
        sql = f"SELECT {cols} FROM {table_name} WHERE id = {id}"
        cursor.execute(sql)
        res = cursor.fetchone()
        if res is None:
            return None
        else:
            return {k: v for (k, v) in zip(cols_l, res)}

    def update(self, schema, id, values):
        cursor = self.sql_connection.cursor()
        table_name = schema[0]
        sets_l = [f"{k} = {self.resolve_type(schema[k], values[k])}" for k in values.keys()]
        sets = ', '.join(sets_l)
        sql = f"UPDATE {table_name} SET {sets} WHERE id = {id}"
        print('Break')

