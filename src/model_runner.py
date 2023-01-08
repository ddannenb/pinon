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

        # adjustment to peers based on historic deltas
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

            mask_in_two_sig = (self.peer_ttm_pe[peer_symbol]['delta_target'] >= mean - 2 * std) & (
                    self.peer_ttm_pe[peer_symbol]['delta_target'] <= mean + 2 * std)
            in_two_sig = self.peer_ttm_pe[peer_symbol].loc[mask_in_two_sig]
            self.peer_stats[peer_symbol].at[0, 'mean_two_sig_delta'] = in_two_sig['delta_target'].mean()


        self.pe_mutiples = self.target_ttm_pe.copy()
        self.pe_mutiples['peer_wavg_ttm_pe'] = 0
        self.pe_mutiples['model_val'] = 0
        self.pe_mutiples['peer_wavg_adj1s_ttm_pe'] = 0
        self.pe_mutiples['model_val_adj1s'] = 0
        self.pe_mutiples['peer_wavg_adj2s_ttm_pe'] = 0
        self.pe_mutiples['model_val_adj2s'] = 0
        self.pe_mutiples['peer_wavg_adj_ttm_pe'] = 0
        self.pe_mutiples['model_val_adj'] = 0



        # calc the weighted average peer pe and weighted average adjusted deltas and pes
        cum_weight = 0
        cum_weighted_delta = 0
        cum_weighted_one_sig_delta = 0
        cum_weighted_two_sig_delta = 0

        for ndx, row in peers.iterrows():
            peer_symbol = row['peer_symbol']
            peer_weight = row['peer_weight']

            cum_weight += peer_weight
            cum_weighted_delta += self.peer_stats[peer_symbol].at[0, 'mean_delta'] * peer_weight
            cum_weighted_one_sig_delta += self.peer_stats[peer_symbol].at[0, 'mean_one_sig_delta'] * peer_weight
            cum_weighted_two_sig_delta += self.peer_stats[peer_symbol].at[0, 'mean_two_sig_delta'] * peer_weight
            # temp = self.peer_ttm_pe[peer_symbol]['ttm_pe'] * peer_weight
            self.pe_mutiples['peer_wavg_ttm_pe'] += self.peer_ttm_pe[peer_symbol]['ttm_pe'] * peer_weight


        cum_weighted_delta = cum_weighted_delta / cum_weight
        cum_weighted_one_sig_delta = cum_weighted_one_sig_delta / cum_weight
        cum_weighted_two_sig_delta = cum_weighted_two_sig_delta / cum_weight

        self.pe_mutiples['peer_wavg_ttm_pe'] = self.pe_mutiples['peer_wavg_ttm_pe'] / cum_weight
        self.pe_mutiples['peer_wavg_adj1s_ttm_pe'] = self.pe_mutiples['peer_wavg_ttm_pe'] / (1 + cum_weighted_one_sig_delta)
        self.pe_mutiples['peer_wavg_adj2s_ttm_pe'] = self.pe_mutiples['peer_wavg_ttm_pe'] / (1 + cum_weighted_two_sig_delta)
        self.pe_mutiples['peer_wavg_adj_ttm_pe'] = self.pe_mutiples['peer_wavg_ttm_pe'] / (1 + cum_weighted_delta)

        self.pe_mutiples['model_val'] = self.pe_mutiples['peer_wavg_ttm_pe'] * self.pe_mutiples['ttm_eps']
        self.pe_mutiples['model_val_adj1s'] = self.pe_mutiples['peer_wavg_adj1s_ttm_pe'] * self.pe_mutiples['ttm_eps']
        self.pe_mutiples['model_val_adj2s'] = self.pe_mutiples['peer_wavg_adj2s_ttm_pe'] * self.pe_mutiples['ttm_eps']
        self.pe_mutiples['model_val_adj'] = self.pe_mutiples['peer_wavg_adj_ttm_pe'] * self.pe_mutiples['ttm_eps']

        print("Done")

    def read_excel_config(self):
        master_config = {}
        master_config['target'] = pd.read_excel(global_defs.get_config_file_path(), sheet_name="Master")
        for ndx, row in master_config['target'].iterrows():
            target = row['target']
            master_config[target] = pd.read_excel(global_defs.get_config_file_path(), sheet_name=target)
        return master_config

    def calc_ttm_pe(self, fundamentals):
        ttm_pe_ratios = pd.DataFrame(index=range(fundamentals.num_qtr_reports - 3),
                                     columns=['qtr_start_date', 'qtr_end_date', 'avg_market_price', 'ttm_pe', 'ttm_eps'])
        ttm_pe_ratios[['qtr_start_date', 'qtr_end_date', 'avg_market_price']] = fundamentals.avg_qtr_market_price[['qtr_start_date', 'qtr_end_date', 'avg_market_price']]
        for n_qtr in range(fundamentals.num_qtr_reports - 3):
            ttm_eps = fundamentals.income_statements.iloc[n_qtr:n_qtr + 4]["eps"].sum()
            amp = fundamentals.avg_qtr_market_price.at[n_qtr, "avg_market_price"]
            ttm_pe = amp / ttm_eps
            ttm_pe_ratios.at[n_qtr, "ttm_eps"] = ttm_eps
            # ttm_pe_ratios.at[n_qtr, "avg_market_price"] = amp
            ttm_pe_ratios.at[n_qtr, "ttm_pe"] = ttm_pe

        return ttm_pe_ratios


runner = ModelRunner()
config = runner.read_excel_config()
peers = config['V']
runner.run_pe_mutiples("V", peers, 10)
print("model_runner")
