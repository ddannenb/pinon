import json
import ssl
from datetime import datetime
from datetime import timedelta
from urllib.request import urlopen

import certifi
import pandas as pd

import global_defs


class Fundamentals():
    def __init__(self, symbol, num_qtr_reports_requested):
        self.symbol = symbol
        self.num_qtr_reports_requested = num_qtr_reports_requested
        self.num_qtr_reports = None
        self.income_statements = None
        self.balance_sheet_statements = None
        self.cash_flow_statement = None
        # self.financial_ratios = None
        self.avg_qtr_market_price = None
        self.report_dates = None


    def fetch_all(self):
        self.get_financial_statements()
        self.trim_statement_gaps()
        self.calc_avg_quarterly_market_price(self.report_dates)
        self.trim_missing_prices()
        self.num_qtr_reports = self.income_statements.shape[0]
        print("Fetched fundamentals for " + self.symbol + ", Number of reports: " + str(self.num_qtr_reports))


    def get_financial_statements(self):
        context = ssl.create_default_context(cafile=certifi.where())
        # income statements
        response = urlopen(global_defs.get_income_statement_uri(self.symbol, self.num_qtr_reports_requested), context=context)
        json_data = response.read().decode("utf-8")
        self.income_statements = pd.DataFrame(json.loads(json_data))

        # balance sheet statements
        response = urlopen(global_defs.get_balance_sheet_statement_uri(self.symbol, self.num_qtr_reports_requested), context=context)
        json_data = response.read().decode("utf-8")
        self.balance_sheet_statements = pd.DataFrame(json.loads(json_data))

        # cash flow statements
        response = urlopen(global_defs.get_cash_flow_statement_uri(self.symbol, self.num_qtr_reports_requested),context=context)
        json_data = response.read().decode("utf-8")
        self.cash_flow_statement = pd.DataFrame(json.loads(json_data))

        # # financial ratios
        # response = urlopen(global_defs.get_financial_ratios_uri(self.symbol, self.num_qtr_reports_requested), context=context)
        # json_data = response.read().decode("utf-8")
        # self.financial_ratios = pd.DataFrame(json.loads(json_data))

    def trim_statement_gaps(self):
        # common report dates
        self.report_dates = pd.merge(self.income_statements['date'], self.balance_sheet_statements['date'], on=['date'], how='inner')
        self.report_dates = pd.merge(self.report_dates, self.cash_flow_statement['date'], on='date', how='inner')

        #trim reports if there are quarterly gaps
        sdate = datetime.strptime(self.report_dates.at[0, 'date'], '%Y-%m-%d')
        trunc_row = self.report_dates.shape[0]
        for row_n in range(1, self.report_dates.shape[0]):
            edate = datetime.strptime(self.report_dates.at[row_n, 'date'], '%Y-%m-%d')
            datediff = sdate - edate
            sdate = edate
            if (datediff.days < 70) | (datediff.days >120):
                trunc_row = row_n

        self.report_dates = self.report_dates.truncate(after=trunc_row - 1)
        self.income_statements = pd.merge(self.income_statements, self.report_dates, on='date', how='inner')
        self.balance_sheet_statements = pd.merge(self.balance_sheet_statements, self.report_dates, on='date', how='inner')
        self.cash_flow_statement = pd.merge(self.cash_flow_statement, self.report_dates, on='date', how='inner')

    def trim_missing_prices(self):
        trunc_row = self.avg_qtr_market_price['avg_market_price'].isna().idxmax()
        self.avg_qtr_market_price = self.avg_qtr_market_price.truncate(after=trunc_row - 1)
        self.report_dates = self.report_dates.truncate(after=trunc_row - 1)
        self.income_statements = self.income_statements.truncate(after=trunc_row - 1)
        self.balance_sheet_statements = self.balance_sheet_statements.truncate(after=trunc_row - 1)
        self.cash_flow_statement = self.cash_flow_statement.truncate(after=trunc_row - 1)


    def calc_avg_quarterly_market_price(self, report_dates):
        self.avg_qtr_market_price = pd.DataFrame(index=range(report_dates.shape[0]), columns=["qtr_start_date", "qtr_end_date", "avg_market_price"])
        end_date = report_dates.at[0, "date"]
        sdt = datetime.strptime(report_dates["date"].iloc[-1], '%Y-%m-%d') + timedelta(days=1)
        start_date = sdt.strftime('%Y-%m-%d')

        context = ssl.create_default_context(cafile=certifi.where())
        response = urlopen(global_defs.get_historical_price_uri(self.symbol, start_date, end_date), context=context)
        json_data = response.read().decode("utf-8")
        all_historical_prices = pd.DataFrame(json.loads(json_data)["historical"])

        for row_n in range(report_dates.shape[0]-1):
            qtr_end_date = report_dates.at[row_n, "date"]
            # API call is data inclusive, add 1 day to report date to bracket the quarter
            qsdt = datetime.strptime(report_dates.at[row_n + 1, "date"], '%Y-%m-%d') + timedelta(days=1)
            qtr_start_date = qsdt.strftime('%Y-%m-%d')
            mask = (all_historical_prices['date'] >= qtr_start_date) & (all_historical_prices['date'] <= qtr_end_date)
            qtr_prices = all_historical_prices.loc[mask]

            qtr_mean = qtr_prices["vwap"].mean()
            self.avg_qtr_market_price.at[row_n, "avg_market_price"] = qtr_mean
            self.avg_qtr_market_price.at[row_n, "qtr_start_date"] = qtr_start_date
            self.avg_qtr_market_price.at[row_n, "qtr_end_date"] = qtr_end_date

# fund = Fundamentals('V', 200)
# fund.fetch_all()
# print('Done')