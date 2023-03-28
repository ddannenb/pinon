import pandas as pd

import pinon as pn
import names as pn_cols

class Comps:
    def __init__(self, config):
        self.config = config
        self.comp_ratios = None
        self.all_ratios = None

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
        if self.all_ratios is None:
            self.run_ratios()

        for target_ticker, company in self.config.companies.iterrows():
            if company[pn_cols.EVALUATE]:
                peer_list = company[pn_cols.PEER_LIST]
                target_ratios = self.all_ratios.loc[target_ticker]
                # ndx = pd.MultiIndex.from_product([peer_list, target_ratios.index], names=[pn_cols.TICKER, pn_cols.REPORT_DATE])
                # all_ks = pd.DataFrame(index=ndx, columns=[pn_cols.TICKER, pn_cols. pn_cols.K])
                # all_ks.sort_index()
                all_ks = None
                for peer_ticker in peer_list:
                    peer_ratios = self.all_ratios.loc[peer_ticker]
                    k_pe = pd.DataFrame(columns=[pn_cols.K_QTR_PE, pn_cols.K_TTM_QTR_PE, pn_cols.TICKER])
                    k_pe.loc[:, pn_cols.K_TTM_QTR_PE] = target_ratios[pn_cols.TTM_QTR_PE_RATIO] / peer_ratios[pn_cols.TTM_QTR_PE_RATIO]
                    k_pe.loc[:, pn_cols.K_QTR_PE] = target_ratios[pn_cols.QTR_PE_RATIO] / peer_ratios[pn_cols.QTR_PE_RATIO]
                    k_pe[pn_cols.TICKER] = peer_ticker
                    all_ks = k_pe if all_ks is None else pd.concat([all_ks, k_pe])

                all_ks.reset_index(inplace=True)
                all_ks.set_index([pn_cols.TICKER, pn_cols.REPORT_DATE], inplace=True)
                print('Here')



