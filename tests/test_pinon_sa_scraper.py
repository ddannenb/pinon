import unittest
import pinon as pn


class TestPinonSAScraper(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.scraper = pn.SaScraper()

    def test_get_ticker_id(self):
        scr = pn.SaScraper()
        id = scr.get_ticker_id('V')
        self.assertEqual(id,9691, 'The returned ticker id is not correct.')  # add assertion here
        id = scr.get_ticker_id('NOTATICKER')
        self.assertIsNone(id, 'The ticker is invalid and the ticker id should be None.')

    def test_parse_tickers(self):
        ticks = self.scraper.parse_tickers('V,  INTC  , CAT')
        self.assertEqual(len(ticks), 3, 'Did not return correct size list')
        self.assertListEqual(ticks, ['V', 'INTC', 'CAT'], 'Did not parse correctly')
        ticks = self.scraper.parse_tickers(['V', 'INTC', 'CAT'])
        self.assertEqual(len(ticks), 3, 'Did not return correct size list')
        self.assertListEqual(ticks, ['V', 'INTC', 'CAT'], 'Did not parse correctly')
        with self.assertRaises(TypeError): self.scraper.parse_tickers(1112)


    def test_get_earnings_estimate(self):
        scr = pn.SaScraper()
        eest = scr.get_earnings_estimate('V')
        print(eest)

    def test_get_earnings_estimates(self):
        scr = pn.SaScraper()
        scr.get_earnings_estimates('V,  INTC  , CAT')
        scr.get_earnings_estimates(['V', 'INTC', 'CAT'])


if __name__ == '__main__':
    unittest.main()
