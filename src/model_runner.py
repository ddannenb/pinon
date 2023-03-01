import pandas as pd

import global_defs
from fundamentals import Fundamentals
from trading_multiples import TradingMultiples


class ModelRunner:
    def __init__(self):
        self.fundamentals = None
        self.peer_fundamentals = {}
        self.target_ttm_pe = None
        self.peer_ttm_pe = {}
        self.peer_stats = {}
        self.pe_mutiples = pd.DataFrame()
        self.master_config = self.read_excel_config()

    def get_fundamentas(self, target_symbol, peers, num_years):
        # since pe is using a ttm approach, additional 3 qtr reports are fetched
        num_reports = num_years * 4 + 3

        self.fundamentals = Fundamentals(target_symbol, num_reports)
        self.fundamentals.fetch_all()

        for ndx, row in peers.iterrows():
            peer_symbol = row['peer_symbol']
            self.peer_fundamentals[peer_symbol] = Fundamentals(peer_symbol, num_reports)
            self.peer_fundamentals[peer_symbol].fetch_all()

    def read_excel_config(self):
        master_config = {}
        master_config['target'] = pd.read_excel(global_defs.get_config_file_path(), sheet_name="Master")
        for ndx, row in master_config['target'].iterrows():
            target = row['target']
            master_config[target] = pd.read_excel(global_defs.get_config_file_path(), sheet_name=target)
        return master_config




runner = ModelRunner()
config = runner.read_excel_config()
peers = config['PAGS']
runner.get_fundamentas("PAGS", peers, 10)
tm = TradingMultiples()
tm.run_pe_mutiples("V", peers, runner.fundamentals, runner.peer_fundamentals)
print("model_runner")
