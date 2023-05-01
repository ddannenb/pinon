import pandas as pd
import numpy as np
import simfin.names as sf_cols

import names as pn_cols
from daily_prices import DailyPrices
from fundamentals import Fundamentals

PE_COLS = [pn_cols.QTR_EPS, pn_cols.TTM_EPS, pn_cols.QTR_PE_RATIO, pn_cols.TTM_PE_RATIO]
class Multiples:
    def __init__(self, config):
        # self.ticker = ticker
        self.config = config
        self.price_ratios = None
        self.mu_price_ratios = None
        self.daily_prices = DailyPrices()
        self.fundamentals = Fundamentals()

    def run_price_ratios(self):
        self.init_price_ratios()
        self.calc_quarterly_pe()
        # TODO additional multiple calc go here
        self.run_mu_price_ratios()
        return self.price_ratios

    def init_price_ratios(self):
        self.price_ratios = None

        for ticker in self.config.companies.index:
            inc = self.fundamentals.get_quarterly_income_statement(ticker)
            dp = self.daily_prices.get_downsampled_prices(ticker)
            ndx = dp.index.intersection(inc.index)

            # Limit data to number of years requested
            past_qtrs = self.config.companies.loc[ticker, pn_cols.PAST_YEARS_REQUESTED] * 4
            s_ndx = len(ndx) - past_qtrs if len(ndx) > past_qtrs else 0
            ndx = ndx.take([*range(s_ndx, len(ndx))])

            # Breaking reports
            if ticker in self.config.breaking_reports.index:
                upcoming_qtr = ndx[-1] + pd.tseries.offsets.QuarterEnd()
                breaking_report = self.config.breaking_reports.loc[ticker]
                if upcoming_qtr in breaking_report.index and upcoming_qtr in dp.index:
                    ndx = ndx.append(pd.Index([upcoming_qtr]))
                    # df = pd.concat([df, pd.DataFrame(index=pd.Index([upcoming_qtr]))])
                    self.config.breaking_reports.at[(ticker, upcoming_qtr), pn_cols.BREAKING_EMPLOYED] = True
                    print(f"Adding breaking report for ticker {ticker} for report date {upcoming_qtr.strftime('%Y-%m-%d')}")

            df = pd.DataFrame(index=ndx, columns=PE_COLS)
            df.index.name = pn_cols.REPORT_DATE
            df[pn_cols.MU_QTR_PRICE] = dp[sf_cols.CLOSE]
            df[pn_cols.TICKER] = ticker
            self.price_ratios = df if self.price_ratios is None else pd.concat([self.price_ratios, df])

        self.price_ratios.reset_index(inplace=True)
        self.price_ratios.set_index([pn_cols.TICKER, pn_cols.REPORT_DATE], inplace=True)
        self.price_ratios.sort_index(inplace=True)

    def calc_quarterly_pe(self):
        for ticker in self.config.companies.index:
            inc = self.fundamentals.get_quarterly_income_statement(ticker)
            dp = self.daily_prices.get_downsampled_prices(ticker)
            pe = pd.DataFrame(index=self.price_ratios.loc[ticker].index, columns=PE_COLS)

            pe[pn_cols.QTR_EPS] = inc[sf_cols.NET_INCOME] / inc[sf_cols.SHARES_DILUTED]
            br = self.config.get_breaking_report(ticker)
            if br is not None:
                pe.loc[(br[pn_cols.REPORT_DATE]), pn_cols.QTR_EPS] = br[pn_cols.EPS_BREAKING]
            pe[pn_cols.TTM_EPS] = pe[pn_cols.QTR_EPS].rolling(4).sum()
            pe[pn_cols.QTR_PE_RATIO] = dp[sf_cols.CLOSE] / pe[pn_cols.QTR_EPS] / 4
            pe[pn_cols.TTM_PE_RATIO] = dp[sf_cols.CLOSE] / pe[pn_cols.TTM_EPS]

            self.price_ratios.loc[(ticker,), PE_COLS] = pe.values

    def run_mu_price_ratios(self):
        self.mu_price_ratios = None

        if self.price_ratios is None:
            self.run_price_ratios()

        for ticker in self.config.companies.index:
            mm = pd.DataFrame(columns=[pn_cols.TICKER, pn_cols.MU_QTR_PE_RATIO, pn_cols.MU_TTM_PE_RATIO], index=pd.Index([t[1] for t in pn_cols.TIME_AVG_LIST]))
            mm.index.name = pn_cols.TIME_AVG

            mpr = None
            for (num_yrs, ta_ndx) in pn_cols.TIME_AVG_LIST:
                if num_yrs == 0:
                    mpr = [self.price_ratios.loc[(ticker,), pn_cols.QTR_PE_RATIO].tail(1).squeeze(), self.price_ratios.loc[(ticker,), pn_cols.TTM_PE_RATIO].tail(1).squeeze()]

                elif num_yrs == -1:
                    mpr = [self.price_ratios.loc[(ticker,), pn_cols.QTR_PE_RATIO].mean(), self.price_ratios.loc[(ticker,), pn_cols.TTM_PE_RATIO].mean()]

                else:
                    mpr = [self.price_ratios.loc[(ticker,), pn_cols.QTR_PE_RATIO].tail(4*num_yrs).mean(), self.price_ratios.loc[(ticker,), pn_cols.TTM_PE_RATIO].tail(4*num_yrs).mean()]

                mm.loc[ta_ndx, [pn_cols.MU_QTR_PE_RATIO, pn_cols.MU_TTM_PE_RATIO]] = mpr

            mm.loc[:, pn_cols.TICKER] = ticker
            self.mu_price_ratios = mm if self.mu_price_ratios is None else pd.concat([self.mu_price_ratios, mm])

        self.mu_price_ratios.reset_index(inplace=True)
        self.mu_price_ratios.set_index([pn_cols.TICKER, pn_cols.TIME_AVG], inplace=True)
        self.mu_price_ratios.sort_index(inplace=True)