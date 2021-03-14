import ssl
import logging
import hmac
import json
import hashlib
from multidict import CIMultiDictProxy
from typing import List, Optional

from cryptoxlib.CryptoXLibClient import CryptoXLibClient, RestCallType
from cryptoxlib.clients.bitvavo import enums
from cryptoxlib.clients.bitvavo.exceptions import BitvavoException
from cryptoxlib.clients.bitvavo.functions import map_pair
from cryptoxlib.Pair import Pair
from cryptoxlib.WebsocketMgr import WebsocketMgr, Subscription
from cryptoxlib.clients.bitvavo.BitvavoWebsocket import BitvavoWebsocket


LOG = logging.getLogger(__name__)


class BitvavoClient(CryptoXLibClient):
    REST_API_URI = "https://api.bitvavo.com/v2/"
    VALIDITY_WINDOW_MS = 5000

    def __init__(self, api_key: str = None, sec_key: str = None, api_trace_log: bool = False,
                 ssl_context: ssl.SSLContext = None) -> None:
        super().__init__(api_trace_log, ssl_context)

        self.api_key = api_key
        self.sec_key = sec_key

    def _get_rest_api_uri(self) -> str:
        return self.REST_API_URI

    def _sign_payload(self, rest_call_type: RestCallType, resource: str, data: dict = None, params: dict = None, headers: dict = None) -> None:
        timestamp = self._get_current_timestamp_ms()

        resource_string = resource

        if params is not None and len(params) > 0:
            params_string = '&'.join([f"{key}={val}" for key, val in params.items()])
            if "?" in resource:
                resource_string += "&"
            else:
                resource_string += "?"
            resource_string += params_string

        signature_string = str(timestamp) + rest_call_type.value + '/v2/' + resource_string
        if data is not None:
            signature_string += json.dumps(data, separators=(',',':'))

        LOG.debug(f"Signature input string: {signature_string}")
        signature = hmac.new(self.sec_key.encode('utf-8'), signature_string.encode('utf-8'), hashlib.sha256).hexdigest()

        headers['Bitvavo-Access-Key'] = self.api_key
        headers['Bitvavo-Access-Signature'] = signature
        headers['Bitvavo-Access-Timestamp'] = str(timestamp)
        headers['Bitvavo-Access-Window'] = str(self.VALIDITY_WINDOW_MS)

    def _preprocess_rest_response(self, status_code: int, headers: 'CIMultiDictProxy[str]', body: Optional[dict]) -> None:
        if str(status_code)[0] != '2':
            raise BitvavoException(f"BitvavoException: status [{status_code}], response [{body}]")

    def _get_websocket_mgr(self, subscriptions: List[Subscription], startup_delay_ms: int = 0,
                           ssl_context = None) -> WebsocketMgr:
        return BitvavoWebsocket(subscriptions, self.api_key, self.sec_key, ssl_context)

    async def get_time(self) -> dict:
        return await self._create_get("time")

    async def get_exchange_info(self) -> dict:
        return await self._create_get("markets")

    async def get_assets(self) -> dict:
        return await self._create_get("assets")

    async def get_open_orders(self, pair: Pair = None) -> dict:
        get_params = ""
        if pair is not None:
            get_params = f"?market={map_pair(pair)}"

        return await self._create_get(f"ordersOpen{get_params}", signed = True)

    async def create_order(self, pair: Pair, type: enums.OrderType, side: enums.OrderSide, amount: str = None,
                                 price: str = None, amount_quote: str = None, time_in_force: enums.TimeInForce = None,
                                 self_trade_prevention: enums.SelfTradePrevention = None,
                                 prevent_limit_immediate_fill: bool = None, disable_market_protection: bool = None,
                                 full_response: bool = None) -> dict:
        data = self._clean_request_params({
            "market": map_pair(pair),
            "side": side.value,
            "orderType": type.value,
            "amount": amount,
            "price": price,
            "amountQuote": amount_quote,
            "postOnly": prevent_limit_immediate_fill,
            "disableMarketProtection": disable_market_protection,
            "responseRequired": full_response
        })

        if time_in_force is not None:
            data['timeInForce'] = time_in_force.value

        if time_in_force is not None:
            data['selfTradePrevention'] = self_trade_prevention.value

        return await self._create_post("order", data = data, signed = True)

    async def cancel_order(self, pair: Pair, order_id: str) -> dict:
        params = self._clean_request_params({
            "market": map_pair(pair),
            "orderId": order_id
        })

        return await self._create_delete("order", params = params, signed = True)

    async def get_balance(self, coin: str = None) -> dict:
        params = self._clean_request_params({
            "symbol": coin
        })

        return await self._create_get("balance", params = params, signed = True)

    async def get_24h_price_ticker(self, pair: Pair = None) -> dict:
        get_params = ""
        if pair is not None:
            get_params = f"?market={map_pair(pair)}"

        return await self._create_get(f"ticker/24h{get_params}", signed = True)

    async def get_price_ticker(self, pair: Pair = None) -> dict:
        get_params = ""
        if pair is not None:
            get_params = f"?market={map_pair(pair)}"

        return await self._create_get(f"ticker/price{get_params}", signed = True)

    async def get_best_orderbook_ticker(self, pair: Optional[Pair] = None) -> dict:
        get_params = ""
        if pair is not None:
            get_params = f"?market={map_pair(pair)}"

        return await self._create_get(f"ticker/book{get_params}", signed = True)
