import unittest
from df_names import EARNING_ESTIMATES, COLS_EARNINGS_ESTIMATES


class TestPinonDfNames(unittest.TestCase):
    def test_accessor(self):
        self.assertEqual(EARNING_ESTIMATES.TICKER, 'Ticker')

    def test_cols(self):
        cols = COLS_EARNINGS_ESTIMATES
        self.assertGreaterEqual(len(cols), 3)

if __name__ == '__main__':
    unittest.main()
