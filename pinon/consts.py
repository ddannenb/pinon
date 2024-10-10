import inspect
import pathlib

PROJECT_PATH = pathlib.Path(__file__).parent
HDR_DATA_PATH = PROJECT_PATH / 'api_hdrs'

class EARNING_ESTIMATES:

        TICKER = 'Ticker'
        SEQUENCE = 'Sequence'
        PERIOD_END_DATE = 'Period end date'
        PERIOD_TYPE = 'Period type'
        FISCAL_QTR = 'Fiscal quarter'
        FISCAL_YEAR = 'Fiscal year'
        CAL_QTR = 'Calendar quarter'
        CAL_YEAR = 'Calendar year'

        NUM_ESTS = 'Number of analyst estimates'
        EST_LOW = 'Low estimate'
        EST_HIGH = 'High estimate'
        EST_MEAN = 'Mean estimate'
        ACTUAL = 'Actual'


@staticmethod
def cols(cls):
        """
        Returns the column values in order of declaration
        :param cls:
        :return:
        """
        ex = dir(type('dummy', (object,), {}))
        declared_members = [item for item in inspect.getmembers(cls) if item[0] not in ex]
        all_members_sorted = [item for item in cls.__dict__.keys()]
        res = [(all_members_sorted.index(item[0]), item[0], item[1]) for item in declared_members]
        res_sorted = sorted(res, key=lambda x: x[0])
        return [item[2] for item in res_sorted]

@staticmethod
def gen_headers(hdr_file_path):
        res = {}
        with open(hdr_file_path, 'r') as file:
                for line in file:
                        if line:
                                k,v = line.split('\t', 1)
                                if k[0] != ':':
                                        res[k.strip()] = v.strip()
        return res

COLS_EARNINGS_ESTIMATES = cols(EARNING_ESTIMATES)
SA_API_HDRS = gen_headers(HDR_DATA_PATH / 'api_hdr.txt')
