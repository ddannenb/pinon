import pathlib
import pandas as pd
import simfin as sf

import names as pn_cols
from fundamentals import Fundamentals
from companies import Companies

PROJ_PATH = pathlib.Path(__file__).parent.parent
CONFIG_PATH = PROJ_PATH / "config"
SIMFIN_DATA_PATH = PROJ_PATH / 'simfin_data'
class MasterConfig:
    def __init__(self):
        self.company_details = None
        self.config_path = CONFIG_PATH / f"{config_name}.xlsx"
        if not self.config_path.is_file():
            raise TypeError(f"{self.config_path} is not a valid file")
        print(f"Config file found at: {self.config_path}")

        # Simfin setup
        sf.set_data_dir(SIMFIN_DATA_PATH)
        print(f"Simfin data directory: {SIMFIN_DATA_PATH}")

        sf.load_api_key(CONFIG_PATH / 'simfin_api_key.txt')

    def parse_master_sheet(self):
        master_sheet = pd.read_excel(self.config_path, sheet_name="Master", header=1, nrows=20)
        comp = Companies()
        return master_sheet
