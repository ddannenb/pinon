import pathlib
import pandas as pd
import simfin as sf
import simfin.names as sf_cols

import pinon.names as pn_cols
from pinon import Fundamentals, Companies

PROJ_PATH = pathlib.Path(__file__).parent.parent
CONFIG_PATH = PROJ_PATH / "config"
SIMFIN_DATA_PATH = PROJ_PATH / 'simfin_data'


class Config:
    def __init__(self, config_name):
        self.company_details = None
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
        return master_sheet

    def parse_target_sheet(self, sheet_name, past_years_requested=-1):
        companies_section = pd.read_excel(self.config_path, sheet_name=sheet_name, header=2, nrows=25)
        self.company_details = pd.DataFrame(
            columns=[pn_cols.TICKER, pn_cols.COMPANY_NAME, pn_cols.INDUSTRY_ID, pn_cols.PAST_YEARS_REQUESTED, pn_cols.PEER_WEIGHT, pn_cols.EVALUATE, pn_cols.PEER_LIST, pn_cols.FIRST_REPORT_DATE, pn_cols.LAST_REPORT_DATE])
        all_peers = []
        comp = Companies()
        funds = Fundamentals()

        for ndx, row in companies_section.iterrows():
            c = comp.get_company(row[pn_cols.TICKER])
            if c is None:
                print(f"There is an error in the supplied ticker symbol {row[pn_cols.TICKER]} in Company List of sheet: {sheet_name} of config file: {self.config_path}. It was not found and was dropped from the list.")
            else:
                cc = pd.Series(c)
                all_peers.append(row[pn_cols.TICKER])
                cc[pn_cols.TICKER] = row[pn_cols.TICKER]
                cc[pn_cols.PAST_YEARS_REQUESTED] = past_years_requested
                cc[pn_cols.PEER_WEIGHT] = row[pn_cols.PEER_WEIGHT]
                cc[pn_cols.EVALUATE] = True if (row[pn_cols.EVALUATE].lower() == 'y' or row[pn_cols.EVALUATE].lower() == 'yes') else False
                cc[pn_cols.PEER_LIST] = [] if cc[pn_cols.EVALUATE] else None
                cc[pn_cols.FIRST_REPORT_DATE] = funds.get_first_report_date(row[pn_cols.TICKER])
                cc[pn_cols.LAST_REPORT_DATE] = funds.get_last_report_date(row[pn_cols.TICKER])
                self.company_details.loc[len(self.company_details.index)] = cc

        self.company_details.set_index(pn_cols.TICKER, inplace=True, drop=True)

        eval_mask = (self.company_details[pn_cols.EVALUATE])
        eval_list = self.company_details[eval_mask].index.tolist()

        for c in eval_list:
            # self.company_details[peer, pn_cols.PEER_LIST] = [x for x in all_peers if x != peer]
            pl = [x for x in all_peers if x != c]
            self.company_details.at[c, pn_cols.PEER_LIST] = pl

        return self.company_details


# clp = ClParser()
# clp.parse_args()
# clp.read_excel_config()
# print('Done')
