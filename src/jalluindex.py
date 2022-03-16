from dataclasses import dataclass
import datetime
from math import floor
import time
from typing import List
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# TODO: Environment variable?
API_URL = "https://oluet-api.xyz/query"

# TODO: Dynamic fetching of product ID?
# Hopefully it won't ever update.
JALOVIINA_ID = 706
PARAMS = {'productID': JALOVIINA_ID}

PRICE_QUERY = gql(
    """
    query getPrice ($productID: ID!) {
        drink (productID: $productID) {
            hinta
        }
    }
    """
)

HISTORY_QUERY = gql(
    """
    query getHistory ($productID: ID!)  {
        pricehistory (productID: $productID) {
            hinta
            date
        } 
    }
    """
)

def millis() -> int:
    return floor(time.time() * 1000)

def parse_date(datestring: str) -> datetime.datetime:
    # Example string:
    #   2021-01-11T00:00:00Z
    return datetime.datetime.strptime(
        datestring[:10],
        '%Y-%m-%d'
    )

@dataclass
class HistoryEntry:
    price: float
    date: datetime.datetime

    def __init__(self, price: float, datestring: str):
        self.price = price
        self.date = parse_date(datestring)

class Jalluindex:
    client: Client
    history: List[HistoryEntry]
    history_cached: int
    price_cached: int
    price: float

    def __init__(self):
        transport = AIOHTTPTransport(url=API_URL)
        self.client = Client(transport=transport, fetch_schema_from_transport=True)
        self.history = []

        self._fetch_history()
        self._fetch_price()

    @property
    def jalluindex(self):
        if abs(millis() - self.price_cached) > 12 * 60 * 60 * 1000:
            self._fetch_price()
        
        return self.price
    
    @property
    def index(self):
        """An alias for jalluindex"""
        return self.jalluindex

    def _fetch_price(self) -> None:
        result = self.client.execute(PRICE_QUERY, variable_values=PARAMS)
        
        if not 'drink' in result:
            logger.error('no drink in price query')
            return
        
        if not 'hinta' in result['drink']:
            logger.error('no price for drink in price query')
            return
        
        self.price = result['drink']['hinta']
        self.price_cached = millis()

    def _fetch_history(self) -> None:
        result = self.client.execute(HISTORY_QUERY, variable_values=PARAMS)

        if not 'pricehistory' in result:
            logger.error('no pricehistory in gql query')
            return
        
        self.history = []
        pricehistory = result['pricehistory']

        for entry in pricehistory:
            self.history.append(
                HistoryEntry(
                    entry['hinta'],
                    entry['date']
                )
            )
        self.history_cached = millis()

if __name__ == '__main__':
    jalluindex = Jalluindex()
    print(jalluindex.jalluindex)
    print(jalluindex.jalluindex)
    print(len(jalluindex.history))