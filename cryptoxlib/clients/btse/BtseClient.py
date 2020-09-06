import ssl
import logging
import datetime
import pytz
import hmac
import hashlib
import json
from multidict import CIMultiDictProxy
from typing import List, Optional

from cryptoxlib.CryptoXLibClient import CryptoXLibClient, RestCallType
from cryptoxlib.clients.btse import enums
from cryptoxlib.clients.btse.exceptions import BtseRestException
from cryptoxlib.clients.btse.functions import map_pair
from cryptoxlib.Pair import Pair
from cryptoxlib.WebsocketMgr import WebsocketMgr, Subscription
from cryptoxlib.clients.btse.BtseWebsocket import BtseWebsocket


LOG = logging.getLogger(__name__)


class BtseClient(CryptoXLibClient):
    REST_API_URI = "https://api.btse.com/spot/api/v3.1/"

    def __init__(self, api_key: str = None, sec_key: str = None, api_trace_log: bool = False,
                 ssl_context: ssl.SSLContext = None) -> None:
        super().__init__(api_trace_log, ssl_context)

        self.api_key = api_key
        self.sec_key = sec_key

    def _get_rest_api_uri(self) -> str:
        return self.REST_API_URI

    def _sign_payload(self, rest_call_type: RestCallType, resource: str, data: dict = None, params: dict = None, headers: dict = None) -> None:
        timestamp = self._get_current_timestamp_ms()

        signature_string = f"/api/v3.1/{resource}{timestamp}"
        if data is not None:
            signature_string += json.dumps(data)

        LOG.debug(f"Signature input string: {signature_string}")
        signature = hmac.new(self.sec_key.encode('utf-8'), signature_string.encode('utf-8'), hashlib.sha384).hexdigest()

        headers['btse-api'] = self.api_key
        headers['btse-nonce'] = str(timestamp)
        headers['btse-sign'] = signature

    def _preprocess_rest_response(self, status_code: int, headers: 'CIMultiDictProxy[str]', body: Optional[dict]) -> None:
        if str(status_code)[0] != '2':
            raise BtseRestException(status_code, body)

    def _get_websocket_mgr(self, subscriptions: List[Subscription], startup_delay_ms: int = 0,
                           ssl_context = None) -> WebsocketMgr:
        return BtseWebsocket(subscriptions, self.api_key, self.sec_key, ssl_context)

    def _get_header(self):
        header = {
            'Accept': 'application/json'
        }

        return header

    async def get_time(self) -> dict:
        return await self._create_get("time", headers = self._get_header())

    async def get_exchange_info(self, pair: Pair = None) -> dict:
        params = {}

        if pair is not None:
            params['symbol'] = map_pair(pair)

        return await self._create_get("market_summary", params = params, headers = self._get_header())

    async def get_order_book(self, pair: Pair = None, depth: int = None) -> dict:
        params = self._clean_request_params({
            "depth": depth,
        })

        if pair is not None:
            params['symbol'] = map_pair(pair)

        return await self._create_get("orderbook/L2", params = params, headers = self._get_header())

    async def get_price(self, pair: Pair = None) -> dict:
        params = {}

        if pair is not None:
            params['symbol'] = map_pair(pair)

        return await self._create_get("price", params = params, headers = self._get_header())

    async def get_funds(self) -> dict:
        return await self._create_get("user/wallet", headers = self._get_header(), signed = True)

    async def get_open_orders(self, pair: Pair) -> dict:
        params = {
            'symbol': map_pair(pair)
        }
        return await self._create_get("user/open_orders", params = params, headers = self._get_header(), signed = True)

    async def get_fees(self, pair: Pair = None) -> dict:
        params = {}

        if pair is not None:
            params['symbol'] = map_pair(pair)

        return await self._create_get("user/fees", params = params, headers = self._get_header(), signed = True)

    async def create_order(self, pair: Pair, side: enums.OrderSide, type: enums.OrderType,
                                 amount: str, price: str = None, stop_price: str = None, post_only = None,
                                 trail_value: str = None, trigger_price: str = None,
                                 transction_type: enums.TransactionType = None,
                                 time_in_force: enums.TimeInForce = None, client_id: str = None) -> dict:
        data = self._clean_request_params({
            "symbol": map_pair(pair),
            "side": side.value,
            "type": type.value,
            "size": amount,
            "price": price,
            "stopPrice": stop_price,
            "postOnly": post_only,
            "clOrderID": client_id,
            "trailValue": trail_value,
            "triggerPrice": trigger_price
        })

        if time_in_force is not None:
            data['time_in_force'] = time_in_force.value

        if transction_type is not None:
            data['txType'] = transction_type.value

        return await self._create_post("order", data = data, headers = self._get_header(), signed = True)

    async def cancel_order(self, pair: Pair, order_id: str = None, client_order_id: str = None) -> dict:
        params = self._clean_request_params({
            "symbol": map_pair(pair),
            "orderId": order_id,
            "clOrderID": client_order_id
        })

        return await self._create_delete("order", params = params, headers = self._get_header(), signed = True)