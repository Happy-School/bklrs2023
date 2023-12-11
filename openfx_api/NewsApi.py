import requests
import datetime as dt
import time

class AlphaVantageApi:
    def __init__(self):
        self.api_key = 'A39CWXNUIKNBORAP'
        self.base_url = 'https://www.alphavantage.co/query'
        self.session = requests.Session()
        self.last_req_time = dt.datetime.now()

    def throttle(self):
        el_s = (dt.datetime.now() - self.last_req_time).total_seconds()
        THROTTLE_TIME = 5  # Adjust the throttle time as needed
        if el_s < THROTTLE_TIME:
            time.sleep(THROTTLE_TIME - el_s)
        self.last_req_time = dt.datetime.now()

    def make_request(self, news_type, tickers='FOREX:EUR', params=None):
        url = f'{self.base_url}?function={news_type}&tickers={tickers}&limit={params}&apikey={self.api_key}'

        self.throttle()

        try:
            response = self.session.get(url, params=params, verify=True)

            if response.status_code == 200:
                return True, response.json()
            else:
                return False, response.json()

        except Exception as error:
            return False, {'Exception': str(error)}

    def get_alpha_vantage_data(self, limit=1):
        news_type = 'NEWS_SENTIMENT'
        params = {'limit': limit}
        return self.make_request(news_type, params=params)
