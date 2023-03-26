import pandas as pd

import pinon as pn
import names as pn_cols

class Comps:
    def __init__(self, config):
        self.config = config
        self.comp_ratios = None

    def run_comps(self):
        all_ratios = None
        for ticker in self.config.companies.index:
            m = pn.Multiples(ticker, self.config)
            ratios = m.run_multiples()
            ratios[pn_cols.TICKER] = ticker
            all_ratios = ratios if all_ratios is None else pd.concat([all_ratios, ratios])

        all_ratios.reset_index(inplace=True)
        all_ratios.set_index([pn_cols.TICKER, pn_cols.REPORT_DATE], inplace=True)
        print('Here')


