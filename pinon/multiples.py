import pandas as pd
import numpy as np
import simfin.names as sf_cols

import names as pn_cols
from daily_prices import DailyPrices
from fundamentals import Fundamentals

class Multiples:
    def __init__(self, config):
        self.PE_COLS = [pn_cols.QTR_EPS, pn_cols.TTM_EPS, pn_cols.QTR_REV, pn_cols.TTM_REV, pn_cols.QTR_DIV, pn_cols.TTM_DIV, pn_cols.QTR_PE_RATIO, pn_cols.TTM_PE_RATIO]
        self.config = config
        self.qtr_derived_bases = None
        self.mu_price_ratios = None
        self.daily_prices = DailyPrices()
        self.fundamentals = Fundamentals()

    def run_price_ratios(self):
        self.run_qtr_derived()
        self.calc_quarterly_pe()
        # TODO additional multiple calc go here
        self.run_mu_price_ratios()
        return self.qtr_derived_bases

    def run_qtr_derived(self):

        DF_COLS = [pn_cols.TICKER, pn_cols.QTR_EPS, pn_cols.TTM_EPS, pn_cols.QTR_REV, pn_cols.TTM_REV, pn_cols.QTR_DIV,
                   pn_cols.TTM_DIV, pn_cols.QTR_PE_RATIO, pn_cols.TTM_PE_RATIO, pn_cols.MU_QTR_PRICE, pn_cols.BREAKING_EMPLOYED]

        self.qtr_derived_bases = None

        for ticker in self.config.companies.index:
            inc = self.fundamentals.get_quarterly_income_statement(ticker)
            dp = self.daily_prices.get_downsampled_prices(ticker)
            ndx = dp.index.intersection(inc.index)

            # Limit data to number of years requested
            past_qtrs = self.config.companies.loc[ticker, pn_cols.PAST_YEARS_REQUESTED] * 4
            s_ndx = len(ndx) - past_qtrs if len(ndx) > past_qtrs else 0
            ndx = ndx.take([*range(s_ndx, len(ndx))])





            # Breaking reports
            # if ticker in self.config.breaking_reports.index:
            #     upcoming_qtr = ndx[-1] + pd.tseries.offsets.QuarterEnd()
            #     breaking_report = self.config.breaking_reports.loc[ticker]
            #     if upcoming_qtr in breaking_report.index and upcoming_qtr in dp.index:
            #         ndx = ndx.append(pd.Index([upcoming_qtr]))
            #         # TODO Not clear that breaking report is being added, just the index??
            #         # df = pd.concat([df, pd.DataFrame(index=pd.Index([upcoming_qtr]))])
            #         self.config.breaking_reports.at[(ticker, upcoming_qtr), pn_cols.BREAKING_EMPLOYED] = True
            #         print(f"Adding breaking report for ticker {ticker} for report date {upcoming_qtr.strftime('%Y-%m-%d')}")

            df = pd.DataFrame(index=ndx, columns=DF_COLS)

            # Reference data
            df.index.name = pn_cols.REPORT_DATE
            df[pn_cols.TICKER] = ticker
            df[pn_cols.BREAKING_EMPLOYED] = False
            df[pn_cols.QTR_DIV] = dp[sf_cols.DIVIDENDS]
            df[pn_cols.QTR_REV] = inc[sf_cols.REVENUE]
            df[pn_cols.QTR_EPS] = inc[sf_cols.NET_INCOME] / inc[sf_cols.SHARES_DILUTED]
            df[pn_cols.MU_QTR_PRICE] = dp[sf_cols.CLOSE]

            # Breaking reports - NEW
            upcoming_qtr = df.index[-1] + pd.tseries.offsets.QuarterEnd()
            # Note: ndx is intersection of dp and inc indexes. To use the breaking report, must have downsampled price for the quarter but no the published reports
            if upcoming_qtr not in ndx and upcoming_qtr in dp.index:
                br = self.config.get_breaking_report(ticker, upcoming_qtr)
                if br is not None:
                    # ndx = ndx.append(pd.Index([upcoming_qtr]))
                    # df.index = df.index.append(pd.Index([upcoming_qtr]))
                    # df.set_index(ndx)
                    df = pd.concat([df, pd.DataFrame(index=pd.Index([upcoming_qtr]))])
                    df.loc[upcoming_qtr, [pn_cols.QTR_EPS, pn_cols.QTR_REV, pn_cols.QTR_DIV, pn_cols.BREAKING_EMPLOYED]]\
                        = br.loc[upcoming_qtr, [pn_cols.EPS_BREAKING, pn_cols.REVENUE_BREAKING, pn_cols.DIV_BREAKING, pn_cols.BREAKING_EMPLOYED]].to_list()

            # ROI and ROI score
            # for (num_yrs, roi_ndx) in pn_cols.ROI_LIST:
            #     if num_yrs > 0:
            #         s = df.loc[]
            #         s = self.multiples.qtr_derived_bases.loc[(peer_ticker,), pn_cols.MU_QTR_PRICE].rolling(
            #             num_yrs * 4).apply(self.calc_roi, raw=False, args=(peer_ticker, num_yrs)).shift(
            #             -num_yrs * 4 - 1)
            #     else:
            #         l = len(self.multiples.qtr_derived_bases.loc[(peer_ticker,)])
            #         s = self.multiples.qtr_derived_bases.loc[(peer_ticker,), pn_cols.MU_QTR_PRICE].rolling(l).apply(
            #             self.calc_roi, raw=False, args=(peer_ticker, l / 4)).shift(-l + 1)
            #
            #     peer_val.loc[(peer_ticker,), (roi_ndx,)] = s.values

            self.qtr_derived_bases = df if self.qtr_derived_bases is None else pd.concat([self.qtr_derived_bases, df])

        self.qtr_derived_bases.reset_index(inplace=True)
        self.qtr_derived_bases.set_index([pn_cols.TICKER, pn_cols.REPORT_DATE], inplace=True)
        self.qtr_derived_bases.sort_index(inplace=True)

    def calc_quarterly_pe(self):
        for ticker in self.config.companies.index:
            inc = self.fundamentals.get_quarterly_income_statement(ticker)
            dp = self.daily_prices.get_downsampled_prices(ticker)
            pe = pd.DataFrame(index=self.qtr_derived_bases.loc[ticker].index, columns=self.PE_COLS)

            # pe[pn_cols.QTR_EPS] = inc[sf_cols.NET_INCOME] / inc[sf_cols.SHARES_DILUTED]
            # pe[pn_cols.QTR_REV] = inc[sf_cols.REVENUE]
            # pe[pn_cols.QTR_DIV] = dp[sf_cols.DIVIDENDS]
            br = self.config.get_breaking_report(ticker)
            if br is not None:
                pe.loc[(br[pn_cols.REPORT_DATE]), pn_cols.QTR_EPS] = br[pn_cols.EPS_BREAKING]
                pe.loc[(br[pn_cols.REPORT_DATE]), pn_cols.QTR_REV] = br[pn_cols.REVENUE_BREAKING]
                # TODO - add dividends to breaking reports

            pe[pn_cols.TTM_EPS] = pe[pn_cols.QTR_EPS].rolling(4).sum()
            pe[pn_cols.TTM_REV] = pe[pn_cols.QTR_REV].rolling(4).sum()
            pe[pn_cols.TTM_DIV] = pe[pn_cols.QTR_DIV].rolling(4).sum()
            pe[pn_cols.QTR_PE_RATIO] = dp[sf_cols.CLOSE] / pe[pn_cols.QTR_EPS] / 4
            pe[pn_cols.TTM_PE_RATIO] = dp[sf_cols.CLOSE] / pe[pn_cols.TTM_EPS]

            self.qtr_derived_bases.loc[(ticker,), self.PE_COLS] = pe.values

    def run_mu_price_ratios(self):
        self.mu_price_ratios = None

        if self.qtr_derived_bases is None:
            self.run_price_ratios()

        for ticker in self.config.companies.index:
            mm = pd.DataFrame(columns=[pn_cols.TICKER, pn_cols.MU_QTR_PE_RATIO, pn_cols.MU_TTM_PE_RATIO], index=pd.Index([t[1] for t in pn_cols.TIME_AVG_LIST]))
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

            mm.loc[:, pn_cols.TICKER] = ticker
            self.mu_price_ratios = mm if self.mu_price_ratios is None else pd.concat([self.mu_price_ratios, mm])

        self.mu_price_ratios.reset_index(inplace=True)
        self.mu_price_ratios.set_index([pn_cols.TICKER, pn_cols.TIME_AVG], inplace=True)
        self.mu_price_ratios.sort_index(inplace=True)