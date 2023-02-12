import pathlib

FMP_API_KEY = "8c0af34f05d7501418ffd0b08e1958d8"
FMP_BASE_URI = "https://financialmodelingprep.com/api/v3/"
# DATA_PATH = pathlib.Path(__file__).parent.parent.absolute().as_posix()
DATA_PATH = pathlib.Path(__file__).parent.parent / "data"


def get_income_statement_uri(symbol, num_reports=None):
    uri = FMP_BASE_URI + "income-statement/" + symbol + "?apikey=" + FMP_API_KEY + "&period=quarter"
    if num_reports is None:
        return uri
    else:
        return uri + "&limit=" + str(num_reports)


def get_balance_sheet_statement_uri(symbol, num_reports=None):
    uri = FMP_BASE_URI + "balance-sheet-statement/" + symbol + "?apikey=" + FMP_API_KEY + "&period=quarter"
    if num_reports is None:
        return uri
    else:
        return uri + "&limit=" + str(num_reports)


def get_cash_flow_statement_uri(symbol, num_reports=None):
    uri = FMP_BASE_URI + "cash-flow-statement/" + symbol + "?apikey=" + FMP_API_KEY + "&period=quarter"
    if num_reports is None:
        return uri
    else:
        return uri + "&limit=" + str(num_reports)

def get_financial_ratios_uri(symbol, num_reports=None):
    uri = FMP_BASE_URI + "ratios/" + symbol + "?apikey=" + FMP_API_KEY + "&period=quarter"
    if num_reports is None:
        return uri
    else:
        return uri + "&limit=" + str(num_reports)


def get_historical_price_uri(symbol, start_date, end_date):
    return FMP_BASE_URI + "historical-price-full/" + symbol + "?apikey=" + FMP_API_KEY + "&from=" + start_date + "&to=" + end_date


def get_config_file_path(file_name="master_short.xlsx"):
    return DATA_PATH / file_name
