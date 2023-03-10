import pathlib
import pandas as pd
import simfin as sf
import simfin.names as sf_cols
import pinon.names as pn_cols

from companies import Companies

PROJ_PATH = pathlib.Path(__file__).parent.parent
CONFIG_PATH = PROJ_PATH / "config"
SIMFIN_DATA_PATH = PROJ_PATH / 'simfin_data'


class Config:
    def __init__(self, config_name):
        self.mode = None
        self.targets = None
        self.peers = None
        self.master_config = None
        self.company_details = pd.DataFrame(
            columns=[pn_cols.TICKER, pn_cols.COMPANY_NAME, pn_cols.INDUSTRY_ID, pn_cols.PAST_YEARS_REQUESTED, pn_cols.PEER_LIST])
        self.config_path = CONFIG_PATH / f"{config_name}.xlsx"
        if not self.config_path.is_file():
            raise TypeError(f"{self.config_path} is not a valid file")
        print(f"Config file found at: {self.config_path}")

        # Simfin setup
        sf.set_data_dir(SIMFIN_DATA_PATH)
        print(f"Simfin data directory: {SIMFIN_DATA_PATH}")

        sf.load_api_key(CONFIG_PATH / 'simfin_api_key.txt')

    def parse_master_sheet(self):
        master_sheet = pd.read_excel(self.config_path, sheet_name="Master", header=1, nrows=20)
        comp = Companies()
        company_details = pd.DataFrame(columns=[pn_cols.TICKER, pn_cols.COMPANY_NAME, pn_cols.INDUSTRY_ID, pn_cols.PAST_YEARS_REQUESTED])


        for ndx, row in master_sheet.iterrows():
            c = comp.get_company(row[pn_cols.TICKER]).copy()
            if c is None:
                print(f"There is an error in the ticker symbol {ndx} supplied in the Master sheet of config file: {self.config_path}")
            else:
                c[pn_cols.TICKER] = c.name  # the index
                c[pn_cols.PAST_YEARS_REQUESTED] = row[pn_cols.PAST_YEARS_REQUESTED]
                company_details.loc[len(company_details.index)] = c

        company_details.set_index(pn_cols.TICKER, inplace=True, drop=True)

        return company_details

    def parse_target_sheet(self, sheet_name, past_years_requested=-1):
        target_section = pd.read_excel(self.config_path, sheet_name=sheet_name, header=2, nrows=10)
        peer_section = pd.read_excel(self.config_path, sheet_name=sheet_name, header=16, nrows=20)
        all_peers = []

        comp = Companies()

        for ndx, row in target_section.iterrows():
            c = comp.get_company(row[pn_cols.TICKER]).copy()
            if c is None:
                print(f"There is an error in the ticker symbol {ndx} supplied in sheet {sheet_name} of config file: {self.config_path}")
            else:
                all_peers.append(c.name)
                c[pn_cols.TICKER] = c.name  # the index
                c[pn_cols.PAST_YEARS_REQUESTED] = past_years_requested
                c[pn_cols.PEER_LIST] = []
                self.company_details.loc[len(self.company_details.index)] = c

        self.company_details.set_index(pn_cols.TICKER, inplace=True, drop=True)
        return self.company_details


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
            self.master_config[target_symbol]['recent_reports'] = target_sheet_recent_reports.drop(['report_date'],
                                                                                                   axis=1).to_dict(
                'records')
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
