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
        pe = pd.DataFrame(index=pe_ndx, columns=[pn_cols.QTR_EPS, pn_cols.TTM_QTR_EPS, pn_cols.QTR_PE_RATIO, pn_cols.TTM_QTR_PE_RATIO])
        pe[pn_cols.QTR_EPS] = inc[sf_cols.NET_INCOME] / inc[sf_cols.SHARES_DILUTED]
        # Add EPS for any late breaking reports
        if ticker in self.config.breaking_reports.index:
            breaking_qtr = dp.index[-1]
            upcoming_qtr = pe.index[-1] + pd.tseries.offsets.QuarterEnd()
            breaking_report = self.config.breaking_reports.loc[ticker]
            if upcoming_qtr in breaking_report.index and upcoming_qtr in dp.index:
                pe = pd.concat([pe, pd.DataFrame(index=pd.Index([upcoming_qtr]))])
                pe.loc[upcoming_qtr, pn_cols.QTR_EPS] = breaking_report.loc[upcoming_qtr, pn_cols.EPS_BREAKING]
                print(f"Adding breaking report for ticker {ticker} for report date {upcoming_qtr}")


        pe[pn_cols.TTM_QTR_EPS] = pe[pn_cols.QTR_EPS].rolling(4).sum()
        pe[pn_cols.QTR_PE_RATIO] = dp[sf_cols.CLOSE] / pe[pn_cols.QTR_EPS]
        pe[pn_cols.TTM_QTR_PE_RATIO] = dp[sf_cols.CLOSE] / pe[pn_cols.TTM_QTR_EPS]

        return pe
