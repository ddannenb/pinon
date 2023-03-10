import simfin_global_cache as sfc


class Companies:
    def __init__(self):
        self.companies = sfc._load_companies()

    def get_company(self, ticker):
        if ticker not in self.companies.index:
            return None
        else:
            return self.companies.loc[ticker]

