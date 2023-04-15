import pandas as pd
import numpy as np
import simfin.names as sf_cols

import names as pn_cols
from daily_prices import DailyPrices
from fundamentals import Fundamentals
class Multiples:
    def __init__(self, config):
        # self.ticker = ticker
        self.config = config
        self.all_multiples = None
        self.multiples = None
        self.mu_multiples = None
        self.daily_prices = DailyPrices()
        self.fundamentals = Fundamentals()
        self.breaking_report = None
        self.breaking_report_date = None

    def run_multiples(self):
        # self.all_multiples = None
        self.init_multiples()
        for ticker in self.config.companies.index:
            df = self.init_multiples()
            multiples = self.calc_quarterly_pe(ticker, df)
            # TODO additional multiple calc go here
            multiples[pn_cols.TICKER] = ticker
            self.all_multiples = multiples if self.all_multiples is None else pd.concat([self.all_multiples, multiples])

        self.all_multiples.reset_index(inplace=True)
        self.all_multiples.set_index([pn_cols.TICKER, pn_cols.REPORT_DATE], inplace=True)

    def init_multiples(self):
        self.multiples = None

        for ticker in self.config.companies.index:
            inc = self.fundamentals.get_quarterly_income_statement(ticker)
            dp = self.daily_prices.get_downsampled_prices(ticker)
            ndx = dp.index.intersection(inc.index)
            # TODO limit results to length of financials or num_years_requested

            # Breaking reports
            if ticker in self.config.breaking_reports.index:
                upcoming_qtr = ndx[-1] + pd.tseries.offsets.QuarterEnd()
                breaking_report = self.config.breaking_reports.loc[ticker]
                if upcoming_qtr in breaking_report.index and upcoming_qtr in dp.index:
                    ndx = ndx.append(pd.Index([upcoming_qtr]))
                    # df = pd.concat([df, pd.DataFrame(index=pd.Index([upcoming_qtr]))])
                    self.config.breaking_reports.at[(ticker, upcoming_qtr), pn_cols.BREAKING_EMPLOYED] = True
                    print(f"Adding breaking report for ticker {ticker} for report date {upcoming_qtr.strftime('%Y-%m-%d')}")

            pe_cols = [pn_cols.QTR_EPS, pn_cols.TTM_QTR_EPS, pn_cols.QTR_PE_RATIO, pn_cols.TTM_QTR_PE_RATIO]
            df = pd.DataFrame(index=ndx, columns=pe_cols)
            df.index.name = pn_cols.REPORT_DATE
            df[pn_cols.MU_QTR_PRICE] = dp[sf_cols.CLOSE]
            df[pn_cols.TICKER] = ticker
            self.multiples = df if self.multiples is None else pd.concat([self.multiples, df])

        self.multiples.reset_index(inplace=True)
        self.multiples.set_index([pn_cols.TICKER, pn_cols.REPORT_DATE], inplace=True)
        print('Here')

    def calc_quarterly_pe(self, ticker, multiples):
        inc = self.fundamentals.get_quarterly_income_statement(ticker)
        dp = self.daily_prices.get_downsampled_prices(ticker)
        pe_cols = [pn_cols.QTR_EPS, pn_cols.TTM_QTR_EPS, pn_cols.QTR_PE_RATIO, pn_cols.TTM_QTR_PE_RATIO]
        pe = pd.DataFrame(index=self.multiples.loc[ticker].index, columns=pe_cols)

        pe[pn_cols.QTR_EPS] = inc[sf_cols.NET_INCOME] / inc[sf_cols.SHARES_DILUTED]
        br = self.config.get_breaking_report(ticker)
        if br is not None:
            pe.loc[(br[pn_cols.REPORT_DATE]), pn_cols.QTR_EPS] = br[pn_cols.EPS_BREAKING]
        pe[pn_cols.TTM_QTR_EPS] = pe[pn_cols.QTR_EPS].rolling(4).sum()
        pe[pn_cols.QTR_PE_RATIO] = dp[sf_cols.CLOSE] / pe[pn_cols.QTR_EPS] / 4
        pe[pn_cols.TTM_QTR_PE_RATIO] = dp[sf_cols.CLOSE] / pe[pn_cols.TTM_QTR_EPS]

        self.multiples.loc[(ticker, ), pe_cols] = pe.values
        print('HERE')
    def run_mu_multiples(self):
        if self.multiples is None:
            self.run_multiples()

        self.mu_multiples = pd.DataFrame(columns=[pn_cols.MU_QTR_PE_RATIO, pn_cols.MU_TTM_QTR_PE_RATIO], index=['0 year', '1 year','3 year', '5 year'])
        self.mu_multiples.index.name = pn_cols.MU_NUM_YEARS

        self.mu_multiples.loc['0 year'] = [self.multiples.loc[:, pn_cols.QTR_PE_RATIO].tail(1).mean() / 4, self.multiples.loc[:, pn_cols.TTM_QTR_PE_RATIO].tail(1).mean()]
        self.mu_multiples.loc['1 year'] = np.nan if self.multiples.shape[0] < 4 else [self.multiples.loc[:, pn_cols.QTR_PE_RATIO].tail(4).mean() / 4, self.multiples.loc[:, pn_cols.TTM_QTR_PE_RATIO].tail(4).mean()]
        self.mu_multiples.loc['3 year'] = np.nan if self.multiples.shape[0] < 12 else [self.multiples.loc[:, pn_cols.QTR_PE_RATIO].tail(12).mean() / 4, self.multiples.loc[:, pn_cols.TTM_QTR_PE_RATIO].tail(12).mean()]
        self.mu_multiples.loc['5 year'] = np.nan if self.multiples.shape[0] < 20 else [self.multiples.loc[:, pn_cols.QTR_PE_RATIO].tail(20).mean() / 4, self.multiples.loc[:, pn_cols.TTM_QTR_PE_RATIO].tail(20).mean()]

    # TODO
    def calc_present_fv(self):
        if self.mu_multiples is None:
            self.run_mu_multiples()



