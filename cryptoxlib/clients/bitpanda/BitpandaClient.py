import ssl
import logging
import datetime
import pytz
from multidict import CIMultiDictProxy
from typing import List, Optional

from cryptoxlib.CryptoXLibClient import CryptoXLibClient, RestCallType
from cryptoxlib.clients.bitpanda import enums
from cryptoxlib.clients.bitpanda.exceptions import BitpandaRestException, BitpandaException
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
        headers["Authorization"] = "Bearer " + self.api_key

    def _preprocess_rest_response(self, status_code: int, headers: 'CIMultiDictProxy[str]', body: Optional[dict]) -> None:
        if str(status_code)[0] != '2':
            raise BitpandaRestException(status_code, body)

    def _get_websocket_mgr(self, subscriptions: List[Subscription], startup_delay_ms: int = 0,
                           ssl_context = None) -> WebsocketMgr:
        return BitpandaWebsocket(subscriptions = subscriptions, api_key = self.api_key, ssl_context = ssl_context,
                                 startup_delay_ms = startup_delay_ms)

    async def get_currencies(self) -> dict:
        return await self._create_get("currencies")
    
    async def get_fee_groups(self) -> dict:
        return await self._create_get("fees")

    async def get_account_balances(self) -> dict:
        return await self._create_get("account/balances", signed = True)

    async def get_account_fees(self) -> dict:
        return await self._create_get("account/fees", signed = True)

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

        return await self._create_get("account/orders", params = params, signed = True)

    async def get_account_order(self, order_id: str) -> dict:
        return await self._create_get("account/orders/" + order_id, signed = True)

    async def get_account_order_trades(self, order_id: str) -> dict:
        return await self._create_get("account/orders/" + order_id + "/trades", signed = True)

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

        return await self._create_get("account/trades", params = params, signed = True)

    async def get_account_trade(self, trade_id: str) -> dict:
        return await self._create_get("account/trades/" + trade_id, signed = True)

    async def get_account_trading_volume(self) -> dict:
        return await self._create_get("account/trading-volume", signed = True)

    async def create_market_order(self, pair: Pair, side: enums.OrderSide, amount: str, client_id: str = None) -> dict:
        data = {
            "instrument_code": map_pair(pair),
            "side": side.value,
            "type": enums.OrderType.MARKET.value,
            "amount": amount
        }

        if client_id is not None:
            data['client_id'] = client_id

        return await self._create_post("account/orders", data = data, signed = True)

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

        return await self._create_post("account/orders", data = data, signed = True)

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

        return await self._create_post("account/orders", data = data, signed = True)

    async def delete_account_orders(self, pair: Pair = None, ids: List[str] = None) -> dict:
        params = {}

        if pair is not None:
            params["instrument_code"] = map_pair(pair)

        if ids is not None:
            params['ids'] = ','.join(ids)

        return await self._create_delete("account/orders", params = params, signed = True)

    async def delete_account_order(self, order_id: str = None, client_id: str = None) -> dict:
        if order_id is None and client_id is None:
            raise BitpandaException('One of order_id/client_id has to be provided.')

        if order_id is not None and client_id is not None:
            raise BitpandaException('Only one of order_id/client_id can be provided.')

        if order_id is not None:
            return await self._create_delete("account/orders/" + order_id, signed = True)
        else:
            return await self._create_delete("account/orders/client/" + client_id, signed = True)

    async def update_order(self, amount: str, order_id: str = None, client_id: str = None) -> dict:
        if order_id is None and client_id is None:
            raise BitpandaException('One of order_id/client_id has to be provided.')

        if order_id is not None and client_id is not None:
            raise BitpandaException('Only one of order_id/client_id can be provided.')

        data = {
            "amount": amount
        }

        if order_id is not None:
            return await self._create_put("account/orders/" + order_id, data = data, signed = True)
        else:
            return await self._create_put("account/orders/client/" + client_id, data = data, signed = True)

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

    async def get_order_book(self, pair: Pair, level: str = None, depth: str = None) -> dict:
        params = BitpandaClient._clean_request_params({
            "level": level,
            "depth": depth
        })

        return await self._create_get("order-book/" + map_pair(pair), params = params)

    async def get_time(self) -> dict:
        return await self._create_get("time")

    async def get_market_tickers(self) -> dict:
        return await self._create_get("market-ticker")

    async def get_market_ticker(self, pair: Pair) -> dict:
        return await self._create_get("market-ticker/" + map_pair(pair))

    async def get_price_tick(self, pair: Pair, from_timestamp: datetime.datetime = None,
                               to_timestamp: datetime.datetime = None) -> dict:
        params = {}

        if from_timestamp is not None:
            params['from'] = from_timestamp.astimezone(pytz.utc).isoformat()

        if to_timestamp is not None:
            params['to'] = to_timestamp.astimezone(pytz.utc).isoformat()


        return await self._create_get("price-ticks/" + map_pair(pair), params = params)

    async def create_deposit_crypto_address(self, currency: str) -> dict:
        data = {
            "currency": currency
        }

        return await self._create_post("account/deposit/crypto", data = data, signed = True)

    async def get_deposit_crypto_address(self, currency: str) -> dict:
        return await self._create_get("account/deposit/crypto/" + currency, signed = True)

    async def get_fiat_deposit_info(self) -> dict:
        return await self._create_get("account/deposit/fiat/EUR", signed = True)

    async def withdraw_crypto(self, currency: str, amount: str, address: str, destination_tag: str = None) -> dict:
        data = {
            'currency': currency,
            'amount': amount,
            'recipient': {
                'address': address
            }
        }

        if destination_tag is not None:
            data['recipient']['destination_tag'] = destination_tag

        return await self._create_post("account/withdraw/crypto", data = data, signed = True)

    async def withdraw_fiat(self, currency: str, amount: str, payout_account_id: str) -> dict:
        data = {
            'currency': currency,
            'amount': amount,
            'payout_account_id': payout_account_id
        }

        return await self._create_post("account/withdraw/fiat", data = data, signed = True)

    async def get_deposits(self, from_timestamp: datetime.datetime = None,
                           to_timestamp: datetime.datetime = None,
                           currency: str = None,
                           max_page_size: int = None,
                           cursor: int = None) -> dict:
        params = self._clean_request_params({
            'currency_code': currency,
            'max_page_size': max_page_size,
            'cursor': cursor
        })

        if from_timestamp is not None:
            params['from'] = from_timestamp.astimezone(pytz.utc).isoformat()

        if to_timestamp is not None:
            params['to'] = to_timestamp.astimezone(pytz.utc).isoformat()

        return await self._create_get("account/deposits", params = params, signed = True)

    async def get_bitpanda_deposits(self, from_timestamp: datetime.datetime = None,
                           to_timestamp: datetime.datetime = None,
                           currency: str = None,
                           max_page_size: int = None,
                           cursor: int = None) -> dict:
        params = self._clean_request_params({
            'currency_code': currency,
            'max_page_size': max_page_size,
            'cursor': cursor
        })

        if from_timestamp is not None:
            params['from'] = from_timestamp.astimezone(pytz.utc).isoformat()

        if to_timestamp is not None:
            params['to'] = to_timestamp.astimezone(pytz.utc).isoformat()

        return await self._create_get("account/deposits/bitpanda", params = params, signed = True)

    async def get_withdrawals(self, from_timestamp: datetime.datetime = None,
                           to_timestamp: datetime.datetime = None,
                           currency: str = None,
                           max_page_size: int = None,
                           cursor: int = None) -> dict:
        params = self._clean_request_params({
            'currency_code': currency,
            'max_page_size': max_page_size,
            'cursor': cursor
        })

        if from_timestamp is not None:
            params['from'] = from_timestamp.astimezone(pytz.utc).isoformat()

        if to_timestamp is not None:
            params['to'] = to_timestamp.astimezone(pytz.utc).isoformat()

        return await self._create_get("account/withdrawals", params = params, signed = True)

    async def get_bitpanda_withdrawals(self, from_timestamp: datetime.datetime = None,
                           to_timestamp: datetime.datetime = None,
                           currency: str = None,
                           max_page_size: int = None,
                           cursor: int = None) -> dict:
        params = self._clean_request_params({
            'currency_code': currency,
            'max_page_size': max_page_size,
            'cursor': cursor
        })

        if from_timestamp is not None:
            params['from'] = from_timestamp.astimezone(pytz.utc).isoformat()

        if to_timestamp is not None:
            params['to'] = to_timestamp.astimezone(pytz.utc).isoformat()

        return await self._create_get("account/withdrawals/bitpanda", params = params, signed = True)

    async def toggle_best_fee_collection(self, indicator: bool) -> dict:
        data = {
            'collect_fees_in_best': indicator
        }

        return await self._create_post("account/fees", data = data, signed = True)

    async def auto_cancel_all_orders(self, timeout_ms: int) -> dict:
        data = {
            'timeout': timeout_ms
        }

        return await self._create_post("account/orders/cancel-all-after", data = data, signed = True)

    async def delete_auto_cancel_all_orders(self) -> dict:
        return await self._create_delete("account/orders/cancel-all-after", signed = True)