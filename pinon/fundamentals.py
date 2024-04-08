import simfin_global_cache as sfc
import simfin.names as sf_cols


class Fundamentals():
    def __init__(self):
        self.quarterly_income_statements = sfc._load_quarterly_income_statements()
        self.quarterly_income_statements_bank = sfc._load_quarterly_income_statements_bank()
        self.quarterly_income_statements_insurance = sfc._load_quarterly_income_statements_insurance()

        self.quarterly_derived_ratios = sfc._load_quarterly_derived_ratios()
        self.quarterly_derived_ratios_bank = sfc._load_quarterly_derived_ratios_bank()
        self.quarterly_derived_ratios_insurance = sfc._load_quarterly_derived_ratios_insurance()

    def get_quarterly_income_statement(self, ticker):
        schema = self.get_simfin_schema(ticker)
        if schema is None:
            return None
        if schema == 'normal':
            return self.quarterly_income_statements.loc[ticker]
        elif schema == 'bank':
            return self.quarterly_income_statements_bank.loc[ticker]
        elif schema == 'insurance':
            return self.quarterly_income_statements_insurance.loc[ticker]

    def get_quarterly_derived_ratios(self, ticker):
        schema = self.get_simfin_schema(ticker)
        if schema is None:
            return None
        if schema == 'normal':
            return self.quarterly_derived_ratios.loc[ticker]
        elif schema == 'bank':
            return self.quarterly_derived_ratios_bank.loc[ticker]
        elif schema == 'insurance':
            return self.quarterly_derived_ratios_insurance.loc[ticker]

    def get_simfin_schema(self, ticker):
        if ticker in self.quarterly_income_statements.index:
            return 'normal'
        elif ticker in self.quarterly_income_statements_bank.index:
            return 'bank'
        elif ticker in self.quarterly_income_statements_insurance.index:
            return 'insurance'
        else:
            return None

    def get_first_report_date(self, ticker):
        c = self.get_quarterly_income_statement(ticker)
        if c is None:
            return None
        return c.index[0]

    def get_last_report_date(self, ticker):
        c = self.get_quarterly_income_statement(ticker)
        if c is None:
            return None
        return c.index[-1]

    def get_past_years_available(self, ticker):
        sd = self.get_last_report_date(ticker)
        ed = self.get_first_report_date(ticker)
        diff = sd - ed
        return diff.days // 365

    def is_standard_reporting_dates(self, ticker):
        c = self.get_quarterly_income_statement(ticker)
        if c is None:
            return False
        l_filter = [val for val in c.index.tolist() if not val.is_quarter_end]
        if l_filter:
            return False
        return True


