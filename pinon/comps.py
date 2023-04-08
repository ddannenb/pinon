import pandas as pd

import pinon as pn
import names as pn_cols

class Comps:
    def __init__(self, config):
        self.config = config
        self.all_ratios = None
        self.all_ks = None
        self.peer_ks = None
        self.target_ks = None

    def run_ratios(self):
        self.all_ratios = None
        for ticker in self.config.companies.index:
            m = pn.Multiples(ticker, self.config)
            ratios = m.run_multiples()
            ratios[pn_cols.TICKER] = ticker
            self.all_ratios = ratios if self.all_ratios is None else pd.concat([self.all_ratios, ratios])

        self.all_ratios.reset_index(inplace=True)
        self.all_ratios.set_index([pn_cols.TICKER, pn_cols.REPORT_DATE], inplace=True)

    def run_variations(self):
        self.all_ks = None
        if self.all_ratios is None:
            self.run_ratios()

        self.all_ks = None
        for target_ticker, company in self.config.companies.iterrows():
            if company[pn_cols.EVALUATE]:
                peer_list = company[pn_cols.PEER_LIST]
                target_ratios = self.all_ratios.loc[target_ticker]
                for peer_ticker in peer_list:
                    peer_ratios = self.all_ratios.loc[peer_ticker]
                    k_pe = pd.DataFrame(columns=[pn_cols.TARGET_TICKER, pn_cols.PEER_TICKER, pn_cols.K_QTR_PE, pn_cols.K_TTM_QTR_PE])
                    k_pe.loc[:, pn_cols.K_TTM_QTR_PE] = target_ratios[pn_cols.TTM_QTR_PE_RATIO] / peer_ratios[pn_cols.TTM_QTR_PE_RATIO]
                    k_pe.loc[:, pn_cols.K_QTR_PE] = target_ratios[pn_cols.QTR_PE_RATIO] / peer_ratios[pn_cols.QTR_PE_RATIO]
                    k_pe[pn_cols.TARGET_TICKER] = target_ticker
                    k_pe[pn_cols.PEER_TICKER] = peer_ticker
                    self.all_ks = k_pe if self.all_ks is None else pd.concat([self.all_ks, k_pe])

        self.all_ks.reset_index(inplace=True)
        self.all_ks.set_index([pn_cols.TARGET_TICKER, pn_cols.PEER_TICKER, pn_cols.REPORT_DATE], inplace=True)

    def run_peer_ks(self):
        self.peer_ks = None
        if self.all_ks is None:
            self.run_variations()

        for target_ticker, target_ks in self.all_ks.groupby(level=pn_cols.TARGET_TICKER):
            m = self.config.companies.index.isin(self.config.companies.loc[target_ticker][pn_cols.PEER_LIST])
            sum_peer_weights = self.config.companies.loc[m][pn_cols.PEER_WEIGHT].sum()
            for peer_ticker, peer_ks in target_ks.groupby(level=pn_cols.PEER_TICKER):
                peer_k = pd.DataFrame(columns=[pn_cols.TARGET_TICKER, pn_cols.PEER_TICKER, pn_cols.K_PEER_QTR_PE, pn_cols.K_PEER_TTM_QTR_PE, pn_cols.K_PEER_WEIGHT])
                k_peer_qtr_pe = peer_ks[pn_cols.K_QTR_PE].mean()
                k_peer_ttm_qtr_pe = peer_ks[pn_cols.K_TTM_QTR_PE].mean()

                k_peer_weight = self.config.companies.loc[peer_ticker][pn_cols.PEER_WEIGHT] / sum_peer_weights
                peer_k.loc[len(peer_k.index)] = [target_ticker, peer_ticker, k_peer_qtr_pe, k_peer_ttm_qtr_pe, k_peer_weight]

                self.peer_ks = peer_k if self.peer_ks is None else pd.concat([self.peer_ks, peer_k])
        self.peer_ks.reset_index(inplace=True, drop=True)
        self.peer_ks.set_index([pn_cols.TARGET_TICKER, pn_cols.PEER_TICKER], inplace=True)
        print('Here')
    def run_target_ks(self):
        self.target_ks = None
        if self.peer_ks is None:
            self.run_peer_ks()

        for target_ticker, peer_ks in self.peer_ks.groupby(level=pn_cols.TARGET_TICKER):
            target_k = pd.DataFrame(columns=[pn_cols.TARGET_TICKER, pn_cols.K_TARGET_QTR_PE, pn_cols.K_TARGET_TTM_QTR_PE])
            k_target_qtr_pe = (peer_ks[pn_cols.K_PEER_QTR_PE] * peer_ks[pn_cols.K_PEER_WEIGHT]).sum()
            k_target_qtr_ttm_pe = (peer_ks[pn_cols.K_PEER_TTM_QTR_PE] * peer_ks[pn_cols.K_PEER_WEIGHT]).sum()
            target_k.loc[len(target_k.index)] = [target_ticker, k_target_qtr_pe, k_target_qtr_ttm_pe]
            self.target_ks = target_k if self.target_ks is None else pd.concat([self.target_ks, target_k])
        self.target_ks.reset_index(inplace=True, drop=True)
        self.target_ks.set_index([pn_cols.TARGET_TICKER])
        print('Here')




