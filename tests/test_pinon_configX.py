import unittest
import pinon as pn


class TestPinonConfigX(unittest.TestCase):
    def test_create_connection(self):
        cx = pn.ConfigX()
        print('Here')


if __name__ == '__main__':
    unittest.main()
