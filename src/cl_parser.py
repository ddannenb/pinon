import pathlib
import pandas as pd

PROJ_PATH = pathlib.Path(__file__).parent.parent
CONFIG_PATH = PROJ_PATH / "config"


class ClParser:
    def __init__(self, config_name):
        self.mode = None
        self.targets = None
        self.peers = None
        self.master_config = None
        self.config_path = CONFIG_PATH / f"{config_name}.xlsx"
        if not self.config_path.is_file():
            raise TypeError(f"{self.config_path} is not a valid file")
        print('Here5')
    def parse_args(self):
        args = self.argumentParser.parse_args()
        self.mode = args.mode
        self.config_path = PROJ_PATH / args.config_file
        if not self.config_path.is_file():
            raise TypeError(f"{self.config_path} is not a valid file")

    def read_excel_config(self):
        self.peers = {}
        self.master_config = {}
        master_sheet = pd.read_excel(self.config_path, sheet_name="Master", header=1, nrows=20)
        for t_ndx, t_row in master_sheet.iterrows():
            target_symbol = t_row['target_symbol']
            self.master_config[target_symbol] = {}
            self.master_config[target_symbol]['num_years'] = t_row['num_years']

            # peers
            self.master_config[target_symbol]['peers'] = {}
            target_sheet_peers = pd.read_excel(self.config_path, sheet_name=target_symbol, header=1, nrows=20)
            for p_ndx, p_row in target_sheet_peers.iterrows():
                peer_symbol = p_row['peer_symbol']
                self.master_config[target_symbol]['peers'][peer_symbol] = {}
                self.master_config[target_symbol]['peers'][peer_symbol]['peer_weight'] = p_row['peer_weight']

            # recent reports
            self.master_config[target_symbol]['recent_reports'] = []
            target_sheet_recent_reports = pd.read_excel(self.config_path, sheet_name=target_symbol, header=24, nrows=5)
            rd_split = target_sheet_recent_reports['report_date'].str.split('-', expand=True)
            # target_sheet_recent_reports['report_quarter'] = rd_split[0]
            target_sheet_recent_reports.insert(0, 'report_quarter', rd_split[0])
            target_sheet_recent_reports.insert(0, 'report_year', rd_split[1])
            # target_sheet_recent_reports['report_year'] = rd_split[1]
            self.master_config[target_symbol]['recent_reports'] = target_sheet_recent_reports.drop(['report_date'], axis=1).to_dict('records')
            # self.master_config[target_symbol]['recent_reports'] = target_sheet_recent_reports.to_dict('records')
            print('Here')

        print('Here')

    def is_pre_mode(self):
        return self.mode == 'pre'

    def is_run_mode(self):
        return self.mode == 'run'


# clp = ClParser()
# clp.parse_args()
# clp.read_excel_config()
# print('Done')
