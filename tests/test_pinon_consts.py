import unittest
import pathlib
from consts import EARNING_ESTIMATES, COLS_EARNINGS_ESTIMATES
from consts import gen_headers

TEST_PATH = pathlib.Path(__file__).parent
TEST_DATA_PATH = TEST_PATH / 'test_data'

class TestPinonConsts(unittest.TestCase):
    def test_accessor(self):
        self.assertEqual(EARNING_ESTIMATES.TICKER, 'Ticker')

    def test_cols(self):
        cols = COLS_EARNINGS_ESTIMATES
        self.assertGreaterEqual(len(cols), 3)

    def test_gen_headers(self):
        hdr = gen_headers(TEST_DATA_PATH / 'gen_hdr_data.txt')


if __name__ == '__main__':
    unittest.main()
