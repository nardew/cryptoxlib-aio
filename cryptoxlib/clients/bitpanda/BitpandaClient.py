import ssl
import logging
import datetime
import pytz
from multidict import CIMultiDictProxy
from typing import List, Optional

from cryptoxlib.CryptoXLibClient import CryptoXLibClient, RestCallType
from cryptoxlib.clients.bitpanda import enums
from cryptoxlib.clients.bitpanda.exceptions import BitpandaRestException
from cryptoxlib.clients.bitpanda.functions import map_pair
from cryptoxlib.Pair import Pair
from cryptoxlib.WebsocketMgr import WebsocketMgr, Subscription
from cryptoxlib.clients.bitpanda.BitpandaWebsocket import BitpandaWebsocket


LOG = logging.getLogger(__name__)


class BitpandaClient(CryptoXLibClient):
    REST_API_URI = "https://api.exchange.bitpanda.com/public/v1/"

    def __init__(self, api_key: str = None, api_trace_log: bool = False,
                 ssl_context: ssl.SSLContext = None) -> None:
        super().__init__(api_trace_log, ssl_context)

        self.api_key = api_key

    def _get_rest_api_uri(self) -> str:
        return self.REST_API_URI

    def _sign_payload(self, rest_call_type: RestCallType, resource: str, data: dict = None, params: dict = None, headers: dict = None) -> None:
        pass

    def _preprocess_rest_response(self, status_code: int, headers: 'CIMultiDictProxy[str]', body: Optional[dict]) -> None:
        if str(status_code)[0] != '2':
            raise BitpandaRestException(status_code, body)

    def _get_websocket_mgr(self, subscriptions: List[Subscription], ssl_context = None) -> WebsocketMgr:
        return BitpandaWebsocket(subscriptions, self.api_key, ssl_context)

    async def get_currencies(self) -> dict:
        return await self._create_get("currencies")

    async def get_account_balances(self) -> dict:
        return await self._create_get("account/balances", headers = self._get_header())

    async def get_account_fees(self) -> dict:
        return await self._create_get("account/fees", headers = self._get_header())

    async def get_account_orders(self, from_timestamp: datetime.datetime = None, to_timestamp: datetime.datetime = None,
                                 pair: Pair = None, with_cancelled_and_rejected: str = None,
                                 with_just_filled_inactive: str = None,
                                 with_just_orders: str = None, max_page_size: str = None, cursor: str = None) -> dict:
        params = BitpandaClient._clean_request_params({
            "with_cancelled_and_rejected": with_cancelled_and_rejected,
            "with_just_filled_inactive": with_just_filled_inactive,
            "with_just_orders": with_just_orders,
            "max_page_size": max_page_size,
            "cursor": cursor,
        })

        if pair is not None:
            params["instrument_code"] = map_pair(pair)

        if from_timestamp is not None:
            params["from"] = from_timestamp.astimezone(pytz.utc).isoformat()

        if to_timestamp is not None:
            params["to"] = to_timestamp.astimezone(pytz.utc).isoformat()

        return await self._create_get("account/orders", params = params, headers = self._get_header())

    async def get_account_order(self, order_id: str) -> dict:
        return await self._create_get("account/orders/" + order_id, headers = self._get_header())

    async def get_account_order_trades(self, order_id: str) -> dict:
        return await self._create_get("account/orders/" + order_id + "/trades", headers = self._get_header())

    async def get_account_trades(self, from_timestamp: datetime.datetime = None, to_timestamp: datetime.datetime = None,
                                 pair: Pair = None, max_page_size: str = None, cursor: str = None) -> dict:
        params = BitpandaClient._clean_request_params({
            "max_page_size": max_page_size,
            "cursor": cursor,
        })

        if pair is not None:
            params["instrument_code"] = map_pair(pair)

        if from_timestamp is not None:
            params["from"] = from_timestamp.astimezone(pytz.utc).isoformat()

        if to_timestamp is not None:
            params["to"] = to_timestamp.astimezone(pytz.utc).isoformat()

        return await self._create_get("account/trades", params = params, headers = self._get_header())

    async def get_account_trade(self, trade_id: str) -> dict:
        return await self._create_get("account/trades/" + trade_id, headers = self._get_header())

    async def get_account_trading_volume(self) -> dict:
        return await self._create_get("account/trading-volume", headers = self._get_header())

    async def create_market_order(self, pair: Pair, side: enums.OrderSide, amount: str, client_id: str = None) -> dict:
        data = {
            "instrument_code": map_pair(pair),
            "side": side.value,
            "type": enums.OrderType.MARKET.value,
            "amount": amount
        }

        if client_id is not None:
            data['client_id'] = client_id

        return await self._create_post("account/orders", data = data, headers = self._get_header())

    async def create_limit_order(self, pair: Pair, side: enums.OrderSide, amount: str, limit_price: str,
                                 time_in_force: enums.TimeInForce = None, client_id: str = None) -> dict:
        data = {
            "instrument_code": map_pair(pair),
            "side": side.value,
            "type": enums.OrderType.LIMIT.value,
            "amount": amount,
            "price": limit_price
        }

        if client_id is not None:
            data['client_id'] = client_id

        if time_in_force is not None:
            data['time_in_force'] = time_in_force.value

        return await self._create_post("account/orders", data = data, headers = self._get_header())

    async def create_stop_limit_order(self, pair: Pair, side: enums.OrderSide, amount: str, limit_price: str,
                                      stop_price: str,
                                      time_in_force: enums.TimeInForce = None, client_id: str = None) -> dict:
        data = {
            "instrument_code": map_pair(pair),
            "side": side.value,
            "type": enums.OrderType.STOP_LIMIT.value,
            "amount": amount,
            "price": limit_price,
            "trigger_price": stop_price
        }

        if client_id is not None:
            data['client_id'] = client_id

        if time_in_force is not None:
            data['time_in_force'] = time_in_force.value

        return await self._create_post("account/orders", data = data, headers = self._get_header())

    async def delete_account_orders(self, pair: Pair = None) -> dict:
        params = {}

        if pair is not None:
            params["instrument_code"] = map_pair(pair)

        return await self._create_delete("account/orders", params = params, headers = self._get_header())

    async def delete_account_order(self, order_id: str) -> dict:
        return await self._create_delete("account/orders/" + order_id, headers = self._get_header())

    async def get_candlesticks(self, pair: Pair, unit: enums.TimeUnit, period: str, from_timestamp: datetime.datetime,
                               to_timestamp: datetime.datetime) -> dict:
        params = {
            "unit": unit.value,
            "period": period,
            "from": from_timestamp.astimezone(pytz.utc).isoformat(),
            "to": to_timestamp.astimezone(pytz.utc).isoformat(),
        }

        return await self._create_get("candlesticks/" + map_pair(pair), params = params)

    async def get_instruments(self) -> dict:
        return await self._create_get("instruments")

    async def get_order_book(self, pair: Pair, level: str = None) -> dict:
        params = BitpandaClient._clean_request_params({
            "level": level,
        })

        return await self._create_get("order-book/" + map_pair(pair), params = params)

    async def get_time(self) -> dict:
        return await self._create_get("time")

    def _get_header(self):
        header = {
            "Authorization": "Bearer " + self.api_key
        }

        return header