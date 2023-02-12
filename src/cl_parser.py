import argparse
import pathlib

PROJ_PATH = pathlib.Path(__file__).parent.parent
DATA_PATH = PROJ_PATH / "data"


class ClParser:
    def __init__(self):
        self.config_path = None
        self.mode = None
        self.argumentParser = argparse.ArgumentParser(description='Processing arguments')
        self.argumentParser.add_argument(dest='config_file', help='Path to configuration file')
        self.argumentParser.add_argument('-m', '--mode', help="pre - preprocess, run - run analysis (default)", default='run', choices=['run', 'pre'])

    def parse_args(self):
        args = self.argumentParser.parse_args()
        self.mode = args.mode
        self.config_path = PROJ_PATH / args.config_file
        if not self.config_path.is_file():
            raise TypeError(f"{self.config_path} is not a valid file")

    def is_pre_mode(self):
        return self.mode == 'pre'

    def is_run_mode(self):
        return self.mode == 'run'


clp = ClParser()
clp.parse_args()
print('Done')
