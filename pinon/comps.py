import pandas as pd
import numpy as np
from scipy import stats

import pinon as pn
import names as pn_cols
from datetime import date

class Comps:
    def __init__(self, config):
        self.config = config
        self.all_ks = None
        self.peer_ks = None
        self.target_ks = None
        self.comp_ratios = None
        self.fair_value = None
        self.multiples = pn.Multiples(config)

    def run(self):
        self.run_all_ks()
        self.run_peer_ks()
        self.run_target_ks()
        self.calc_present_comp_ratios()

    def run_all_ks(self):
        if self.multiples.price_ratios is None:
            self.multiples.run_price_ratios()

        self.all_ks = None
        for target_ticker in self.config.get_target_tickers():
            peer_list = self.config.get_peer_list(target_ticker)
            target_ratios = self.multiples.price_ratios.loc[target_ticker]
            for peer_ticker in peer_list:
                peer_ratios = self.multiples.price_ratios.loc[peer_ticker]
                k_pe = pd.DataFrame(columns=[pn_cols.TARGET_TICKER, pn_cols.PEER_TICKER, pn_cols.K_QTR_PE, pn_cols.K_TTM_PE])
                k_pe.loc[:, pn_cols.K_TTM_PE] = target_ratios[pn_cols.TTM_PE_RATIO] / peer_ratios[pn_cols.TTM_PE_RATIO]
                k_pe.loc[:, pn_cols.K_QTR_PE] = target_ratios[pn_cols.QTR_PE_RATIO] / peer_ratios[pn_cols.QTR_PE_RATIO]
                k_pe[pn_cols.TARGET_TICKER] = target_ticker
                k_pe[pn_cols.PEER_TICKER] = peer_ticker
                self.all_ks = k_pe if self.all_ks is None else pd.concat([self.all_ks, k_pe])

        self.all_ks.reset_index(inplace=True)
        self.all_ks.set_index([pn_cols.TARGET_TICKER, pn_cols.PEER_TICKER, pn_cols.REPORT_DATE], inplace=True)

    def run_peer_ks(self):
        self.peer_ks = None
        if self.all_ks is None:
            self.run_all_ks()

        for target_ticker in self.config.get_target_tickers():
            target_ks = self.all_ks.loc[target_ticker]
            peer_weights = self.config.get_peer_weights(target_ticker)

            for peer_ticker, peer_ks in target_ks.groupby(level=pn_cols.PEER_TICKER):
                peer_k = pd.DataFrame(index=pd.Index([t[1] for t in pn_cols.TIME_AVG_LIST]), columns=[pn_cols.TARGET_TICKER, pn_cols.PEER_TICKER, pn_cols.K_QTR_PE, pn_cols.K_TTM_PE, pn_cols.PEER_WEIGHTS])
                peer_k.index.name = pn_cols.TIME_AVG
                peer_k[pn_cols.TARGET_TICKER] = target_ticker
                peer_k[pn_cols.PEER_TICKER] = peer_ticker
                peer_k[pn_cols.PEER_WEIGHTS] = peer_weights[peer_ticker]

                # Drop NaN and remove outliers outside of 2.0 sigma
                pks_qtr_pe_no_nans = peer_ks.loc[:, pn_cols.K_QTR_PE].dropna()
                pks_ttm_pe_no_nans = peer_ks.loc[:, pn_cols.K_TTM_PE].dropna()
                m_pks_qtr_pe = np.abs(stats.zscore((pks_qtr_pe_no_nans *10000).astype('int'))) <= 2.0
                m_pks_ttm_pe = np.abs(stats.zscore((pks_ttm_pe_no_nans *10000).astype('int'))) <= 2.0
                pks_qtr_pe_clean = pks_qtr_pe_no_nans[m_pks_qtr_pe]
                pks_ttm_pe_clean = pks_ttm_pe_no_nans[m_pks_ttm_pe]

                for (num_yrs, ta_ndx) in pn_cols.TIME_AVG_LIST:

                    pks = None
                    if num_yrs == 0:
                        # 0 year - use the most recent calculated K value
                        pks = [pks_qtr_pe_clean.tail(1).squeeze(), pks_ttm_pe_clean.tail(1).squeeze()]

                    elif num_yrs == -1:
                        # max years
                        pks = [pks_qtr_pe_clean.mean(), pks_ttm_pe_clean.mean()]

                    else:
                        # range of years
                        end_qtr = pd.to_datetime(date.today()) - pd.tseries.offsets.QuarterEnd()
                        start_qtr = end_qtr - pd.DateOffset(years=num_yrs)
                        m_pks_qtr_pe_range = ((pks_qtr_pe_clean.index.get_level_values(level=pn_cols.REPORT_DATE) > start_qtr) & (pks_qtr_pe_clean.index.get_level_values(level=pn_cols.REPORT_DATE) <= end_qtr))
                        m_pks_ttm_pe_range = ((pks_ttm_pe_clean.index.get_level_values(level=pn_cols.REPORT_DATE) > start_qtr) & (pks_ttm_pe_clean.index.get_level_values(level=pn_cols.REPORT_DATE) <= end_qtr))
                        pks_qtr_pe_clean_range = pks_qtr_pe_clean[m_pks_qtr_pe_range]
                        pks_ttm_pe_clean_range = pks_ttm_pe_clean[m_pks_ttm_pe_range]
                        pks = [pks_qtr_pe_clean_range.mean(), pks_ttm_pe_clean_range.mean()]

                    peer_k.loc[ta_ndx, [pn_cols.K_QTR_PE, pn_cols.K_TTM_PE]] = pks

                self.peer_ks = peer_k if self.peer_ks is None else pd.concat([self.peer_ks, peer_k])

        self.peer_ks.reset_index(inplace=True, drop=False)
        self.peer_ks.set_index([pn_cols.TARGET_TICKER, pn_cols.PEER_TICKER, pn_cols.TIME_AVG], inplace=True)

    def run_target_ks(self):
        self.target_ks = None
        if self.peer_ks is None:
            self.run_peer_ks()

        for target_ticker, peer_ks in self.peer_ks.groupby(level=pn_cols.TARGET_TICKER):
            peer_ks_weighted = peer_ks[[pn_cols.K_QTR_PE, pn_cols.K_TTM_PE]].multiply(peer_ks[pn_cols.PEER_WEIGHTS], axis='index')
            target_k = peer_ks_weighted.groupby(level=pn_cols.TIME_AVG, sort=False).sum()
            target_k[pn_cols.TARGET_TICKER] = target_ticker
            self.target_ks = target_k if self.target_ks is None else pd.concat([self.target_ks, target_k])

        self.target_ks.reset_index(inplace=True, drop=False)
        self.target_ks.set_index([pn_cols.TARGET_TICKER, pn_cols.TIME_AVG], inplace=True)

    def calc_present_comp_ratios(self):
        ndx = pd.MultiIndex.from_product([self.config.get_target_tickers(), [t[1] for t in pn_cols.TIME_AVG_LIST]])
        ndx.names = [pn_cols.TARGET_TICKER, pn_cols.TIME_AVG]
        colx = pd.MultiIndex.from_product([[pn_cols.QTR_PE_RATIO, pn_cols.TTM_PE_RATIO], [pn_cols.TARGET_RATIOS, pn_cols.UN_WTD_RATIOS, pn_cols.WTD_RATIOS, pn_cols.WTD_ADJ_RATIOS]])
        self.comp_ratios = pd.DataFrame(columns=colx, index=ndx)
        self.comp_ratios.sort_index(inplace=True)
        for target_ticker in self.config.get_target_tickers():
            # Note: use the k value obtained from maximum history
            target_k = self.target_ks.loc[(target_ticker, pn_cols.TIME_AVG_MAX_YEAR)]
            crs = self.multiples.mu_price_ratios.loc[self.config.get_peer_list(target_ticker)]
            crs[pn_cols.PEER_WEIGHTS] = pd.Series(crs.index.get_level_values(0)).map(self.config.get_peer_weights(target_ticker)).values

            self.comp_ratios.loc[(target_ticker,), (pn_cols.QTR_PE_RATIO, pn_cols.UN_WTD_RATIOS)] = (crs[pn_cols.MU_QTR_PE_RATIO]).groupby(level=1).mean().values
            self.comp_ratios.loc[(target_ticker,), (pn_cols.QTR_PE_RATIO, pn_cols.WTD_RATIOS)] = (crs[pn_cols.MU_QTR_PE_RATIO] * crs[pn_cols.PEER_WEIGHTS]).groupby(level=1).sum().values
            self.comp_ratios.loc[(target_ticker,), (pn_cols.QTR_PE_RATIO, pn_cols.WTD_ADJ_RATIOS)] = (crs[pn_cols.MU_QTR_PE_RATIO] * crs[pn_cols.PEER_WEIGHTS] * target_k[pn_cols.K_QTR_PE]).groupby(level=1).sum().values
            self.comp_ratios.loc[(target_ticker,), (pn_cols.QTR_PE_RATIO, pn_cols.TARGET_RATIOS)] = self.multiples.mu_price_ratios.loc[(target_ticker, ), pn_cols.MU_QTR_PE_RATIO].values

            self.comp_ratios.loc[(target_ticker,), (pn_cols.TTM_PE_RATIO, pn_cols.UN_WTD_RATIOS)] = (crs[pn_cols.MU_TTM_PE_RATIO]).groupby(level=1).mean().values
            self.comp_ratios.loc[(target_ticker,), (pn_cols.TTM_PE_RATIO, pn_cols.WTD_RATIOS)] = (crs[pn_cols.MU_TTM_PE_RATIO] * crs[pn_cols.PEER_WEIGHTS]).groupby(level=1).sum().values
            self.comp_ratios.loc[(target_ticker,), (pn_cols.TTM_PE_RATIO, pn_cols.WTD_ADJ_RATIOS)] = (crs[pn_cols.MU_TTM_PE_RATIO] * crs[pn_cols.PEER_WEIGHTS] * target_k[pn_cols.K_TTM_PE]).groupby(level=1).sum().values
            self.comp_ratios.loc[(target_ticker,), (pn_cols.TTM_PE_RATIO, pn_cols.TARGET_RATIOS)] = self.multiples.mu_price_ratios.loc[(target_ticker, ), pn_cols.MU_TTM_PE_RATIO].values


    def calc_fair_value(self):
        previous_qtr = pd.to_datetime(date.today()) - pd.tseries.offsets.QuarterEnd()
        ndx = pd.MultiIndex.from_product([self.config.get_target_tickers(), [t[1] for t in pn_cols.TIME_AVG_LIST]])
        ndx.names = [pn_cols.TARGET_TICKER, pn_cols.TIME_AVG]
        future_qtrs = self.config.forecasts.index.unique(level=1)
        cols_ndx = self.config.forecasts.index.unique(level=1).union(pd.Index([previous_qtr]))
        colx = pd.MultiIndex.from_product([[pn_cols.QTR_PE_FV, pn_cols.TTM_PE_FV], cols_ndx])
        self.fair_value = pd.DataFrame(columns=colx, index=ndx)
        self.fair_value.sort_index(inplace=True)

        for target_ticker in self.config.get_target_tickers():
            if previous_qtr in self.multiples.price_ratios.loc[target_ticker].index:
                fv_ttm_pe = self.comp_ratios.loc[(target_ticker,), (pn_cols.TTM_PE_RATIO, pn_cols.WTD_ADJ_RATIOS)]
                fv_qtr_pe = self.comp_ratios.loc[(target_ticker,), (pn_cols.QTR_PE_RATIO, pn_cols.WTD_ADJ_RATIOS)]
                previous_ttm_eps = self.multiples.price_ratios.loc[(target_ticker, previous_qtr), pn_cols.TTM_EPS]
                self.fair_value.loc[(target_ticker, ), (pn_cols.TTM_PE_FV, previous_qtr)] = (previous_ttm_eps * fv_ttm_pe).values
                previous_qtr_eps = self.multiples.price_ratios.loc[(target_ticker, previous_qtr), pn_cols.QTR_EPS]
                self.fair_value.loc[(target_ticker, ), (pn_cols.QTR_PE_FV, previous_qtr)] = (previous_qtr_eps * fv_qtr_pe * 4).values

            for forecast_qtr in future_qtrs:
                print(forecast_qtr)
            # self.fair_value.loc[(target_ticker, ), (pn_cols.QTR_PE_FV, future_qtrs.tolist())] = 2

    print('Break')





