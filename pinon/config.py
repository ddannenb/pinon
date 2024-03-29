import pathlib
import pandas as pd
import simfin as sf

import names as pn_cols
from fundamentals import Fundamentals
from companies import Companies

PROJ_PATH = pathlib.Path(__file__).parent.parent
CONFIG_PATH = PROJ_PATH / "config"
SIMFIN_DATA_PATH = PROJ_PATH / 'simfin_data'


class Config:
    def __init__(self, master_config_name, target_sheet_name, past_years_requested=-1):
        self.companies = None
        self.breaking_reports = None
        self.forecasts = None
        self.master_config_name = master_config_name
        self.target_sheet_name = target_sheet_name
        self.past_years_requested = past_years_requested

        # TODO pass config_path into constructor from MasterConfig
        self.config_path = CONFIG_PATH / f"{master_config_name}.xlsx"
        if not self.config_path.is_file():
            raise TypeError(f"{self.config_path} is not a valid file")
        print(f"Config file found at: {self.config_path}")

        # Simfin setup
        sf.set_data_dir(SIMFIN_DATA_PATH)
        print(f"Simfin data directory: {SIMFIN_DATA_PATH}")

        sf.load_api_key(CONFIG_PATH / 'simfin_api_key.txt')

        self.companies = self.parse_target_sheet(self.target_sheet_name, self.past_years_requested)
        self.breaking_reports = self.parse_breaking_reports(self.target_sheet_name)
        self.forecasts = self.parse_forecasts(self.target_sheet_name)

    def parse_breaking_reports(self, sheet_name):
        breaking_reports = pd.DataFrame(columns=[pn_cols.TICKER, pn_cols.REPORT_DATE, pn_cols.EPS_BREAKING, pn_cols.REVENUE_BREAKING])
        breaking_reports = pd.read_excel(self.config_path, sheet_name=sheet_name, header=32, nrows=10)
        breaking_reports[pn_cols.BREAKING_EMPLOYED] = False
        breaking_reports.set_index([pn_cols.TICKER, pn_cols.REPORT_DATE], inplace=True)

        return breaking_reports

    def parse_forecasts(self, sheet_name):
        forecasts = pd.DataFrame(columns=[pn_cols.TICKER, pn_cols.REPORT_DATE, pn_cols.QTR_EPS_FORECAST, pn_cols.QTR_REV_FORECAST, pn_cols.QTR_DIV_FORECAST])
        forecasts = pd.read_excel(self.config_path, sheet_name=sheet_name, header=46)
        forecasts.set_index([pn_cols.TICKER, pn_cols.REPORT_DATE], inplace=True)
        # Rev entered is in million, convert
        forecasts[pn_cols.QTR_REV_FORECAST] = forecasts[pn_cols.QTR_REV_FORECAST] * 1000000
        return forecasts

    def parse_target_sheet(self, sheet_name, past_years_requested=-1):
        companies_section = pd.read_excel(self.config_path, sheet_name=sheet_name, header=2, nrows=25)
        companies = pd.DataFrame(
            columns=[pn_cols.TICKER, pn_cols.COMPANY_NAME, pn_cols.INDUSTRY_ID, pn_cols.SIMFIN_SCHEMA, pn_cols.PAST_YEARS_REQUESTED, pn_cols.WEIGHT, pn_cols.EVALUATE, pn_cols.PEER_LIST, pn_cols.PEER_WEIGHTS, pn_cols.FIRST_REPORT_DATE, pn_cols.LAST_REPORT_DATE])
        all_peers = []
        comp = Companies()
        funds = Fundamentals()

        for ndx, row in companies_section.iterrows():
            ticker = row[pn_cols.TICKER]
            simfin_schema = funds.get_simfin_schema(ticker)
            c = comp.get_company(ticker)
            if c is None:
                print(f"There is an error in the supplied ticker symbol {ticker} in Company List of sheet: {sheet_name} of config file: {self.config_path}. Company was not found and was dropped from the list.")
            elif simfin_schema is None:
                print(f"There is an error in the supplied ticker symbol {ticker} in Company List of sheet: {sheet_name} of config file: {self.config_path}. Financials are not available, company was dropped from the list.")
            elif not funds.is_standard_reporting_dates(ticker):
                print(f"There is an error in the supplied ticker symbol {ticker} in Company List of sheet: {sheet_name} of config file: {self.config_path}. Company uses non stardard quarterly reporting date not currently supported. Company was dropped from the list.")
            else:
                cc = pd.Series(c)
                all_peers.append(ticker)
                cc[pn_cols.TICKER] = ticker
                cc[pn_cols.SIMFIN_SCHEMA] = simfin_schema
                cc[pn_cols.PAST_YEARS_REQUESTED] = past_years_requested
                cc[pn_cols.WEIGHT] = row[pn_cols.WEIGHT]
                cc[pn_cols.EVALUATE] = True if (row[pn_cols.EVALUATE].lower() == 'y' or row[pn_cols.EVALUATE].lower() == 'yes') else False
                cc[pn_cols.PEER_LIST] = [] if cc[pn_cols.EVALUATE] else None
                cc[pn_cols.FIRST_REPORT_DATE] = funds.get_first_report_date(ticker)
                cc[pn_cols.LAST_REPORT_DATE] = funds.get_last_report_date(ticker)
                companies.loc[len(companies.index)] = cc

        companies.set_index(pn_cols.TICKER, inplace=True, drop=True)

        eval_mask = (companies[pn_cols.EVALUATE])
        eval_list = companies[eval_mask].index.tolist()

        # Generate Peer List
        for c in eval_list:
            pl = [x for x in all_peers if x != c]
            companies.at[c, pn_cols.PEER_LIST] = pl

        # Generate Peer Weights
        for c in eval_list:
            pc = companies.loc[companies.index.isin(companies.at[c, pn_cols.PEER_LIST])]
            pws = pc[pn_cols.WEIGHT] / pc[pn_cols.WEIGHT].sum()
            companies.at[c, pn_cols.PEER_WEIGHTS] = pws

        return companies

    def get_breaking_report(self, ticker):
        if ticker not in self.breaking_reports.index:
            return None
        brs = self.breaking_reports.loc[ticker]
        br = brs[brs[pn_cols.BREAKING_EMPLOYED]]
        return None if br.empty else br.reset_index().squeeze()
        # # Move following block to config
        # if ticker in br.index:
        #     breaking_report_date = br.index.tolist()[0][1]

    def get_targets(self):
        return self.companies.loc[self.companies[pn_cols.EVALUATE]]

    def get_target_tickers(self):
        targets = self.get_targets()
        return targets.index.tolist()

    def get_peer_list(self, target):
        return self.companies.loc[target, pn_cols.PEER_LIST]

    def get_peer_weights(self, target):
        return self.companies.loc[target, pn_cols.PEER_WEIGHTS]