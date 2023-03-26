import names as pn_cols

class Comps:
    def __init__(self, config):
        self.config = config
        self.comp_ratios = None

    def run_comps(self, config):
        for ticker in self.config.companies.loc[:, pn_cols.TICKER]:
            print(ticker)
