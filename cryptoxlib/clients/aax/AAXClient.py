import ssl
import logging
import hmac
import hashlib
import json
from multidict import CIMultiDictProxy
from typing import List, Optional

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
        if params is not None:
            signature_string += json.dumps(params)

        LOG.debug(f"Signature input string: {signature_string}")
        signature = hmac.new(self.sec_key.encode('utf-8'), signature_string.encode('utf-8'), hashlib.sha256).hexdigest()

        headers['X-ACCESS-KEY'] = self.api_key
        headers['X-ACCESS-NONCE'] = str(timestamp)
        headers['X-ACCESS-SIGN'] = signature

    def _preprocess_rest_response(self, status_code: int, headers: 'CIMultiDictProxy[str]', body: Optional[dict]) -> None:
        if str(status_code)[0] != '2':
            raise AAXRestException(status_code, body)

    def _get_websocket_mgr(self, subscriptions: List[Subscription], startup_delay_ms: int = 0,
                           ssl_context = None) -> WebsocketMgr:
        return AAXWebsocket(subscriptions, self.api_key, self.sec_key, ssl_context)

    async def get_exchange_info(self) -> dict:
        return await self._create_get("instruments")

    async def get_funds(self) -> dict:
        return await self._create_get("user/balances", signed = True)

    async def get_user_info(self) -> dict:
        return await self._create_get("user/info", signed = True)

    async def create_spot_order(self, pair: Pair, type: enums.OrderType, side: enums.OrderSide,
                           amount: str, price: str = None, stop_price: str = None,
                           time_in_force: enums.TimeInForce = None, client_id: str = None) -> dict:
        data = self._clean_request_params({
            "symbol": map_pair(pair),
            "side": side.value,
            "orderType": type.value,
            "orderQty": amount,
            "price": price,
            "stopPrice": stop_price,
            "clOrdID": client_id
        })

        if time_in_force is not None:
            data['timeInForce'] = time_in_force.value

        return await self._create_post("spot/orders", data = data, signed = True)

    async def update_spot_order(self, order_id: str, amount: str, price: str = None, stop_price: str = None) -> dict:
        data = self._clean_request_params({
            "orderId": order_id,
            "orderQty": amount,
            "price": price,
            "stopPrice": stop_price
        })

        return await self._create_put("spot/orders", data = data, signed = True)

    async def cancel_spot_order(self, order_id: str) -> dict:
        return await self._create_delete(f"spot/orders/cancel/{order_id}", signed = True)

    async def cancel_batch_spot_order(self, pair: Pair, order_id: str = None, client_id: str = None) -> dict:
        data = self._clean_request_params({
            "symbol": map_pair(pair),
            "orderId": order_id,
            "clOrdID": client_id
        })

        return await self._create_delete("spot/orders/cancel/all", data = data, signed = True)

    async def cancel_all_spot_order(self, timeout_ms: int) -> dict:
        data = {
            "timeout": timeout_ms
        }

        return await self._create_post("spot/orders/cancelAllOnTimeout", data = data, signed = True)