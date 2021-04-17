import ssl
import logging
import hmac
import hashlib
from multidict import CIMultiDictProxy
from typing import Optional

from cryptoxlib.CryptoXLibClient import CryptoXLibClient, RestCallType
from cryptoxlib.clients.binance.exceptions import BinanceRestException

LOG = logging.getLogger(__name__)


class BinanceCommonClient(CryptoXLibClient):
    def __init__(self, api_key: str = None, sec_key: str = None, api_trace_log: bool = False,
                 ssl_context: ssl.SSLContext = None) -> None:
        super().__init__(api_trace_log, ssl_context)

        self.api_key = api_key
        self.sec_key = sec_key

    def _sign_payload(self, rest_call_type: RestCallType, resource: str, data: dict = None, params: dict = None, headers: dict = None) -> None:
        params_string = ""
        data_string = ""

        if params is not None and len(params) > 0:
            params_string = '&'.join([f"{key}={val}" for key, val in params.items()])

        if data is not None and len(data) > 0:
            data_string = '&'.join(["{}={}".format(param[0], param[1]) for param in data])

        m = hmac.new(self.sec_key.encode('utf-8'), (params_string + data_string).encode('utf-8'), hashlib.sha256)

        params['signature'] = m.hexdigest()

    def _preprocess_rest_response(self, status_code: int, headers: 'CIMultiDictProxy[str]', body: Optional[dict]) -> None:
        if str(status_code)[0] != '2':
            raise BinanceRestException(status_code, body)

    def _get_header(self):
        header = {
            'Accept': 'application/json',
            "X-MBX-APIKEY": self.api_key
        }

        return header