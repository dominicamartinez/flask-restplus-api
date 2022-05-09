import requests
from urllib.parse import urlencode
import unittest
import json

class TestTakeHomeAPI(unittest.TestCase):

    PRICE_ENDPOINT = "http://localhost:5000/price"
    RATES_ENDPOINT = "http://localhost:5000/rates"

    def test_nonExistEndpoint(self):
        r = requests.get('http://localhost:5000/rate')
        self.assertEqual(r.status_code, 404)

    # This test assumes the initial data information
    def test_priceQuery1InitData(self):
        parameters = {"start":'2015-07-01T07:00:00-05:00', "end":'2015-07-01T12:00:00-05:00'}
        r = requests.get(f"{self.PRICE_ENDPOINT}?{urlencode(parameters)}")
        self.assertEqual(json.loads(r.text),{"price": 1750})

    # This test assumes the initial data information
    def test_priceQuery2InitData(self):
        parameters = {"start":'2015-07-04T15:00:00+00:00', "end":'2015-07-04T20:00:00+00:00'}
        r = requests.get(f"{self.PRICE_ENDPOINT}?{urlencode(parameters)}")
        self.assertEqual(json.loads(r.text),{"price": 2000})

    # This test assumes the initial data information
    def test_priceQuery3InitData(self):
        parameters = {"start":'2015-07-04T07:00:00+05:00', "end":'2015-07-04T20:00:00+05:00'}
        r = requests.get(f"{self.PRICE_ENDPOINT}?{urlencode(parameters)}")
        self.assertEqual(r.text.rstrip(),'"unavailable"')

    def test_ratesPutMethod(self):
        data = { "rates": [{"days": "mon", "times": "0900-2100", "tz": "America/Phoenix","price": 1500}] }
        r = requests.put(self.RATES_ENDPOINT, json=data)
        r = requests.get(self.RATES_ENDPOINT)
        self.assertEqual(json.loads(r.text),data)

    def test_ratesPutMethodValidationTimes(self):
        data = { "rates": [{"days": "mon", "times": "2100-0900", "tz": "America/Phoenix","price": 1500}] }
        r = requests.put(self.RATES_ENDPOINT, json=data)
        self.assertEqual(r.status_code,400)

    def test_ratesPutMethodValidationDays(self):
        data = { "rates": [{"days": "mon,tue", "times": "0900-2100", "tz": "America/Phoenix","price": 1500}] }
        r = requests.put(self.RATES_ENDPOINT, json=data)
        self.assertEqual(r.status_code,400)

    def test_ratesPutMethodValidationTZ(self):
        data = { "rates": [{"days": "mon", "times": "0900-2100", "tz": "America/foobar","price": 1500}] }
        r = requests.put(self.RATES_ENDPOINT, json=data)
        self.assertEqual(r.status_code,400)

    def test_ratesPutMethodValidationPrice(self):
        data = { "rates": [{"days": "mon", "times": "0900-2100", "tz": "America/Phoenix","price": "4f"}] }
        r = requests.put(self.RATES_ENDPOINT, json=data)
        self.assertEqual(r.status_code,400)

if __name__ == '__main__':
    unittest.main()