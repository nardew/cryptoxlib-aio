import unittest
import os
import logging
import datetime

from cryptoxlib.CryptoXLib import CryptoXLib
from cryptoxlib.clients.bitpanda import enums
from cryptoxlib.Pair import Pair
from cryptoxlib.clients.bitpanda.exceptions import BitpandaRestException

from CryptoXLibTest import CryptoXLibTest

api_key = os.environ['AAXAPIKEY']
sec_key = os.environ['AAXSECKEY']


class BitpandaRestApi(CryptoXLibTest):
    @classmethod
    def initialize(cls) -> None:
        cls.client = CryptoXLib.create_aax_client(api_key, sec_key)
        cls.print_logs = True
        cls.log_level = logging.DEBUG

    def check_positive_response(self, response):
        return str(response['status_code'])[0] == '2'

    async def test_get_exchange_info(self):
        response = await self.client.get_exchange_info()
        self.assertTrue(self.check_positive_response(response))

    async def test_get_funds(self):
        response = await self.client.get_funds()
        self.assertTrue(self.check_positive_response(response))


if __name__ == '__main__':
    unittest.main()