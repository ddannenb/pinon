import pandas as pd

import simfin_global_cache as sfc
import simfin.names as sf_cols


class Fundamentals():
    def __init__(self):
        self.quarterly_income_statements = sfc._load_quarterly_income_statements()

    def get_income_statements(self, tickers):
        return self.quarterly_income_statements.loc[tickers]

    def get_first_report_date(self, ticker):
        c = self.quarterly_income_statements.loc[ticker]
        return c.index[0]

    def get_last_report_date(self, ticker):
        c = self.quarterly_income_statements.loc[ticker]
        return c.index[-1]

