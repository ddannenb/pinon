import pandas as pd
import numpy as np

import names as pn_cols



class Validation:
    def __init__(self, config, derived_bases, comps):
        self.config = config
        self.derived_bases = derived_bases
        self.comps = comps
        self.aroi = None
        self.mu_aroi = None
        self.aroi_scores = None
        self.peer_k_scores = None

    def run_regressions(self):
        # AROI regressions for target tickers, multiple time windows
        for ticker in self.config.get_target_tickers():
            db_slice = self.derived_bases.qtr_derived_bases.loc[ticker]

            for (num_yrs, ar_win, ta_ndx) in pn_cols.AROI_LIST:
                aroi_partial = pd.DataFrame(columns=[pn_cols.TICKER, pn_cols.AROI_WINDOW, pn_cols.AROI_FORWARD], index=db_slice.index)

                if num_yrs > 0:
                    aroi_partial[pn_cols.AROI_FORWARD] = db_slice.loc[:, pn_cols.MU_QTR_PRICE].rolling(num_yrs * 4).apply(self.calc_roi, raw=False, args=(db_slice, ticker, num_yrs)).shift(-num_yrs * 4 + 1)
                else:
                    l = len(aroi_partial)
                    aroi_partial[pn_cols.AROI_FORWARD] = db_slice.loc[:, pn_cols.MU_QTR_PRICE].rolling(l).apply(self.calc_roi, raw=False, args=(db_slice, ticker, l / 4)).shift(-l + 1)

                aroi_partial[pn_cols.TICKER] = ticker
                aroi_partial[pn_cols.AROI_WINDOW] = ar_win

                # Combine the tickers
                self.aroi = aroi_partial if self.aroi is None else pd.concat([self.aroi, aroi_partial])

       # Reindex and sort
        self.aroi.reset_index(inplace=True)
        self.aroi.set_index([pn_cols.TICKER, pn_cols.AROI_WINDOW, pn_cols.REPORT_DATE], inplace=True)
        self.aroi.sort_index(inplace=True)
        print('Break')


    def calc_roi(self, mu_price, df, ticker, num_yrs):
        div_return = df.loc[mu_price.index, pn_cols.QTR_DIV].sum()
        p = mu_price.iloc[0]
        g = mu_price.iloc[-1] + div_return - p
        ann_roi = (((p + g)/p)**(1/num_yrs) - 1)
        return ann_roi

    def run_mu_windows(self):
        for ticker in self.config.get_target_tickers():
            # Skip the max years AROI
            for (ars_num_yrs, ar_win, ta_ndx) in [x for x in pn_cols.AROI_LIST if x[0] > 0]:
                for (ta_num_yrs, ta_ndx) in [x for x in pn_cols.TIME_AVG_LIST if x[0] > 0]:
                    aroi_slice = self.aroi.loc[(ticker, ar_win), ([pn_cols.AROI_FORWARD])]
                    aroi_slice.dropna(axis=0, inplace=True)
                    if len(aroi_slice) == 0:
                        break
                    aroi_slice[pn_cols.MU_AROI] = aroi_slice[pn_cols.AROI_FORWARD].rolling(ta_num_yrs * 4).mean()
                    # Better than avg return => 1, Worse than avg return => -1
                    # aroi_slice[pn_cols.AROI_SCORE] = np.where(aroi_slice[pn_cols.AROI_FORWARD] > aroi_slice[pn_cols.MU_AROI], 1, -1)
                    aroi_slice[pn_cols.AROI_SCORE] = np.where(aroi_slice[pn_cols.AROI_FORWARD] > aroi_slice[pn_cols.MU_AROI], 1, np.where(np.isnan(aroi_slice[pn_cols.MU_AROI]), np.nan, -1))
                    aroi_slice[pn_cols.TICKER] = ticker
                    aroi_slice[pn_cols.AROI_WINDOW] = ar_win
                    aroi_slice[pn_cols.TIME_AVG] = ta_ndx
                    self.mu_aroi = aroi_slice if self.mu_aroi is None else pd.concat([self.mu_aroi, aroi_slice])

        # Reindex and sort
        self.mu_aroi.reset_index(inplace=True)
        self.mu_aroi.set_index([pn_cols.TICKER, pn_cols.AROI_WINDOW, pn_cols.TIME_AVG, pn_cols.REPORT_DATE], inplace=True)
        self.mu_aroi.sort_index(inplace=True)

    def run_scores(self):

        for target_ticker in self.config.get_target_tickers():
            # AROI scores
            for (num_yrs, ar_ndx, ta_ndx) in pn_cols.AROI_LIST:
                aroi_sl = self.derived_bases.qtr_derived_bases.loc[(target_ticker,), (ar_ndx)]
                aroi_sl.dropna(axis=0, inplace=True)
                mu_aroi = self.derived_bases.mu_time_bases.loc[(target_ticker, ta_ndx), (pn_cols.MU_AROI)]
                partial_aroi_score = pd.DataFrame(columns=[pn_cols.TICKER, pn_cols.AROI_WINDOW, pn_cols.AROI_SCORE], index=aroi_sl.index)
                # Better than avg return => 1, Worse than avg return => -1
                partial_aroi_score[pn_cols.AROI_SCORE] = np.where(aroi_sl > mu_aroi, 1, -1)
                partial_aroi_score[pn_cols.TICKER] = target_ticker
                partial_aroi_score[pn_cols.AROI_WINDOW] = ar_ndx
                self.aroi_scores = partial_aroi_score if self.aroi_scores is None else pd.concat([self.aroi_scores, partial_aroi_score])

            # Peer K scores
            for peer_ticker in self.config.get_peer_list(target_ticker):
                peer_k_sl = self.comps.all_ks.loc[(target_ticker, peer_ticker), (pn_cols.K_QTR_PE)]
                peer_k_sl.dropna(axis=0, inplace=True)
                for (num_yrs, ta_ndx) in pn_cols.TIME_AVG_LIST:
                    mu_peer_k = self.comps.peer_ks.loc[(target_ticker, peer_ticker, ta_ndx), (pn_cols.K_QTR_PE)]
                    partial_peer_k_score = pd.DataFrame(columns=[pn_cols.TICKER, pn_cols.PEER_TICKER, pn_cols.TIME_AVG, pn_cols.PEER_K_SCORE], index=peer_k_sl.index)
                    # Target under valued compared to peer => 1, overvalued => -1
                    partial_peer_k_score[pn_cols.PEER_K_SCORE] = np.where(peer_k_sl < mu_peer_k, 1, -1)
                    partial_peer_k_score[pn_cols.TICKER] = target_ticker
                    partial_peer_k_score[pn_cols.PEER_TICKER] = peer_ticker
                    partial_peer_k_score[pn_cols.TIME_AVG] = ta_ndx
                    self.peer_k_scores = partial_peer_k_score if self.peer_k_scores is None else pd.concat([self.peer_k_scores, partial_peer_k_score])

        self.aroi_scores.reset_index(inplace=True)
        self.aroi_scores.set_index([pn_cols.TICKER, pn_cols.AROI_WINDOW, pn_cols.REPORT_DATE], inplace=True)
        self.aroi_scores.sort_index(inplace=True)

        self.peer_k_scores.reset_index(inplace=True)
        self.peer_k_scores.set_index([pn_cols.TICKER, pn_cols.PEER_TICKER, pn_cols.TIME_AVG, pn_cols.REPORT_DATE], inplace=True)
        self.peer_k_scores.sort_index(inplace=True)

        print('Here')