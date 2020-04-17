import ssl
import logging
import hmac
import hashlib
import json
from multidict import CIMultiDictProxy
from typing import List, Tuple, Optional

from cryptoxlib.CryptoXLibClient import CryptoXLibClient, RestCallType
from cryptoxlib.clients.aax import enums
from cryptoxlib.Pair import Pair
from cryptoxlib.clients.aax.exceptions import AAXRestException
from cryptoxlib.WebsocketMgr import WebsocketMgr, Subscription
from cryptoxlib.clients.aax.AAXWebsocket import AAXWebsocket
from cryptoxlib.clients.aax.functions import map_pair

LOG = logging.getLogger(__name__)


class AAXClient(CryptoXLibClient):
    REST_API_URI = "https://api.aax.com/v2/"

    def __init__(self, api_key: str = None, sec_key: str = None, api_trace_log: bool = False,
                 ssl_context: ssl.SSLContext = None) -> None:
        super().__init__(api_trace_log, ssl_context)

        self.api_key = api_key
        self.sec_key = sec_key

    def _get_rest_api_uri(self) -> str:
        return self.REST_API_URI

    def _sign_payload(self, rest_call_type: RestCallType, resource: str, data: dict = None, params: dict = None,
                      headers: dict = None) -> None:
        timestamp = self._get_current_timestamp_ms()

        signature_string = f"{timestamp}:{rest_call_type.value}/v2/{resource}"
        if data is not None:
            signature_string += json.dumps(data)

        LOG.debug(f"Signature input string: {signature_string}")
        signature = hmac.new(self.sec_key.encode('utf-8'), signature_string.encode('utf-8'), hashlib.sha256).hexdigest()

        headers['X-ACCESS-KEY'] = self.api_key
        headers['X-ACCESS-NONCE'] = str(timestamp)
        headers['X-ACCESS-SIGN'] = signature

    def _preprocess_rest_response(self, status_code: int, headers: 'CIMultiDictProxy[str]', body: Optional[dict]) -> None:
        if str(status_code)[0] != '2':
            raise AAXRestException(status_code, body)

    def _get_websocket_mgr(self, subscriptions: List[Subscription], ssl_context = None) -> WebsocketMgr:
        return AAXWebsocket(subscriptions, self.api_key, self.sec_key, ssl_context)

    async def get_exchange_info(self) -> dict:
        return await self._create_get("instruments")

    async def get_funds(self) -> dict:
        return await self._create_get("user/balances", signed = True)