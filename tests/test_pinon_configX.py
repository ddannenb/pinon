import unittest
import pathlib
from os import environ as env

import pinon as pn
import configX

TEST_PATH = pathlib.Path(__file__).parent
TEST_DATA_PATH = TEST_PATH / 'test_data'

env['SQLITE_DB_PATH'] = TEST_DATA_PATH.absolute().as_posix()
# env['SQLITE_DB_FILE'] = SQLITE_DB_FILE


class TestPinonConfigX(unittest.TestCase):
    def test_setup_db(self):
        cx = pn.ConfigX()
        cursor = cx.sql_connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        sql_res = cursor.fetchall()
        tables = [item[0] for item in sql_res]
        self.assertIn('user', tables)
        self.assertIn('peer_group', tables)
        self.assertIn('ticker', tables)

    def test_crud_user(self):
        cx = pn.ConfigX()
        user_name = 'Test User'
        new_user_name = 'New User Name'
        user_id = cx.create_user(user_name)
        read_user = cx.read_user(user_id)
        self.assertEqual(user_name, read_user['name'])

        num_up = cx.update_user(user_id, new_user_name)
        self.assertEqual(1, num_up)
        up_user = cx.read_user(user_id)
        self.assertEqual(new_user_name, up_user['name'])

        num_del = cx.delete_user(user_id)
        self.assertEqual(1, num_del)

        no_user = cx.read_user(user_id)
        self.assertIsNone(no_user)

    def test_crud_peer_group(self):
        cx = pn.ConfigX()
        peer_group_name = 'Peer group name'
        num_years_requested = 22
        user_name = 'Test Linked User'
        user_id = cx.create_user(user_name)
        peer_group_id = cx.create_peer_group(user_id, peer_group_name, num_years_requested)
        read_peer_group = cx.read_peer_group(peer_group_id)

        print('Break')

    def test_create(self):
        cx = pn.ConfigX()
        # cx.create('peer_group', {'user_id': 'A User Id', 'name': 'A Name', 'past_year_requested': 34})
        cx.create(configX.PEER_GROUP_SCHEMA, {'user_id': 111, 'name': 'A Name', 'past_years_requested': 34})
        print('Break')





if __name__ == '__main__':
    unittest.main()
