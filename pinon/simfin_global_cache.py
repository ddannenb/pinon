import simfin as sf
from datetime import date
from simfin.names import *

__run_day = date.today()
__daily_share_prices = None
__quarterly_income_statements = None

def _load_daily_share_prices():
    global __run_day
    global __daily_share_prices
    if __daily_share_prices is None or __run_day != date.today():
        __daily_share_prices = sf.load_shareprices(variant='daily', market='us')
    return __daily_share_prices

def _load_quarterly_income_statements():
    global __run_day
    global __quarterly_income_statements
    if __quarterly_income_statements is None or __run_day != date.today():
        __quarterly_income_statements = sf.load_income(variant='annual', market='us', refresh_days=0,
                                                                    index=[TICKER, PUBLISH_DATE])
    return __quarterly_income_statements

