import requests
from requests import Session
import pandas as pd
from consts import EARNING_ESTIMATES, SA_API_HDRS


SA_SITE_API_URL = 'https://seekingalpha.com/api/v3'
SA_SYMBOL_LOOKUP_PATH_P1_TICKER = '/symbols/{ticker}'
SA_EPS_ESTIMATES_PATH_P1_TICKER_ID = '/symbol_data/estimates?estimates_data_items=eps_normalized_actual,eps_normalized_consensus_low,eps_normalized_consensus_mean,eps_normalized_consensus_high,eps_normalized_num_of_estimates&period_type=quarterly&relative_periods=-3,-2,-1,0,1,2,3,4,5,6,7,8,9,10,11&ticker_ids={ticker_id}'

# SA_API_HDRS = {
#     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
#     'Accept-Encoding': 'gzip, deflate, br, zstd',
#     'Accept-Language': 'en-US,en;q=0.9',
#     # 'Cache-Control': 'no-cache',
#     # 'Pragma': 'no-cache',
#     # 'Sec-Ch-Ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
#     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
# }

class SaScraper:
    def __init__(self):
        print('Here')

    def get_ticker_id(self, ticker):
        url = SA_SITE_API_URL + SA_SYMBOL_LOOKUP_PATH_P1_TICKER.format(ticker=ticker)
        session = Session()
        # session.verify = '/Users/daved/Dev/pinon/tests/certs/charles-ssl-proxying-certificate.pem'
        res = session.get(url, headers=SA_API_HDRS)
        if res.status_code != 200:
            print(f'get_ticker API request failed with error code: {res.status_code}')
            return None
        res_json = res.json()
        id = res_json.get('data', {}).get('id')
        return None if id is None else int(id)

    def parse_tickers(self, tickers):
        """
        Parse multiple tickers as input
        :param tickers:
        :returns: List of tickers
        :raise: TypeError
        """
        if isinstance(tickers, list):
            ts = tickers
        elif isinstance(tickers, str):
            tickers = tickers.replace(' ', '')
            ts = tickers.split(',')
        else:
            raise TypeError(f'pinon: Invalid type for argument tickers: {type(tickers)}. Use a list or command separated string')
        return ts

    def get_earnings_estimates(self, tickers, period='quarterly'):
        eests = pd.DataFrame(columns=[])
        ts = self.parse_tickers(tickers)


    def get_earnings_estimate(self, ticker):
        ticker_id = self.get_ticker_id(ticker)
        if ticker_id is None:
            print(f'Ticker: {ticker} was not found.')
            return None

        url = SA_SITE_API_URL + SA_EPS_ESTIMATES_PATH_P1_TICKER_ID.format(ticker_id=ticker_id)
        res = requests.get(url, headers=SA_API_HDRS)
        if res.status_code != 200:
            return None
        res_json = res.json()
        try:
            est_json = res_json['estimates'][f'{ticker_id}']
        except:
            print(f'Could not recurse into response for earnings estimates for ticker: {ticker}.')
            return None
        seq = sorted([int(item) for item in list(est_json['eps_normalized_num_of_estimates'].keys())])
        num_items = len(seq)
        df_data = {
            EARNING_ESTIMATES.TICKER: ([ticker]*num_items),
            EARNING_ESTIMATES.SEQUENCE: seq,
            EARNING_ESTIMATES.PERIOD_END_DATE: [est_json['eps_normalized_num_of_estimates'][str(s)][0]['period']['periodenddate'] for s in seq],
            EARNING_ESTIMATES.PERIOD_TYPE: [est_json['eps_normalized_num_of_estimates'][str(s)][0]['period']['periodtypeid'] for s in seq],
            EARNING_ESTIMATES.FISCAL_QTR: [est_json['eps_normalized_num_of_estimates'][str(s)][0]['period']['fiscalquarter'] for s in seq],
            EARNING_ESTIMATES.FISCAL_YEAR: [est_json['eps_normalized_num_of_estimates'][str(s)][0]['period']['fiscalyear'] for s in seq],
            EARNING_ESTIMATES.CAL_QTR: [est_json['eps_normalized_num_of_estimates'][str(s)][0]['period']['calendarquarter'] for s in seq],
            EARNING_ESTIMATES.CAL_YEAR: [est_json['eps_normalized_num_of_estimates'][str(s)][0]['period']['calendaryear'] for s in seq],
            EARNING_ESTIMATES.NUM_ESTS: [est_json['eps_normalized_num_of_estimates'][str(s)][0]['dataitemvalue'] for s in seq],
            EARNING_ESTIMATES.EST_LOW: [est_json['eps_normalized_consensus_low'][str(s)][0]['dataitemvalue'] for s in seq],
            EARNING_ESTIMATES.EST_HIGH: [est_json['eps_normalized_consensus_high'][str(s)][0]['dataitemvalue'] for s in seq],
            EARNING_ESTIMATES.EST_MEAN: [est_json['eps_normalized_consensus_mean'][str(s)][0]['dataitemvalue'] for s in seq],
            EARNING_ESTIMATES.ACTUAL: ([None]*num_items)
        }
        for s in est_json['eps_normalized_actual']:
            ndx = seq.index(int(s))
            df_data[EARNING_ESTIMATES.ACTUAL][ndx] = est_json['eps_normalized_actual'][s][0]['dataitemvalue']
        ee = pd.DataFrame(df_data)

        return ee

