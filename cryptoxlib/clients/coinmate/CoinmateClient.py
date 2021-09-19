import ssl
import logging
import datetime
import hmac
import hashlib
import pytz
from multidict import CIMultiDictProxy
from typing import List, Optional

from cryptoxlib.CryptoXLibClient import CryptoXLibClient, RestCallType
from cryptoxlib.clients.coinmate.functions import map_pair
from cryptoxlib.clients.coinmate.exceptions import CoinmateRestException, CoinmateException
from cryptoxlib.clients.coinmate import enums
from cryptoxlib.clients.coinmate.CoinmateWebsocket import CoinmateWebsocket
from cryptoxlib.Pair import Pair
from cryptoxlib.WebsocketMgr import WebsocketMgr, Subscription


LOG = logging.getLogger(__name__)


class CoinmateClient(CryptoXLibClient):
    REST_API_URI = "https://coinmate.io/api/"

    def __init__(self, user_id: str = None, api_key: str = None, sec_key: str = None, api_trace_log: bool = False,
                 ssl_context: ssl.SSLContext = None) -> None:
        super().__init__(api_trace_log, ssl_context)

        self.user_id = user_id
        self.api_key = api_key
        self.sec_key = sec_key

    def _get_rest_api_uri(self) -> str:
        return self.REST_API_URI

    def _sign_payload(self, rest_call_type: RestCallType, resource: str, data: dict = None, params: dict = None, headers: dict = None) -> None:
        nonce = self._get_current_timestamp_ms()
        input_message = str(nonce) + str(self.user_id) + self.api_key

        m = hmac.new(self.sec_key.encode('utf-8'), input_message.encode('utf-8'), hashlib.sha256)

        params['signature'] = m.hexdigest().upper()
        params['clientId'] = self.user_id
        params['publicKey'] = self.api_key
        params['nonce'] = nonce

    def _preprocess_rest_response(self, status_code: int, headers: 'CIMultiDictProxy[str]', body: Optional[dict]) -> None:
        if str(status_code)[0] != '2':
            raise CoinmateRestException(status_code, body)
        else:
            if "error" in body and body['error'] is True:
                raise CoinmateRestException(status_code, body)

    def _get_websocket_mgr(self, subscriptions: List[Subscription], startup_delay_ms: int = 0,
                           ssl_context = None) -> WebsocketMgr:
        return CoinmateWebsocket(subscriptions = subscriptions,
                                 user_id = self.user_id, api_key = self.api_key, sec_key = self.sec_key,
                                 ssl_context = ssl_context,
                                 startup_delay_ms = startup_delay_ms)

    async def get_exchange_info(self) -> dict:
        return await self._create_get("tradingPairs")

    async def get_currency_pairs(self) -> dict:
        return await self._create_get("products")

    async def get_order_book(self, pair: Pair, group: bool = False) -> dict:
        params = CoinmateClient._clean_request_params({
            "currencyPair": map_pair(pair),
            "groupByPriceLimit": group
        })

        return await self._create_get("orderBook", params = params)

    async def get_ticker(self, pair: Pair) -> dict:
        params = CoinmateClient._clean_request_params({
            "currencyPair": map_pair(pair)
        })

        return await self._create_get("ticker", params = params)

    async def get_transactions(self, minutes_history: int, currency_pair: Pair = None) -> dict:
        params = CoinmateClient._clean_request_params({
            "minutesIntoHistory": minutes_history
        })

        if currency_pair is not None:
            params['currencyPair'] = map_pair(currency_pair)

        return await self._create_get("transactions", params = params)

    async def get_balances(self) -> dict:
        return await self._create_post("balances", signed = True)

    async def get_fees(self, pair: Pair = None) -> dict:
        params = {}
        if pair is not None:
            params['currencyPair'] = map_pair(pair)

        return await self._create_post("traderFees", params = params, signed = True)

    async def get_transaction_history(self, offset: int = None, limit: int = None, ascending = False, order_id: str = None,
                                      from_timestamp: datetime.datetime = None, to_timestamp: datetime.datetime = None) -> dict:
        params = CoinmateClient._clean_request_params({
            "offset": offset,
            "limit": limit,
            "orderId": order_id
        })

        if ascending is True:
            params['sort'] = 'ASC'
        else:
            params['sort'] = 'DESC'

        if from_timestamp is not None:
            params["timestampFrom"] = from_timestamp.astimezone(pytz.utc).isoformat()

        if to_timestamp is not None:
            params["timestampTo"] = to_timestamp.astimezone(pytz.utc).isoformat()

        return await self._create_post("transactionHistory", params = params, signed = True)

    async def get_trade_history(self, limit: int = None, ascending = False, order_id: str = None, last_id: str = None,
                                      from_timestamp: datetime.datetime = None, to_timestamp: datetime.datetime = None,
                                pair: Pair = None) -> dict:
        params = CoinmateClient._clean_request_params({
            "limit": limit,
            "orderId": order_id,
            "lastId": last_id
        })

        if pair is not None:
            params['currencyPair'] = map_pair(pair)

        if ascending is True:
            params['sort'] = 'ASC'
        else:
            params['sort'] = 'DESC'

        if from_timestamp is not None:
            params["timestampFrom"] = from_timestamp.astimezone(pytz.utc).isoformat()

        if to_timestamp is not None:
            params["timestampTo"] = to_timestamp.astimezone(pytz.utc).isoformat()

        return await self._create_post("tradeHistory", params = params, signed = True)

    async def get_transfer(self, transaction_id: str) -> dict:
        params = CoinmateClient._clean_request_params({
            "transactionId": transaction_id
        })

        return await self._create_post("transfer", params = params, signed = True)

    async def get_transfer_history(self, limit: int = None, ascending = False, last_id: str = None,
                                      from_timestamp: datetime.datetime = None, to_timestamp: datetime.datetime = None,
                                currency: str = None) -> dict:
        params = CoinmateClient._clean_request_params({
            "limit": limit,
            "lastId": last_id,
            "currency": currency
        })

        if ascending is True:
            params['sort'] = 'ASC'
        else:
            params['sort'] = 'DESC'

        if from_timestamp is not None:
            params["timestampFrom"] = from_timestamp.astimezone(pytz.utc).isoformat()

        if to_timestamp is not None:
            params["timestampTo"] = to_timestamp.astimezone(pytz.utc).isoformat()

        return await self._create_post("transferHistory", params = params, signed = True)

    async def get_order_history(self, pair: Pair, limit: int = None) -> dict:
        params = CoinmateClient._clean_request_params({
            "currencyPair": map_pair(pair),
            "limit": limit
        })

        return await self._create_post("orderHistory", params = params, signed = True)

    async def get_open_orders(self, pair: Pair = None) -> dict:
        params = {}

        if pair is not None:
            params["currencyPair"] = map_pair(pair)

        return await self._create_post("openOrders", params = params, signed = True)

    async def get_order(self, order_id: str = None, client_id: str = None) -> dict:
        if not (bool(order_id) ^ bool(client_id)):
            raise CoinmateException("One and only one of order_id and client_id can be provided.")

        params = {}

        if order_id is not None:
            endpoint = "orderById"
            params["orderId"] = order_id
        else:
            endpoint = "order"
            params["clientOrderId"] = client_id

        return await self._create_post(endpoint, params = params, signed = True)

    async def cancel_order(self, order_id: str) -> dict:
        params = {
            "orderId": order_id
        }

        return await self._create_post("cancelOrder", params = params, signed = True)

    async def cancel_all_orders(self, pair: Pair = None) -> dict:
        params = {}

        if pair is not None:
            params["currencyPair"] = map_pair(pair)

        return await self._create_post("cancelAllOpenOrders", params = params, signed = True)

    async def create_order(self, type: enums.OrderType,
                           pair: Pair,
                           side: enums.OrderSide,
                           amount: str,
                           price: str = None,
                           stop_price: str = None,
                           trailing: bool = None,
                           hidden: bool = None,
                           time_in_force: enums.TimeInForce = None,
                           post_only: bool = None,
                           client_id: str = None) -> dict:
        params = CoinmateClient._clean_request_params({
            "currencyPair": map_pair(pair),
            "price": price,
            "stopPrice": stop_price,
            "clientOrderId": client_id
        })

        if type == enums.OrderType.MARKET:
            if side == enums.OrderSide.BUY:
                endpoint = "buyInstant"
                params["total"] = amount
            else:
                endpoint = "sellInstant"
                params["amount"] = amount
        else:
            if side == enums.OrderSide.BUY:
                endpoint = "buyLimit"
            else:
                endpoint = "sellLimit"

            params["amount"] = amount

        if trailing is True:
            params["trailing"] = "1"

        if hidden is True:
            params["hidden"] = "1"

        if post_only is True:
            params["postOnly"] = "1"

        if time_in_force == enums.TimeInForce.IMMEDIATE_OR_CANCELLED:
            params["immediateOrCancel"] = "1"

        return await self._create_post(endpoint, params = params, signed = True)