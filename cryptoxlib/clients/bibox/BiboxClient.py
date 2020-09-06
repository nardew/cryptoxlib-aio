import ssl
import logging
import json
import hmac
import hashlib
from multidict import CIMultiDictProxy
from typing import List, Optional

from cryptoxlib.CryptoXLibClient import CryptoXLibClient, RestCallType
from cryptoxlib.clients.bibox import enums
from cryptoxlib.clients.bibox.exceptions import BiboxException
from cryptoxlib.clients.bibox.functions import map_pair
from cryptoxlib.Pair import Pair
from cryptoxlib.WebsocketMgr import WebsocketMgr, Subscription
from cryptoxlib.clients.bibox.BiboxWebsocket import BiboxWebsocket


LOG = logging.getLogger(__name__)


class BiboxClient(CryptoXLibClient):
    REST_API_URI = "https://api.bibox.com/v1/"

    def __init__(self, api_key: str = None, sec_key: str = None, api_trace_log: bool = False,
                 ssl_context: ssl.SSLContext = None) -> None:
        super().__init__(api_trace_log, ssl_context)

        self.api_key = api_key
        self.sec_key = sec_key

    def _get_rest_api_uri(self) -> str:
        return self.REST_API_URI

    def _sign_payload(self, rest_call_type: RestCallType, resource: str, data: dict = None, params: dict = None, headers: dict = None) -> None:
        cmds = data['cmds']

        signature = hmac.new(self.sec_key.encode('utf-8'), cmds.encode('utf-8'), hashlib.md5).hexdigest()

        data['apikey'] = self.api_key
        data['sign'] = signature

        LOG.debug(f"Signed data: {data}")

    def _preprocess_rest_response(self, status_code: int, headers: 'CIMultiDictProxy[str]', body: Optional[dict]) -> None:
        if body is not None and 'error' in body:
            raise BiboxException(f"BiboxException: status [{status_code}], response [{body}]")

    def _get_websocket_mgr(self, subscriptions: List[Subscription], startup_delay_ms: int = 0,
                           ssl_context = None) -> WebsocketMgr:
        return BiboxWebsocket(subscriptions, self.api_key, self.sec_key, ssl_context)

    async def get_ping(self) -> dict:
        data = {
            "cmds": json.dumps([{
                "cmd": "ping",
                "body": {}
            }])
        }

        return await self._create_post("mdata", data = data)

    async def get_pairs(self) -> dict:
        return await self._create_get("mdata?cmd=pairList")

    async def get_exchange_info(self) -> dict:
        params = {
            "cmd": "tradeLimit"
        }

        return await self._create_get("orderpending", params = params)

    async def get_spot_assets(self, full: bool = False) -> dict:
        data = {
            "cmds": json.dumps([{
                "cmd": "transfer/assets",
                "body": {
                    "select": 1 if full else 0
                }
            }])
        }

        return await self._create_post("transfer", data = data, signed = True)

    async def create_order(self, pair: Pair, price: str, quantity: str, order_type: enums.OrderType,
                           order_side: enums.OrderSide) -> dict:
        data = {
            "cmds": json.dumps([{
                "cmd": "orderpending/trade",
                "index": self._get_current_timestamp_ms(),
                "body": {
                    "pair": map_pair(pair),
                    "account_type": 0, # spot account
                    "order_type": order_type.value,
                    "order_side": order_side.value,
                    "price": price,
                    "amount": quantity
                }
            }])
        }

        return await self._create_post("orderpending", data = data, signed = True)

    async def cancel_order(self, order_id: str) -> dict:
        data = {
            "cmds": json.dumps([{
                "cmd": "orderpending/cancelTrade",
                "index": self._get_current_timestamp_ms(),
                "body": {
                    "orders_id": order_id
                }
            }])
        }

        return await self._create_post("orderpending", data = data, signed = True)

