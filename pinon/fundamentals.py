import pandas as pd

import simfin_global_cache as sfc


class Fundamentals():
    def __init__(self):
        self.quarterly_income_statements = sfc._load_quarterly_income_statements()

    def get_income_statements(self, tickers):
        return self.quarterly_income_statements.loc[tickers]