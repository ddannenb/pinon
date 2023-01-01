from urllib.request import urlopen
import certifi
import json
import pandas as pd
import numpy as np
import global_defs
from datetime import datetime
from datetime import timedelta

class TtmPe():
    def __init__(self, symbol, num_reports):
        self.symbol = symbol
        self.num_reports = num_reports
        self.income_statement = None
        self.balance_sheet = None
        self.cash_flow = None
        self.market_price = None
        self.report_dates = None


    def get_financial_statements(self):
        response = urlopen(global_defs.get_income_statement_uri(self.symbol, self.num_reports), cafile=certifi.where())
        json_data = response.read().decode("utf-8")
        self.income_statement = pd.DataFrame(json.loads(json_data))

        self.report_dates = self.income_statement[["date"]]
        self.calc_avg_quarterly_market_price(self.report_dates)
        print(self.report_dates)

    def calc_avg_quarterly_market_price(self, report_dates):
        self.market_price = pd.DataFrame(index=range(report_dates.shape[0]), columns=["avg_market_price"])
        for row_n in range(report_dates.shape[0]-1):
            end_date = report_dates.at[row_n, "date"]
            # API call is data inclusive, add 1 day to report date to bracket the quarter
            sdt = datetime.strptime(report_dates.at[row_n + 1, "date"], '%Y-%m-%d') + timedelta(days=1)
            start_date = sdt.strftime('%Y-%m-%d')

            response = urlopen(global_defs.get_historical_price_uri(self.symbol, start_date, end_date), cadefault=certifi.where())
            json_data = response.read().decode("utf-8")
            qtr_prices = pd.DataFrame(json.loads(json_data)["historical"])
            qtr_mean = qtr_prices["vwap"].mean()
            self.market_price.at[row_n, "avg_market_price"] = qtr_mean

    def read_excel_config(self):
        master_config = pd.read_excel(global_defs.get_config_file_path())
        print(master_config)



tf = TtmPe("V", 40);
res = tf.get_financial_statements()
pdres = pd.DataFrame(res)
tf.read_excel_config()
print("Done")
