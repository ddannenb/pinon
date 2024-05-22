from os import environ as env
import pathlib

import pinon as pn
from pinon import Config

TEST_PATH = pathlib.Path(__file__).parent
SIMFIN_TEST_DATA_PATH = TEST_PATH / 'simfin_test_data'
env['SIMFIN_DATA_PATH'] = SIMFIN_TEST_DATA_PATH.absolute().as_posix()

def main():
    config: Config = pn.Config('master', 'V', 15)
    db = pn.DerivedBases(config)
    db.run_derived_bases()
    comps = pn.Comps(config, db)
    comps.run()
    val = pn.Validation(config, db, comps)
    val.run_aroi_regressions()
    val.run_aroi_scores()
    val.run_peer_k_scores()
    val.compile_validation_stats()

    print('Here')


if __name__ == "__main__":
    main()