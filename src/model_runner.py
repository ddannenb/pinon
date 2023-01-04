from fundamentals import Fundamentals
import pandas as pd
import global_defs


class ModelRunner:
    def __init__(self):
        self.fundamentals = None
        self.peer_fundamentals = {}
        self.target_ttm_pe = None
        self.peer_ttm_pe = {}
        self.peer_stats = {}
        self.pe_mutiples = pd.DataFrame()
        self.master_config = self.read_excel_config()

    def run_pe_mutiples(self, symbol, peers, num_years):
        # since pe is using a ttm approach, additional 3 qtr reports are fetched
        num_reports = num_years * 4 + 3

        self.fundamentals = Fundamentals(symbol, num_reports)
        self.fundamentals.fetch_all()

        self.target_ttm_pe = self.calc_ttm_pe(self.fundamentals)

        for ndx, row in peers.iterrows():
            peer_symbol = row['peer_symbol']
            self.peer_fundamentals[peer_symbol] = Fundamentals(peer_symbol, num_reports)
            self.peer_fundamentals[peer_symbol].fetch_all()

            self.peer_ttm_pe[peer_symbol] = self.calc_ttm_pe(self.peer_fundamentals[peer_symbol])
            self.peer_ttm_pe[peer_symbol]['delta_target'] = (self.peer_ttm_pe[peer_symbol]['ttm_pe'] /
                                                             self.target_ttm_pe['ttm_pe']) - 1

        for ndx, row in peers.iterrows():
            peer_symbol = row['peer_symbol']

            self.peer_stats[peer_symbol] = pd.DataFrame()
            mean = self.peer_ttm_pe[peer_symbol]['delta_target'].mean()
            self.peer_stats[peer_symbol].at[0, 'mean_delta'] = mean

            std = self.peer_ttm_pe[peer_symbol]['delta_target'].std()

            mask_in_one_sig = (self.peer_ttm_pe[peer_symbol]['delta_target'] >= mean - std) & (
                        self.peer_ttm_pe[peer_symbol]['delta_target'] <= mean + std)
            in_one_sig = self.peer_ttm_pe[peer_symbol].loc[mask_in_one_sig]
            self.peer_stats[peer_symbol].at[0, 'mean_one_sig_delta'] = in_one_sig['delta_target'].mean()

            mask_in_two_sig = (self.peer_ttm_pe[peer_symbol]['delta_target'] >= mean - 3 * std) & (
                    self.peer_ttm_pe[peer_symbol]['delta_target'] <= mean + 3 * std)
            in_two_sig = self.peer_ttm_pe[peer_symbol].loc[mask_in_two_sig]
            self.peer_stats[peer_symbol].at[0, 'mean_two_sig_delta'] = in_two_sig['delta_target'].mean()

        cum_pe = 0
        for ndx, row in peers.iterrows():
            peer_symbol = row['peer_symbol']
            peer_weight = row['peer_weight']


        print("Done")
        # self.ttm_pe['cum_peer_delta'] = 0
        # for k in peers:
        #     self.ttm_pe['cum_peer_delta'] += self.ttm_pe[k + '_peer_delta_pe']
        # self.ttm_pe['cum_peer_delta'] = self.ttm_pe['cum_peer_delta'] / len(peers)
        #
        # self.pe_mutiples["industry_pe"]

    def read_excel_config(self):
        master_config = {}
        master_config['target'] = pd.read_excel(global_defs.get_config_file_path(), sheet_name="Master")
        for ndx, row in master_config['target'].iterrows():
            target = row['target']
            master_config[target] = pd.read_excel(global_defs.get_config_file_path(), sheet_name=target)
        return master_config

    def calc_ttm_pe(self, fundamentals):
        ttm_pe_ratios = pd.DataFrame(index=range(fundamentals.num_qtr_reports - 3),
                                     columns=["ttm_pe", "ttm_eps", "avg_market_price"])
        for n_qtr in range(fundamentals.num_qtr_reports - 3):
            ttm_eps = fundamentals.income_statements.iloc[n_qtr:n_qtr + 4]["eps"].sum()
            amp = fundamentals.avg_qtr_market_price.at[n_qtr, "avg_market_price"]
            ttm_pe = amp / ttm_eps
            ttm_pe_ratios.at[n_qtr, "ttm_eps"] = ttm_eps
            ttm_pe_ratios.at[n_qtr, "avg_market_price"] = amp
            ttm_pe_ratios.at[n_qtr, "ttm_pe"] = ttm_pe

        return ttm_pe_ratios


runner = ModelRunner()
config = runner.read_excel_config()
peers = config['V']
runner.run_pe_mutiples("V", peers, 10)
print("model_runner")
