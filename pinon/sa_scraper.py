import requests

SA_SITE_API_URL = 'https://seekingalpha.com/api/v3'
SA_SYMBOL_LOOKUP_PATH_P1_TICKER = '/symbols/{ticker}'
SA_EPS_ESTIMATES_PATH_P1_TICKER_ID = '/symbol_data/estimates?estimates_data_items=eps_normalized_actual,eps_normalized_consensus_low,eps_normalized_consensus_mean,eps_normalized_consensus_high,eps_normalized_num_of_estimates&period_type=quarterly&relative_periods=-3,-2,-1,0,1,2,3,4,5,6,7,8,9,10,11&ticker_ids={ticker_id}'

SA_API_HDRS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'en-US,en;q=0.9',
    # 'Cache-Control': 'no-cache',
    # 'Pragma': 'no-cache',
    # 'Sec-Ch-Ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
}

class SaScraper:
    def __init__(self):
        print('Here')

    def get_ticker_id(self, ticker):
        url = SA_SITE_API_URL + SA_SYMBOL_LOOKUP_PATH_P1_TICKER.format(ticker=ticker)
        res = requests.get(url)
        if res.status_code != 200:
            return None
        res_json = res.json()
        id = res_json.get('data', {}).get('id')
        return None if id is None else int(id)

    def get_earnings_estimates(self, ticker):
        id = self.get_ticker_id(ticker)
        if id is None:
            print(f'Ticker: {ticker} was not found')
            return None

        url = SA_SITE_API_URL + SA_EPS_ESTIMATES_PATH_P1_TICKER_ID.format(ticker_id=id)
        res = requests.get(url, headers=SA_API_HDRS)
        if res.status_code != 200:
            return None
        res_json = res.json()
        print(res_json)
