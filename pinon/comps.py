import pandas as pd

import pinon as pn
import names as pn_cols

class Comps:
    def __init__(self, config):
        self.config = config
        self.all_ks = None
        self.peer_ks = None
        self.target_ks = None
        self.multiples = None
        self.comp_ratios = None
        self.m = pn.Multiples(config)

    def run(self):
        self.run_variations()
        self.run_peer_ks()
        self.run_target_ks()
        self.calc_present_comp_ratios()

    def run_variations(self):
        if self.multiples is None:
            self.multiples = self.m.run_multiples()

        self.all_ks = None
        for target_ticker, company in self.config.companies.iterrows():
            if company[pn_cols.EVALUATE]:
                peer_list = company[pn_cols.PEER_LIST]
                target_multiples = self.multiples.loc[target_ticker]
                for peer_ticker in peer_list:
                    peer_multiples = self.multiples.loc[peer_ticker]
                    k_pe = pd.DataFrame(columns=[pn_cols.TARGET_TICKER, pn_cols.PEER_TICKER, pn_cols.K_QTR_PE, pn_cols.K_TTM_PE])
                    k_pe.loc[:, pn_cols.K_TTM_PE] = target_multiples[pn_cols.TTM_PE_RATIO] / peer_multiples[pn_cols.TTM_PE_RATIO]
                    k_pe.loc[:, pn_cols.K_QTR_PE] = target_multiples[pn_cols.QTR_PE_RATIO] / peer_multiples[pn_cols.QTR_PE_RATIO]
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
                peer_k = pd.DataFrame(columns=[pn_cols.TARGET_TICKER, pn_cols.PEER_TICKER, pn_cols.K_PEER_QTR_PE, pn_cols.K_PEER_TTM_PE, pn_cols.K_PEER_WEIGHT])
                k_peer_qtr_pe = peer_ks[pn_cols.K_QTR_PE].mean()
                k_peer_ttm_qtr_pe = peer_ks[pn_cols.K_TTM_PE].mean()

                k_peer_weight = self.config.companies.loc[peer_ticker][pn_cols.PEER_WEIGHT] / sum_peer_weights
                peer_k.loc[len(peer_k.index)] = [target_ticker, peer_ticker, k_peer_qtr_pe, k_peer_ttm_qtr_pe, k_peer_weight]

                self.peer_ks = peer_k if self.peer_ks is None else pd.concat([self.peer_ks, peer_k])
        self.peer_ks.reset_index(inplace=True, drop=True)
        self.peer_ks.set_index([pn_cols.TARGET_TICKER, pn_cols.PEER_TICKER], inplace=True)

    def run_target_ks(self):
        self.target_ks = None
        if self.peer_ks is None:
            self.run_peer_ks()

        for target_ticker, peer_ks in self.peer_ks.groupby(level=pn_cols.TARGET_TICKER):
            target_k = pd.DataFrame(columns=[pn_cols.TARGET_TICKER, pn_cols.K_TARGET_QTR_PE, pn_cols.K_TARGET_TTM_PE])
            k_target_qtr_pe = (peer_ks[pn_cols.K_PEER_QTR_PE] * peer_ks[pn_cols.K_PEER_WEIGHT]).sum()
            k_target_qtr_ttm_pe = (peer_ks[pn_cols.K_PEER_TTM_PE] * peer_ks[pn_cols.K_PEER_WEIGHT]).sum()
            target_k.loc[len(target_k.index)] = [target_ticker, k_target_qtr_pe, k_target_qtr_ttm_pe]
            self.target_ks = target_k if self.target_ks is None else pd.concat([self.target_ks, target_k])
        self.target_ks.reset_index(inplace=True, drop=True)
        self.target_ks.set_index([pn_cols.TARGET_TICKER], inplace=True)

    def calc_present_comp_ratios(self):
        ndx = pd.MultiIndex.from_product([self.target_ks.index.to_list(), pn_cols.YEAR_ROLLUP_LIST])
        ndx.names = [pn_cols.TARGET_TICKER, pn_cols.MU_NUM_YEARS]
        colx = pd.MultiIndex.from_product([[pn_cols.WTD_RATIOS, pn_cols.WTD_ADJ_RATIOS], [pn_cols.QTR_PE_RATIO, pn_cols.TTM_PE_RATIO]])
        self.comp_ratios = pd.DataFrame(columns=colx, index=ndx)
        for target_ticker in self.target_ks.index:
            self.comp_ratios.loc[(target_ticker, pn_cols.WTD_RATIOS)] = 1
            temp = self.m.mu_multiples.loc[target_ticker]
            temp2 = self.comp_ratios.loc[self.comp_ratios.index.get_level_values(0).isin(self.config.companies.loc[target_ticker, pn_cols.PEER_LIST])]
            print('Here')


    def calc_fair_value(self):
        if self.mu_multiples is None:
            self.run_mu_multiples()


