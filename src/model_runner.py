from fundamentals import Fundamentals
import pandas as pd
import global_defs

class ModelRunner:
    def __init__(self):
        self.fundamentals = None
        self.peer_fundamentals = {}
        self.ttm_pe = pd.DataFrame()

    def run_pe_mutiples(self, symbol, peers, num_years):
        # since pe is using a ttm approach, additional 3 qtr reports are fetched
        num_reports = num_years * 4 + 3

        self.fundamentals = Fundamentals(symbol, num_reports)
        self.fundamentals.fetch_all()

        target_ttm_pe = self.calc_ttm_pe(self.fundamentals)
        self.ttm_pe[symbol + '_target_ttm_pe'] = target_ttm_pe["ttm_pe"]

        for k in peers:
            self.peer_fundamentals[k] = Fundamentals(k, num_reports)
            self.peer_fundamentals[k].fetch_all()

            peer_ttm_pe = self.calc_ttm_pe(self.peer_fundamentals[k])
            self.ttm_pe[k + '_peer_ttm_pe'] = peer_ttm_pe['ttm_pe']
            self.ttm_pe[k + '_peer_delta_pe'] = (self.ttm_pe[k + '_peer_ttm_pe'] / self.ttm_pe[symbol + '_target_ttm_pe']) - 1


    def read_excel_config(self):
        master_config = pd.read_excel(global_defs.get_config_file_path())
        print(master_config)

    def calc_ttm_pe(self, fundamentals):
        ttm_pe_ratios = pd.DataFrame(index=range(fundamentals.num_qtr_reports-3), columns=["ttm_pe", "ttm_eps", "avg_market_price"])
        for n_qtr in range(fundamentals.num_qtr_reports-3):
            ttm_eps = fundamentals.income_statements.iloc[n_qtr:n_qtr+4]["eps"].sum()
            amp = fundamentals.avg_qtr_market_price.at[n_qtr, "avg_market_price"]
            ttm_pe_ratios.at[n_qtr, "ttm_eps"] = ttm_eps
            ttm_pe_ratios.at[n_qtr, "avg_market_price"] = amp
            ttm_pe_ratios.at[n_qtr, "ttm_pe"] = amp / ttm_eps

        return ttm_pe_ratios







runner = ModelRunner()
peers = ["MA", "DFS", "AXP"]
runner.run_pe_mutiples("V", peers, 10)
print("model_runner")