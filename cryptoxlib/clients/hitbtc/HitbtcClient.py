import ssl
import logging
import base64
import datetime
import pytz
from multidict import CIMultiDictProxy
from typing import List, Optional

from cryptoxlib.CryptoXLibClient import CryptoXLibClient, RestCallType
from cryptoxlib.clients.hitbtc import enums
from cryptoxlib.clients.hitbtc.exceptions import HitbtcRestException
from cryptoxlib.clients.hitbtc.functions import map_pair
from cryptoxlib.Pair import Pair
from cryptoxlib.WebsocketMgr import WebsocketMgr, Subscription
from cryptoxlib.clients.hitbtc.HitbtcWebsocket import HitbtcWebsocket


LOG = logging.getLogger(__name__)


class HitbtcClient(CryptoXLibClient):
    REST_API_URI = "https://api.hitbtc.com/api/2/"

    def __init__(self, api_key: str = None, sec_key: str = None, api_trace_log: bool = False,
                 ssl_context: ssl.SSLContext = None) -> None:
        super().__init__(api_trace_log, ssl_context)

        self.api_key = api_key
        self.sec_key = sec_key

    def _get_rest_api_uri(self) -> str:
        return self.REST_API_URI

    def _sign_payload(self, rest_call_type: RestCallType, resource: str, data: dict = None, params: dict = None, headers: dict = None) -> None:
        headers["Authorization"] = "Basic " + base64.b64encode(bytes(f"{self.api_key}:{self.sec_key}", "utf-8")).decode('utf-8')

    def _preprocess_rest_response(self, status_code: int, headers: 'CIMultiDictProxy[str]', body: Optional[dict]) -> None:
        if str(status_code)[0] != '2':
            raise HitbtcRestException(status_code, body)

    def _get_websocket_mgr(self, subscriptions: List[Subscription], startup_delay_ms: int = 0,
                           ssl_context = None) -> WebsocketMgr:
        return HitbtcWebsocket(subscriptions, self.api_key, self.sec_key, ssl_context, startup_delay_ms)

    async def get_currencies(self, currencies: List[str] = None) -> dict:
        params = {}
        if currencies:
            params['currencies'] = ','.join(currencies)

        return await self._create_get("public/currency", params = params)

    async def get_currency(self, currency: str) -> dict:
        return await self._create_get(f"public/currency/{currency}")

    async def get_symbols(self, pairs: List[Pair] = None) -> dict:
        params = {}
        if pairs is not None:
            params['symbols'] = ','.join(map_pair(pair) for pair in pairs)

        return await self._create_get("public/symbol", params = params)

    async def get_symbol(self, pair: Pair) -> dict:
        return await self._create_get(f"public/symbol/{map_pair(pair)}")

    async def get_tickers(self, pairs: List[Pair] = None) -> dict:
        params = {}
        if pairs is not None:
            params['symbols'] = ','.join(map_pair(pair) for pair in pairs)

        return await self._create_get("public/ticker", params = params)

    async def get_ticker(self, pair: Pair) -> dict:
        return await self._create_get(f"public/ticker/{map_pair(pair)}")

    async def get_order_books(self, limit: int = None, pairs: List[Pair] = None) -> dict:
        params = self._clean_request_params({
            "limit": limit
        })

        if pairs is not None:
            params['symbols'] = ','.join(map_pair(pair) for pair in pairs)

        return await self._create_get("public/orderbook", params = params)

    async def get_order_book(self, pair: Pair, limit: int = None, volume: int = None) -> dict:
        params = self._clean_request_params({
            "limit": limit,
            "volume": volume
        })

        return await self._create_get(f"public/orderbook/{map_pair(pair)}", params = params)

    async def get_balance(self) -> dict:
        return await self._create_get(f"trading/balance", signed = True)

    async def create_order(self, pair: Pair, side: enums.OrderSide, type: enums.OrderType, amount: str,
                           price: str = None, stop_price: str = None, time_in_force: enums.TimeInForce = None,
                           client_id: str = None, expire_time: datetime.datetime = None, strict_validate: bool = None,
                           post_only: bool = None) -> dict:
        data = {
            "symbol": map_pair(pair),
            "side": side.value,
            "type": type.value,
            "quantity": amount,
            "price": price,
            "stopPrice": stop_price,
            "clientOrderId": client_id,
            "strictValidate": strict_validate,
            "postOnly": post_only
        }

        if time_in_force is not None:
            data['timeInForce'] = time_in_force.value

        if expire_time:
            data["expireTime"] = expire_time.astimezone(pytz.utc).isoformat()

        return await self._create_post("order", data = data, signed = True)

    async def cancel_orders(self, pair: Pair = None) -> dict:
        params = {}
        if pair is not None:
            params['symbol'] = map_pair(pair)

        return await self._create_delete(f"order", params = params, signed = True)

    async def cancel_order(self, client_id: str) -> dict:
        return await self._create_delete(f"order/{client_id}", signed = True)