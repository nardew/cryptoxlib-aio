import asyncio
import logging
import os
import pytest

from cryptolib.CryptoLib import CryptoLib
from cryptolib.clients.bitforex import enums
from cryptolib.Pair import Pair
from cryptolib.clients.bitforex.exceptions import BitforexException

LOG = logging.getLogger("cryptolib")
LOG.setLevel(logging.DEBUG)
LOG.addHandler(logging.StreamHandler())

api_key = os.environ['BITFOREXAPIKEY']
sec_key = os.environ['BITFOREXSECKEY']

bitforex = CryptoLib.create_bitforex_client(api_key, sec_key)

@pytest.mark.asyncio
async def test_exchange_info():
    result = await bitforex.get_exchange_info()
    assert True

