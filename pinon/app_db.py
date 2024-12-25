import pinon as pn
# Sqlite schema
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

class AppDb:
    def __init__(self, sql_connection):
        self.sql_connection = pn.sql_connection()

    def create_user(self, **kwargs):
        return self.create(USER_SCHEMA, kwargs)

    def read_user(self, id):
        return self.read(USER_SCHEMA, id)

    def read_user_by_name(self, name):
        cols_l = [c for c in list(USER_SCHEMA.keys())[1:]]
        sql = f"SELECT * FROM user WHERE name = {name};"
        cursor = self.sql_connection.cursor()
        cursor.execute(sql)
        res = cursor.fetchone()
        if res is None:
            return None
        else:
            return {k: v for (k, v) in zip(cols_l, res)}

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