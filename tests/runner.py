from os import environ as env
import pathlib

import pinon as pn

TEST_PATH = pathlib.Path(__file__).parent
SIMFIN_TEST_DATA_PATH = TEST_PATH / 'simfin_test_data'
env['SIMFIN_DATA_PATH'] = SIMFIN_TEST_DATA_PATH.absolute().as_posix()

def main():
    config = pn.Config('master', 'V', 15)
    m = pn.DerivedBases(config)
    m.run_price_ratios()
    print('Here')


if __name__ == "__main__":
    main()