import pandas as pd
import numpy as np
import simfin.names as sf_cols

import names as pn_cols
from daily_prices import DailyPrices
from fundamentals import Fundamentals

class DerivedBases:
    def __init__(self, config):
        self.PE_COLS = [pn_cols.QTR_EPS, pn_cols.TTM_EPS, pn_cols.QTR_REV, pn_cols.TTM_REV, pn_cols.QTR_DIV, pn_cols.TTM_DIV, pn_cols.QTR_PE_RATIO, pn_cols.TTM_PE_RATIO]
        self.config = config
        self.qtr_derived_bases = None
        self.mu_time_bases = None
        self.daily_prices = DailyPrices()
        self.fundamentals = Fundamentals()

    def run_derived_bases(self):
        self.run_qtr_bases()
        self.run_mu_time_bases()
        return self.qtr_derived_bases

    def run_qtr_bases(self):

        DF_COLS = [pn_cols.TICKER, pn_cols.QTR_EPS, pn_cols.TTM_EPS, pn_cols.QTR_REV, pn_cols.TTM_REV, pn_cols.QTR_DIV,
                   pn_cols.TTM_DIV, pn_cols.QTR_PE_RATIO, pn_cols.TTM_PE_RATIO, pn_cols.MU_QTR_PRICE, pn_cols.BREAKING_EMPLOYED] + [ar_ndx for (x, ar_ndx, z) in pn_cols.AROI_LIST]

        self.qtr_derived_bases = None

        for ticker in self.config.companies.index:
            inc = self.fundamentals.get_quarterly_income_statement(ticker)
            dp = self.daily_prices.get_downsampled_prices(ticker)
            ndx = dp.index.intersection(inc.index)
            ndx.name = pn_cols.REPORT_DATE

            # Limit data to number of years requested
            past_qtrs = self.config.companies.loc[ticker, pn_cols.PAST_YEARS_REQUESTED] * 4
            s_ndx = len(ndx) - past_qtrs if len(ndx) > past_qtrs else 0
            ndx = ndx.take([*range(s_ndx, len(ndx))])

            df = pd.DataFrame(index=ndx, columns=DF_COLS)

            # Before Breaking reports so those values don't get overwritten
            df[pn_cols.QTR_EPS] = inc[sf_cols.NET_INCOME] / inc[sf_cols.SHARES_DILUTED]
            df[pn_cols.QTR_DIV] = dp[sf_cols.DIVIDENDS].fillna(0)
            df[pn_cols.QTR_REV] = inc[sf_cols.REVENUE]
            df[pn_cols.BREAKING_EMPLOYED] = df[pn_cols.BREAKING_EMPLOYED].astype(object)
            df[pn_cols.BREAKING_EMPLOYED] = False


            # Breaking reports
            upcoming_qtr = df.index[-1] + pd.tseries.offsets.QuarterEnd()
            # Note: ndx is intersection of dp and inc indexes. To use the breaking report, must have downsampled price for the quarter but not the published reports
            if upcoming_qtr not in ndx and upcoming_qtr in dp.index:
                br = self.config.get_breaking_report(ticker, upcoming_qtr)
                if br is not None:
                    df = pd.concat([df, pd.DataFrame(index=pd.Index([upcoming_qtr], name=pn_cols.REPORT_DATE))])
                    df.loc[upcoming_qtr, [pn_cols.QTR_EPS, pn_cols.QTR_REV, pn_cols.QTR_DIV, pn_cols.BREAKING_EMPLOYED]] \
                        = br.loc[upcoming_qtr, [pn_cols.EPS_BREAKING, pn_cols.REVENUE_BREAKING, pn_cols.DIV_BREAKING,
                                                pn_cols.BREAKING_EMPLOYED]].to_list()

            df[pn_cols.TICKER] = ticker
            df[pn_cols.MU_QTR_PRICE] = dp[sf_cols.CLOSE]

            df[pn_cols.TTM_EPS] = df[pn_cols.QTR_EPS].rolling(4).sum()
            df[pn_cols.TTM_REV] = df[pn_cols.QTR_REV].rolling(4).sum()
            df[pn_cols.TTM_DIV] = df[pn_cols.QTR_DIV].rolling(4).sum()

            # Derived price ratios
            df[pn_cols.QTR_PE_RATIO] = dp[sf_cols.CLOSE] / df[pn_cols.QTR_EPS] / 4
            df[pn_cols.TTM_PE_RATIO] = dp[sf_cols.CLOSE] / df[pn_cols.TTM_EPS]

            # Derived references

            # AROI
            for (num_yrs, ar_ndx, z) in pn_cols.AROI_LIST:
                if num_yrs > 0:
                    # s = df.loc[:, pn_cols.MU_QTR_PRICE].rolling(num_yrs * 4).apply(self.calc_roi, raw=False, args=(df, ticker, num_yrs))
                    s = df.loc[:, pn_cols.MU_QTR_PRICE].rolling(num_yrs * 4).apply(self.calc_roi, raw=False, args=(df, ticker, num_yrs)).shift(-num_yrs * 4 + 1)
                else:
                    l = len(df)
                    s = df.loc[:, pn_cols.MU_QTR_PRICE].rolling(l).apply(self.calc_roi, raw=False, args=(df, ticker, l / 4)).shift(-l + 1)

                df.loc[:, ar_ndx] = s.values

            # Append all of the tickers together
            self.qtr_derived_bases = df if self.qtr_derived_bases is None else pd.concat([self.qtr_derived_bases, df])

        self.qtr_derived_bases.reset_index(inplace=True)
        self.qtr_derived_bases.set_index([pn_cols.TICKER, pn_cols.REPORT_DATE], inplace=True)
        self.qtr_derived_bases.sort_index(inplace=True)

    def calc_roi(self, mu_price, df, ticker, num_yrs):
        div_return = df.loc[mu_price.index, pn_cols.QTR_DIV].sum()
        p = mu_price.iloc[0]
        g = mu_price.iloc[-1] + div_return - p
        ann_roi = (((p + g)/p)**(1/num_yrs) - 1)
        return ann_roi

    def run_mu_time_bases(self):
        self.mu_time_bases = None

        if self.qtr_derived_bases is None:
            self.run_qtr_bases()

        for ticker in self.config.companies.index:
            mm = pd.DataFrame(columns=[pn_cols.TICKER, pn_cols.MU_QTR_PE_RATIO, pn_cols.MU_TTM_PE_RATIO, pn_cols.MU_AROI], index=pd.Index([t[1] for t in pn_cols.TIME_AVG_LIST]))
            mm.index.name = pn_cols.TIME_AVG
            mpr = None

            for (num_yrs, ta_ndx) in pn_cols.TIME_AVG_LIST:
                if num_yrs == 0:
                    mpr = [self.qtr_derived_bases.loc[(ticker,), pn_cols.QTR_PE_RATIO].tail(1).squeeze(), self.qtr_derived_bases.loc[(ticker,), pn_cols.TTM_PE_RATIO].tail(1).squeeze()]

                elif num_yrs == -1:
                    mpr = [self.qtr_derived_bases.loc[(ticker,), pn_cols.QTR_PE_RATIO].mean(), self.qtr_derived_bases.loc[(ticker,), pn_cols.TTM_PE_RATIO].mean()]

                else:
                    mpr = [self.qtr_derived_bases.loc[(ticker,), pn_cols.QTR_PE_RATIO].tail(4 * num_yrs).mean(), self.qtr_derived_bases.loc[(ticker,), pn_cols.TTM_PE_RATIO].tail(4 * num_yrs).mean()]

                mm.loc[ta_ndx, [pn_cols.MU_QTR_PE_RATIO, pn_cols.MU_TTM_PE_RATIO]] = mpr

            # Time averaged Annualized ROI
            # for (num_yrs, ar_ndx, ta_ndx) in pn_cols.AROI_LIST:
            #     ar = self.qtr_derived_bases.loc[(ticker,), ar_ndx].mean()
            #     mm.loc[ta_ndx, [pn_cols.MU_AROI]] = ar

            mm.loc[:, pn_cols.TICKER] = ticker
            self.mu_time_bases = mm if self.mu_time_bases is None else pd.concat([self.mu_time_bases, mm])

        self.mu_time_bases.reset_index(inplace=True)
        self.mu_time_bases.set_index([pn_cols.TICKER, pn_cols.TIME_AVG], inplace=True)
        self.mu_time_bases.sort_index(inplace=True)