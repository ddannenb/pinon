import pathlib
import simfin as sf
import simfin.names as sf_cols

# Params for running the utility
# SimFin will re download new data sets after this many days. Set to -1 to force re download
INFINITY_DAYS = 365000

PROJ_PATH = pathlib.Path(__file__).parent.parent.parent
TEST_PATH = PROJ_PATH / "tests"
CONFIG_PATH = PROJ_PATH / "config"
SIMFIN_TEMP_DATA_PATH = TEST_PATH / 'simfin_temp_data'
SIMFIN_TEST_DATA_PATH = TEST_PATH / 'simfin_test_data'
TEST_TICKERS = ["V", "AXP", "DFS", "MA", "PYPL", "COF", "WU", "PAGS", "BAC"]


def main():
    # Simfin setup
    sf.set_data_dir(SIMFIN_TEMP_DATA_PATH)
    print(f"Simfin temp data directory: {SIMFIN_TEMP_DATA_PATH}")
    sf.load_api_key(CONFIG_PATH / 'simfin_api_key.txt')

    # US income quarterly
    qis = sf.load_income(variant='quarterly', market='us', refresh_days=INFINITY_DAYS,
                         index=[sf_cols.TICKER, sf_cols.REPORT_DATE])
    t = [t for t in TEST_TICKERS if t in qis.index]
    qis_test = qis.loc[t]
    qis_test.to_csv(SIMFIN_TEST_DATA_PATH / "us-income-quarterly.csv", sep=';')

    # US income banks quarterly
    qis = sf.load_income_banks(variant='quarterly', market='us', refresh_days=INFINITY_DAYS,
                               index=[sf_cols.TICKER, sf_cols.REPORT_DATE])
    t = [t for t in TEST_TICKERS if t in qis.index]
    qis_test = qis.loc[t]
    qis_test.to_csv(SIMFIN_TEST_DATA_PATH / "us-income-banks-quarterly.csv", sep=';')

    # US income insurance quarterly
    qis = sf.load_income_insurance(variant='quarterly', market='us', refresh_days=INFINITY_DAYS,
                                   index=[sf_cols.TICKER, sf_cols.REPORT_DATE])
    t = [t for t in TEST_TICKERS if t in qis.index]
    qis_test = qis.loc[t]
    qis_test.to_csv(SIMFIN_TEST_DATA_PATH / "us-income-insurance-quarterly.csv", sep=';')

    # US derived quarterly
    qis = sf.load_derived(variant='quarterly', market='us', refresh_days=INFINITY_DAYS,
                          index=[sf_cols.TICKER, sf_cols.REPORT_DATE])
    t = [t for t in TEST_TICKERS if t in qis.index]
    qis_test = qis.loc[t]
    qis_test.to_csv(SIMFIN_TEST_DATA_PATH / "us-derived-quarterly.csv", sep=';')

    # US derived banks quarterly
    qis = sf.load_derived_banks(variant='quarterly', market='us', refresh_days=INFINITY_DAYS,
                          index=[sf_cols.TICKER, sf_cols.REPORT_DATE])
    t = [t for t in TEST_TICKERS if t in qis.index]
    qis_test = qis.loc[t]
    qis_test.to_csv(SIMFIN_TEST_DATA_PATH / "us-derived-banks-quarterly.csv", sep=';')

    # US derived insurance quarterly
    qis = sf.load_derived_insurance(variant='quarterly', market='us', refresh_days=INFINITY_DAYS,
                                index=[sf_cols.TICKER, sf_cols.REPORT_DATE])
    t = [t for t in TEST_TICKERS if t in qis.index]
    qis_test = qis.loc[t]
    qis_test.to_csv(SIMFIN_TEST_DATA_PATH / "us-derived-insurance-quarterly.csv", sep=';')

    # US share prices daily
    qis = sf.load_shareprices(variant='daily', market='us', refresh_days=INFINITY_DAYS, index=[sf_cols.TICKER, sf_cols.DATE])
    t = [t for t in TEST_TICKERS if t in qis.index]
    qis_test = qis.loc[t]
    qis_test.to_csv(SIMFIN_TEST_DATA_PATH / "us-shareprices-daily.csv", sep=';')

    # US derived share prices daily
    qis = sf.load_derived_shareprices(variant='daily', market='us', refresh_days=INFINITY_DAYS, index=[sf_cols.TICKER, sf_cols.DATE])
    t = [t for t in TEST_TICKERS if t in qis.index]
    qis_test = qis.loc[t]
    qis_test.to_csv(SIMFIN_TEST_DATA_PATH / "us-derived-shareprices-daily.csv", sep=';')

    # sf.set_data_dir(SIMFIN_TEST_DATA_PATH)
    # qis_trunc = sf.load_derived_shareprices(variant='daily', market='us', refresh_days=INFINITY_DAYS,
    #                                      index=[sf_cols.TICKER, sf_cols.DATE])

    print("Income statements loaded from SimFin")


if __name__ == "__main__":
    main()
