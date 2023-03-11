import simfin_global_cache as sfc
import simfin.names as sf_cols


class Fundamentals():
    def __init__(self):
        self.quarterly_income_statements = sfc._load_quarterly_income_statements()
        self.quarterly_income_statements_bank = sfc._load_quarterly_income_statements_bank()
        self.quarterly_income_statements_insurance = sfc._load_quarterly_income_statements_insurance()

    def get_quarterly_income_statement(self, ticker, schema='normal'):
        if schema == 'normal':
            return self.quarterly_income_statements.loc[ticker]
        elif schema == 'bank':
            return self.quarterly_income_statements_bank.loc[ticker]
        elif schema == 'insurance':
            return self.quarterly_income_statements_insurance.loc[ticker]

    def get_simfin_schema(self, ticker):
        if ticker in self.quarterly_income_statements.index:
            return 'normal'
        elif ticker in self.quarterly_income_statements_bank.index:
            return 'bank'
        elif ticker in self.quarterly_income_statements_insurance.index:
            return 'insurance'
        else:
            return 'not_found'

    def get_first_report_date(self, ticker, schema='normal'):
        c = self.get_quarterly_income_statement(ticker, schema)
        return c.index[0]

    def get_last_report_date(self, ticker, schema='normal'):
        c = self.get_quarterly_income_statement(ticker, schema)
        return c.index[-1]

