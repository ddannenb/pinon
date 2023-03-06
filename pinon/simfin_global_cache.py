import simfin as sf
from datetime import date
import simfin.names as sf_cols

__daily_share_prices = None
__daily_share_prices_updated = None
__quarterly_income_statements = None
__quarterly_income_statements_updated = None

def _load_daily_share_prices():
    global __daily_share_prices_updated
    global __daily_share_prices
    if __daily_share_prices is None or __daily_share_prices_updated != date.today():
        __daily_share_prices = sf.load_shareprices(variant='daily', market='us')
        __daily_share_prices_updated = date.today()
    return __daily_share_prices

def _load_quarterly_income_statements():
    global __quarterly_income_statements_updated
    global __quarterly_income_statements
    if __quarterly_income_statements is None or __quarterly_income_statements_updated != date.today():
        __quarterly_income_statements = sf.load_income(variant='quarterly', market='us', refresh_days=0, index=[sf_cols.TICKER, sf_cols.REPORT_DATE])
        __quarterly_income_statements_updated = date.today()
    return __quarterly_income_statements

