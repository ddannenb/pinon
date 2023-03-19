import pandas as pd
import simfin_global_cache as sfc

class DailyPrices:
    def __init__(self):
        self.daily_prices = sfc._load_daily_share_prices()
        self.daily_share_price_ratios = sfc._load_daily_share_price_ratios()

    def get_daily_prices(self, tickers):
        return self.daily_prices.loc[tickers]

    def get_daily_share_price_ratios(self, ticker):
        return self.daily_share_price_ratios.loc[ticker]
    def get_downsampled_prices(self, ticker, period='quarterly'):
        """
         Returns prices downsampled to quarterly mean. The quarterly date index represents the right side (end) of the interval
        """
        pl = period.lower()
        rule = None
        if pl == 'quarterly' or pl == 'q':
            rule = 'Q'
        if pl == 'monthly' or pl == 'm':
            rule = 'M'

        return self.daily_prices.loc[ticker].resample(rule).mean()

    def get_downsampled_share_price_ratios(self, ticker, period='quarterly'):
        """
         Returns share price ratios downsampled to quarterly mean. The quarterly date index represents the right side (end) of the interval
        """
        pl = period.lower()
        rule = None
        if pl == 'quarterly' or pl == 'q':
            rule = 'Q'
        if pl == 'monthly' or pl == 'm':
            rule = 'M'

        return self.daily_share_price_ratios.loc[ticker].resample(rule).last()
