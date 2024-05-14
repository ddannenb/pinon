import pandas as pd
import numpy as np

import names as pn_cols



class Validation:
    def __init__(self, config, derived_bases, comps):
        self.config = config
        self.derived_bases = derived_bases
        self.comps = comps
        self.aroi_scores = None
        self.peer_k_scores = None

    def run_aroi_scores(self):

        for target_ticker in self.config.get_target_tickers():
            # AROI scores
            for (num_yrs, ar_ndx, ta_ndx) in pn_cols.AROI_LIST:
                aroi_sl = self.derived_bases.qtr_derived_bases.loc[(target_ticker,), (ar_ndx)]
                aroi_sl.dropna(axis=0, inplace=True)
                mu_aroi = self.derived_bases.mu_time_bases.loc[(target_ticker, ta_ndx), (pn_cols.MU_AROI)]
                partial_aroi_score = pd.DataFrame(columns=[pn_cols.TICKER, pn_cols.AROI_WINDOW, pn_cols.AROI_SCORE], index=aroi_sl.index)
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