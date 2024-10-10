import pytest
import pathlib
from os import environ as env

import pinon as pn

TEST_PATH = pathlib.Path(__file__).parent
SIMFIN_TEST_DATA_PATH = TEST_PATH / 'simfin_test_data'
env['SIMFIN_DATA_PATH'] = SIMFIN_TEST_DATA_PATH.absolute().as_posix()

class TestPinonValidation:

    def test_1(self):
        config = pn.Config('master', 'V', 15)
        print('Here')

