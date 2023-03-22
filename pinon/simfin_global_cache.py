import simfin as sf
from datetime import date
import simfin.names as sf_cols

__daily_share_prices = None
__daily_share_prices_updated = None

__daily_share_price_ratios = None
__daily_share_price_ratios_updated = None

__quarterly_income_statements = None
__quarterly_income_statements_updated = None
__quarterly_income_statements_bank = None
__quarterly_income_statements_bank_updated = None
__quarterly_income_statements_insurance = None
__quarterly_income_statements_insurance_updated = None

__quarterly_derived_ratios = None
__quarterly_derived_ratios_updated = None
__quarterly_derived_ratios_bank = None
__quarterly_derived_ratios_bank_updated = None
__quarterly_derived_ratios_insurance = None
__quarterly_derived_ratios_insurance_updated = None

__companies = None
__companies_updated = None

# Daily Share Prices
def _load_daily_share_prices():
    global __daily_share_prices_updated
    global __daily_share_prices
    if __daily_share_prices is None or __daily_share_prices_updated != date.today():
        __daily_share_prices = sf.load_shareprices(variant='daily', market='us', refresh_days=1)
        __daily_share_prices_updated = date.today()
    return __daily_share_prices

def _load_daily_share_price_ratios():
    global __daily_share_price_ratios_updated
    global __daily_share_price_ratios
    if __daily_share_price_ratios is None or __daily_share_price_ratios_updated != date.today():
        __daily_share_price_ratios = sf.load_derived_shareprices(variant='daily', market='us', refresh_days=1)
        __daily_share_price_ratios_updated = date.today()
    return __daily_share_price_ratios

# Income Statements
def _load_quarterly_income_statements():
    global __quarterly_income_statements_updated
    global __quarterly_income_statements

    if __quarterly_income_statements is None or __quarterly_income_statements_updated != date.today():
        __quarterly_income_statements = sf.load_income(variant='quarterly', market='us', refresh_days=1, index=[sf_cols.TICKER, sf_cols.REPORT_DATE])
        __quarterly_income_statements_updated = date.today()
    return __quarterly_income_statements
def _load_quarterly_income_statements_bank():
    global __quarterly_income_statements_bank_updated
    global __quarterly_income_statements_bank
    if __quarterly_income_statements_bank is None or __quarterly_income_statements_bank_updated != date.today():
        __quarterly_income_statements_bank = sf.load_income_banks(variant='quarterly', market='us', refresh_days=1, index=[sf_cols.TICKER, sf_cols.REPORT_DATE])
        __quarterly_income_statements_bank_updated = date.today()

    return __quarterly_income_statements_bank

def _load_quarterly_income_statements_insurance():
    global __quarterly_income_statements_insurance_updated
    global __quarterly_income_statements_insurance

    if __quarterly_income_statements_insurance is None or __quarterly_income_statements_insurance_updated != date.today():
        __quarterly_income_statements_insurance = sf.load_income_insurance(variant='quarterly', market='us', refresh_days=1, index=[sf_cols.TICKER, sf_cols.REPORT_DATE])
        __quarterly_income_statements_insurance_updated = date.today()
    return __quarterly_income_statements_insurance

# Derived ratios
def _load_quarterly_derived_ratios():
    global __quarterly_derived_ratios_updated
    global __quarterly_derived_ratios

    if __quarterly_derived_ratios is None or __quarterly_derived_ratios_updated != date.today():
        __quarterly_derived_ratios = sf.load_derived(variant='quarterly', market='us', refresh_days=1, index=[sf_cols.TICKER, sf_cols.REPORT_DATE])
        __quarterly_derived_ratios_updated = date.today()
    return __quarterly_derived_ratios
def _load_quarterly_derived_ratios_bank():
    global __quarterly_derived_ratios_bank_updated
    global __quarterly_derived_ratios_bank
    if __quarterly_derived_ratios_bank is None or __quarterly_derived_ratios_bank_updated != date.today():
        __quarterly_derived_ratios_bank = sf.load_derived_banks(variant='quarterly', market='us', refresh_days=1, index=[sf_cols.TICKER, sf_cols.REPORT_DATE])
        __quarterly_derived_ratios_bank_updated = date.today()

    return __quarterly_derived_ratios_bank

def _load_quarterly_derived_ratios_insurance():
    global __quarterly_derived_ratios_insurance_updated
    global __quarterly_derived_ratios_insurance

    if __quarterly_derived_ratios_insurance is None or __quarterly_derived_ratios_insurance_updated != date.today():
        __quarterly_derived_ratios_insurance = sf.load_derived_insurance(variant='quarterly', market='us', refresh_days=1, index=[sf_cols.TICKER, sf_cols.REPORT_DATE])
        __quarterly_derived_ratios_insurance_updated = date.today()
    return __quarterly_derived_ratios_insurance

# Companies
def _load_companies():
    global __companies
    global __companies_updated
    if __companies_updated is None or __companies_updated != date.today():
        __companies = sf.load_companies(market='us', refresh_days=10)
        __companies_updated = date.today()
    return __companies


