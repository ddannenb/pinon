import pandas as pd
import simfin.names as sf_cols

import names as pn_cols
from daily_prices import DailyPrices
from fundamentals import Fundamentals
class TradingRatios:
    def __init__(self, config):
        self.config = config
        self.ratios = None
        self.daily_prices = DailyPrices()
        self.fundamentals = Fundamentals()
    def calc_quarterly_pe(self, ticker):

        inc = self.fundamentals.get_quarterly_income_statement(ticker)
        dp = self.daily_prices.get_downsampled_prices(ticker)
        # TODO limit results to length of financials or num_years_requested
        pe_ndx = dp.index.intersection(inc.index)
        re_inc = inc.reindex(pe_ndx)
        re_dp = dp.reindex(pe_ndx)
        pe = pd.DataFrame(index=pe_ndx, columns=[pn_cols.QTR_EPS, pn_cols.TTM_EPS, pn_cols.QTR_PE_RATIO, pn_cols.TTM_PE_RATIO])
        pe[pn_cols.QTR_EPS] = re_inc[sf_cols.NET_INCOME] / re_inc[sf_cols.SHARES_DILUTED]
        pe[pn_cols.TTM_EPS] = pe[pn_cols.QTR_EPS].rolling(4).sum()
        pe[pn_cols.QTR_PE_RATIO] = re_dp[sf_cols.CLOSE] / pe[pn_cols.QTR_EPS]
        pe[pn_cols.TTM_PE_RATIO] = re_dp[sf_cols.CLOSE] / pe[pn_cols.TTM_EPS]

        return pe
