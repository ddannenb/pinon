import pandas as pd
import numpy as np
import simfin.names as sf_cols

import names as pn_cols
from daily_prices import DailyPrices
from fundamentals import Fundamentals
class Multiples:
    def __init__(self, ticker, config):
        self.ticker = ticker
        self.config = config
        self.multiples = None
        self.mu_multiples = None
        self.daily_prices = DailyPrices()
        self.fundamentals = Fundamentals()
        self.breaking_report = None
        self.breaking_report_date = None

    def run_multiples(self):
        self.init_dataframe()
        self.calc_quarterly_pe()
        # TODO call other ratio methods here
        return self.multiples

    def init_dataframe(self):
        inc = self.fundamentals.get_quarterly_income_statement(self.ticker)
        dp = self.daily_prices.get_downsampled_prices(self.ticker)
        ndx = dp.index.intersection(inc.index)
        # TODO limit results to length of financials or num_years_requested
        df = pd.DataFrame(index=ndx)

        # Breaking reports available
        if self.ticker in self.config.breaking_reports.index:
            upcoming_qtr = ndx[-1] + pd.tseries.offsets.QuarterEnd()
            breaking_report = self.config.breaking_reports.loc[self.ticker]
            if upcoming_qtr in breaking_report.index and upcoming_qtr in dp.index:
                df = pd.concat([df, pd.DataFrame(index=pd.Index([upcoming_qtr]))])
                self.breaking_report = breaking_report
                self.breaking_report_date = upcoming_qtr
                print(f"Adding breaking report for ticker {self.ticker} for report date {upcoming_qtr.strftime('%Y-%m-%d')}")

        self.multiples = df

    def calc_quarterly_pe(self):

        new_cols = [pn_cols.QTR_EPS, pn_cols.TTM_QTR_EPS, pn_cols.QTR_PE_RATIO, pn_cols.TTM_QTR_PE_RATIO]
        if not set(new_cols).issubset(self.multiples.columns):
            self.multiples = pd.concat([self.multiples, pd.DataFrame(index=self.multiples.index, columns=new_cols)], axis=1)
        inc = self.fundamentals.get_quarterly_income_statement(self.ticker)
        dp = self.daily_prices.get_downsampled_prices(self.ticker)
        # TODO limit results to length of financials or num_years_requested

        self.multiples[pn_cols.QTR_EPS] = inc[sf_cols.NET_INCOME] / inc[sf_cols.SHARES_DILUTED]
        if self.breaking_report is not None:
            self.multiples.loc[self.breaking_report_date, pn_cols.QTR_EPS] = self.breaking_report.loc[self.breaking_report_date, pn_cols.EPS_BREAKING]
        self.multiples[pn_cols.TTM_QTR_EPS] = self.multiples[pn_cols.QTR_EPS].rolling(4).sum()
        self.multiples[pn_cols.QTR_PE_RATIO] = dp[sf_cols.CLOSE] / self.multiples[pn_cols.QTR_EPS]
        self.multiples[pn_cols.TTM_QTR_PE_RATIO] = dp[sf_cols.CLOSE] / self.multiples[pn_cols.TTM_QTR_EPS]
        self.multiples.index.name = sf_cols.REPORT_DATE

        return self.multiples

    def run_mu_multiples(self):
        if self.multiples is None:
            self.run_multiples()

        self.mu_multiples = pd.DataFrame(columns=[pn_cols.MU_QTR_PE_RATIO, pn_cols.MU_TTM_QTR_PE_RATIO], index=['0 year', '1 year','3 year', '5 year'])
        self.mu_multiples.index.name = pn_cols.MU_NUM_YEARS

        self.mu_multiples.loc['0 year'] = [self.multiples.loc[:, pn_cols.QTR_PE_RATIO].tail(1).mean() / 4, self.multiples.loc[:, pn_cols.TTM_QTR_PE_RATIO].tail(1).mean()]
        self.mu_multiples.loc['1 year'] = np.nan if self.multiples.shape[0] < 4 else [self.multiples.loc[:, pn_cols.QTR_PE_RATIO].tail(4).mean() / 4, self.multiples.loc[:, pn_cols.TTM_QTR_PE_RATIO].tail(4).mean()]
        self.mu_multiples.loc['3 year'] = np.nan if self.multiples.shape[0] < 12 else [self.multiples.loc[:, pn_cols.QTR_PE_RATIO].tail(12).mean() / 4, self.multiples.loc[:, pn_cols.TTM_QTR_PE_RATIO].tail(12).mean()]
        self.mu_multiples.loc['5 year'] = np.nan if self.multiples.shape[0] < 20 else [self.multiples.loc[:, pn_cols.QTR_PE_RATIO].tail(20).mean() / 4, self.multiples.loc[:, pn_cols.TTM_QTR_PE_RATIO].tail(20).mean()]

    def calc_present_fv(self):
        if self.mu_multiples is None:
            self.run_mu_multiples()



