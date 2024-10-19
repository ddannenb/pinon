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
        user_id = cx.create_user(name=user_name)
        read_user = cx.read_user(user_id)
        self.assertEqual(user_name, read_user['name'])

        num_up = cx.update_user(user_id, name=new_user_name)
        self.assertEqual(1, num_up)
        up_user = cx.read_user(user_id)
        self.assertEqual(new_user_name, up_user['name'])

        num_del = cx.delete_user(user_id)
        self.assertEqual(1, num_del)

        no_user = cx.read_user(user_id)
        self.assertIsNone(no_user)

    def test_crud(self):
        cx = pn.ConfigX()
        pg_name = 'Peer group name'
        new_pg_name = 'New peer group name'
        pyr = 22
        new_nyr = 33
        un = 'Test Linked User'
        u_id = cx.create_user(name=un)
        pg_id = cx.create_peer_group(user_id=u_id, name=pg_name, past_years_requested=pyr)
        read_pg = cx.read_peer_group(pg_id)
        self.assertEqual(read_pg['user_id'], u_id)
        self.assertEqual(read_pg['name'], pg_name)
        self.assertEqual(read_pg['past_years_requested'], pyr)

        # num_up = cx.update_peer_group(pg_id, u_id, new_pg_name, new_nyr)
        num_up = cx.update_peer_group(pg_id, past_years_requested=new_nyr)
        self.assertEqual(1, num_up)
        up_pg = cx.read_peer_group(pg_id)
        self.assertEqual(up_pg['user_id'], u_id)
        self.assertEqual(up_pg['name'], pg_name)
        self.assertEqual(up_pg['past_years_requested'], new_nyr)



        print('Break')


if __name__ == '__main__':
    unittest.main()
