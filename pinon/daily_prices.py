import pandas as pd
import simfin_global_cache as sfc

class DailyPrices:
    def __init__(self):
        self.daily_prices = sfc._load_daily_share_prices()

    def get_daily_prices(self, tickers):
        return self.daily_prices.loc[tickers]

    def downsample_prices(self, ticker, period='quarterly'):
        """
         Returns prices downsampled to quarterly mean. The quarterly date index represents the right side fo the interval
        """
        pl = period.lower()
        rule = None
        if pl == 'quarterly' or pl == 'q':
            rule = 'Q'
        if pl == 'monthly' or pl == 'm':
            rule = 'M'

        return self.daily_prices.loc[ticker].resample(rule).mean()
