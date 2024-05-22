import pandas as pd
import numpy as np
from scipy import stats

import config
import names as pn_cols



class Validation:
    def __init__(self, config, derived_bases, comps):
        self.config = config
        self.derived_bases = derived_bases
        self.comps = comps
        self.aroi_regression = None
        self.aroi_scores = None
        self.peer_k_scores = None

    def run_aroi_regressions(self):
        # AROI regressions for target tickers, multiple time windows
        for ticker in self.config.get_target_tickers():
            db_slice = self.derived_bases.qtr_derived_bases.loc[ticker]

            for (num_yrs, ar_win, z) in pn_cols.AROI_LIST:
                aroi_partial = pd.DataFrame(columns=[pn_cols.TICKER, pn_cols.AROI_WINDOW, pn_cols.AROI_FORWARD], index=db_slice.index)

                if num_yrs > 0:
                    aroi_partial[pn_cols.AROI_FORWARD] = db_slice.loc[:, pn_cols.MU_QTR_PRICE].rolling(num_yrs * 4).apply(self.calc_aroi, raw=False, args=(db_slice, ticker, num_yrs)).shift(-num_yrs * 4 + 1)
                else:
                    l = len(aroi_partial)
                    aroi_partial[pn_cols.AROI_FORWARD] = db_slice.loc[:, pn_cols.MU_QTR_PRICE].rolling(l).apply(self.calc_aroi, raw=False, args=(db_slice, ticker, l / 4)).shift(-l + 1)

                aroi_partial[pn_cols.TICKER] = ticker
                aroi_partial[pn_cols.AROI_WINDOW] = ar_win

                # Combine the tickers
                self.aroi_regression = aroi_partial if self.aroi_regression is None else pd.concat([self.aroi_regression, aroi_partial])

       # Reindex and sort
        self.aroi_regression.reset_index(inplace=True)
        self.aroi_regression.set_index([pn_cols.TICKER, pn_cols.AROI_WINDOW, pn_cols.REPORT_DATE], inplace=True)
        self.aroi_regression.sort_index(inplace=True)
        print('Break')


    def calc_aroi(self, mu_price, df, ticker, num_yrs):
        div_return = df.loc[mu_price.index, pn_cols.QTR_DIV].sum()
        p = mu_price.iloc[0]
        g = mu_price.iloc[-1] + div_return - p
        ann_roi = (((p + g)/p)**(1/num_yrs) - 1)
        return ann_roi

    def run_aroi_scores(self):
        for target_ticker in self.config.get_target_tickers():
            # Skip the max years AROI
            for (ars_num_yrs, ar_win, z) in [x for x in pn_cols.AROI_LIST if x[0] > 0]:
                # Skip the 0 year time average
                for (ta_num_yrs, ta_ndx) in [x for x in pn_cols.TIME_AVG_LIST if x[0] > 0]:
                    aroi_slice = self.aroi_regression.loc[(target_ticker, ar_win), ([pn_cols.AROI_FORWARD])]
                    aroi_slice.dropna(axis=0, inplace=True)
                    if len(aroi_slice) == 0:
                        break
                    aroi_slice[pn_cols.MU_AROI] = aroi_slice[pn_cols.AROI_FORWARD].rolling(ta_num_yrs * 4).mean()
                    # Better than avg return => 1, Worse than avg return => -1
                    aroi_slice[pn_cols.AROI_SCORE] = np.where(aroi_slice[pn_cols.AROI_FORWARD] > aroi_slice[pn_cols.MU_AROI], 1, np.where(np.isnan(aroi_slice[pn_cols.MU_AROI]), np.nan, -1))
                    aroi_slice[pn_cols.TICKER] = target_ticker
                    aroi_slice[pn_cols.AROI_WINDOW] = ar_win
                    aroi_slice[pn_cols.TIME_AVG] = ta_ndx
                    self.aroi_scores = aroi_slice if self.aroi_scores is None else pd.concat([self.aroi_scores, aroi_slice])

        # Reindex and sort
        self.aroi_scores.reset_index(inplace=True)
        self.aroi_scores.set_index([pn_cols.TICKER, pn_cols.AROI_WINDOW, pn_cols.TIME_AVG, pn_cols.REPORT_DATE], inplace=True)
        self.aroi_scores.sort_index(inplace=True)

    def run_peer_k_scores(self):
        for target_ticker in self.config.get_target_tickers():
            for peer_ticker in self.config.get_peer_list(target_ticker):
                # Skip the 0 year time average
                for (ta_num_yrs, ta_ndx) in [x for x in pn_cols.TIME_AVG_LIST if x[0] > 0]:
                    k_qtr_pe_slice = self.comps.all_ks.loc[(target_ticker, peer_ticker), ([pn_cols.K_QTR_PE])]
                    k_qtr_pe_slice.dropna(axis=0, inplace=True)
                    if len(k_qtr_pe_slice) == 0:
                        break
                    # Drop outliers
                    m = np.abs(stats.zscore((k_qtr_pe_slice[pn_cols.K_QTR_PE] *10000).astype('int'))) <= 2.0
                    k_qtr_pe_slice = k_qtr_pe_slice[m]
                    k_qtr_pe_slice[pn_cols.MU_K_QTR_PE] = k_qtr_pe_slice[pn_cols.K_QTR_PE].rolling(ta_num_yrs * 4).mean()
                    # Target under valued compared to peer => 1, overvalued => -1
                    k_qtr_pe_slice[pn_cols.PEER_K_SCORE] = np.where(k_qtr_pe_slice[pn_cols.K_QTR_PE] < k_qtr_pe_slice[pn_cols.MU_K_QTR_PE], 1, np.where(np.isnan(k_qtr_pe_slice[pn_cols.MU_K_QTR_PE]), np.nan, -1))
                    k_qtr_pe_slice[pn_cols.TICKER] = target_ticker
                    k_qtr_pe_slice[pn_cols.PEER_TICKER] = peer_ticker
                    k_qtr_pe_slice[pn_cols.TIME_AVG] = ta_ndx
                    self.peer_k_scores = k_qtr_pe_slice if self.peer_k_scores is None else pd.concat([self.peer_k_scores, k_qtr_pe_slice])

        # Reindex and sort
        self.peer_k_scores.reset_index(inplace=True)
        self.peer_k_scores.set_index([pn_cols.TICKER, pn_cols.PEER_TICKER, pn_cols.TIME_AVG, pn_cols.REPORT_DATE], inplace=True)
        self.peer_k_scores.sort_index(inplace=True)

        # Peer weighted K scores
        # Iterate and slice by target ticker and time avg
        peer_k_wtd_scores = None
        for target_ticker in self.config.get_target_tickers():
            for (ta_num_yrs, ta_ndx) in [x for x in pn_cols.TIME_AVG_LIST if x[0] > 0]:
                pks_slice = self.peer_k_scores.loc[pd.IndexSlice[target_ticker, :, ta_ndx, :], [pn_cols.K_QTR_PE, pn_cols.MU_K_QTR_PE]]
                # Add weights to k values by peer
                for peer_ticker in self.config.get_peer_list(target_ticker):
                    pks_peer_sl = pd.IndexSlice[target_ticker, peer_ticker, ta_ndx, :]
                    pws = self.config.companies.loc[peer_ticker, pn_cols.PEER_WEIGHT_SCORE]
                    pks_slice.loc[pks_peer_sl, [pn_cols.PEER_WEIGHT_SCORE]] = pws
                    pks_slice.loc[pks_peer_sl, [pn_cols.K_QTR_PE_WTD_EX]] = pws * pks_slice.loc[pks_peer_sl, pn_cols.K_QTR_PE]
                    pks_slice.loc[pks_peer_sl, [pn_cols.MU_K_QTR_PE_WTD_EX]] = pws * pks_slice.loc[pks_peer_sl, pn_cols.MU_K_QTR_PE]

                pks_wtd_slice = pks_slice.groupby(level=pn_cols.REPORT_DATE).sum(min_count=1)

                pks_wtd_slice[pn_cols.K_QTR_PE] = pks_wtd_slice[pn_cols.K_QTR_PE_WTD_EX].div(pks_wtd_slice[pn_cols.PEER_WEIGHT_SCORE])
                pks_wtd_slice[pn_cols.MU_K_QTR_PE] = pks_wtd_slice[pn_cols.MU_K_QTR_PE_WTD_EX].div(pks_wtd_slice[pn_cols.PEER_WEIGHT_SCORE])
                # Target under valued compared to peer => 1, overvalued => -1
                pks_wtd_slice[pn_cols.PEER_K_SCORE] = np.where(pks_wtd_slice[pn_cols.K_QTR_PE] < pks_wtd_slice[pn_cols.MU_K_QTR_PE], 1, np.where(np.isnan(pks_wtd_slice[pn_cols.MU_K_QTR_PE]), np.nan, -1))
                pks_wtd_slice[pn_cols.TICKER] = target_ticker
                pks_wtd_slice[pn_cols.PEER_TICKER] = pn_cols.ALL_PEERS_WTD
                pks_wtd_slice[pn_cols.TIME_AVG] = ta_ndx
                peer_k_wtd_scores = pks_wtd_slice if peer_k_wtd_scores is None else pd.concat([peer_k_wtd_scores, pks_wtd_slice])

        peer_k_wtd_scores.reset_index(inplace=True)
        peer_k_wtd_scores.set_index([pn_cols.TICKER, pn_cols.PEER_TICKER, pn_cols.TIME_AVG, pn_cols.REPORT_DATE], inplace=True)
        peer_k_wtd_scores.sort_index(inplace=True)

        peer_k_wtd_scores.drop([pn_cols.PEER_WEIGHT_SCORE, pn_cols.K_QTR_PE_WTD_EX, pn_cols.MU_K_QTR_PE_WTD_EX], axis=1, inplace=True)
        self.peer_k_scores = pd.concat([self.peer_k_scores, peer_k_wtd_scores])
        self.peer_k_scores.sort_index(inplace=True)
        print('Break')

    def compile_validation_stats(self):
        for target_ticker in self.config.get_target_tickers():
            for (ars_num_yrs, ar_win, z) in [x for x in pn_cols.AROI_LIST if x[0] > 0]:
                for (ta_num_yrs, ta_ndx) in [x for x in pn_cols.TIME_AVG_LIST if x[0] > 0]:
                    ars_sl = self.aroi_scores.loc[(target_ticker, ar_win, ta_ndx), ([pn_cols.AROI_SCORE])]
                    for peer_ticker in [pn_cols.ALL_PEERS_WTD] + self.config.get_peer_list(target_ticker):
                        pks_sl = self.peer_k_scores.loc[(target_ticker, peer_ticker, ta_ndx), ([pn_cols.PEER_K_SCORE])]
                        val_raw = pks_sl[pn_cols.PEER_K_SCORE] + ars_sl[pn_cols.AROI_SCORE]
                        val_raw.dropna(axis=0, inplace=True)
                        val_cnt = len(val_raw)
                        under_val = val_raw[val_raw > 0].count()
                        over_val = val_raw[val_raw < 0].count()

                        if val_cnt > 0:
                            pred_correct = (under_val + over_val) / val_cnt
                            print(f'{pred_correct:.2f}:{over_val}+{under_val}/{val_cnt} correct: {target_ticker}:{peer_ticker} AROI: {ar_win} Time Avg: {ta_ndx}')

