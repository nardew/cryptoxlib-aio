import ssl
import logging
import hmac
import hashlib
from multidict import CIMultiDictProxy
from typing import List, Tuple, Optional

from cryptoxlib.CryptoXLibClient import CryptoXLibClient, RestCallType
from cryptoxlib.clients.bitforex import enums
from cryptoxlib.Pair import Pair
from cryptoxlib.clients.bitforex.exceptions import BitforexRestException
from cryptoxlib.WebsocketMgr import WebsocketMgr, Subscription
from cryptoxlib.clients.bitforex.BitforexWebsocket import BitforexWebsocket
from cryptoxlib.clients.bitforex.functions import map_pair

LOG = logging.getLogger(__name__)


class BitforexClient(CryptoXLibClient):
    REST_API_VERSION_URI = "/api/v1/"
    REST_API_URI = "https://api.bitforex.com" + REST_API_VERSION_URI

    def __init__(self, api_key: str = None, sec_key: str = None, api_trace_log: bool = False,
                 ssl_context: ssl.SSLContext = None) -> None:
        super().__init__(api_trace_log, ssl_context)

        self.api_key = api_key
        self.sec_key = sec_key

    def _get_rest_api_uri(self) -> str:
        return BitforexClient.REST_API_URI

    def _sign_payload(self, rest_call_type: RestCallType, resource: str, data: dict = None, params: dict = None, headers: dict = None) -> None:
        params['accessKey'] = self.api_key

        params_string = ""
        data_string = ""

        if params is not None:
            params_string = BitforexClient.REST_API_VERSION_URI + resource + '?'
            params_string += '&'.join([f"{key}={val}" for key, val in sorted(params.items())])

        if data is not None:
            data_string = '&'.join(["{}={}".format(param[0], param[1]) for param in data])

        m = hmac.new(self.sec_key.encode('utf-8'), (params_string + data_string).encode('utf-8'), hashlib.sha256)

        params['signData'] = m.hexdigest()

    def _preprocess_rest_response(self, status_code: int, headers: 'CIMultiDictProxy[str]', body: Optional[dict]) -> None:
        if body['success'] is False:
            raise BitforexRestException(status_code, body)

    def _get_websocket_mgr(self, subscriptions: List[Subscription], startup_delay_ms: int = 0,
                           ssl_context = None) -> WebsocketMgr:
        return BitforexWebsocket(subscriptions, ssl_context)

    async def get_exchange_info(self) -> dict:
        return await self._create_get("market/symbols")

    async def get_order_book(self, pair: Pair, depth: str = None) -> dict:
        params = CryptoXLibClient._clean_request_params({
            "symbol": map_pair(pair),
            "size": depth,
        })

        return await self._create_get("market/depth", params = params)

    async def get_ticker(self, pair: Pair) -> dict:
        params = CryptoXLibClient._clean_request_params({
            "symbol": map_pair(pair)
        })

        return await self._create_get("market/ticker", params = params, signed = True)

    async def get_candlesticks(self, pair: Pair, interval: enums.CandlestickInterval, size: str = None) -> dict:
        params = CryptoXLibClient._clean_request_params({
            "symbol": map_pair(pair),
            "ktype": interval.value,
            "size": size
        })

        return await self._create_get("market/kline", params = params, signed = True)

    async def get_trades(self, pair: Pair, size: str = None) -> dict:
        params = CryptoXLibClient._clean_request_params({
            "symbol": map_pair(pair),
            "size": size
        })

        return await self._create_get("market/trades", params = params, signed = True)

    async def get_single_fund(self, currency: str) -> dict:
        params = CryptoXLibClient._clean_request_params({
            "currency": currency.lower(),
            "nonce": self._get_current_timestamp_ms()
        })

        return await self._create_post("fund/mainAccount", params = params, signed = True)

    async def get_funds(self) -> dict:
        params = CryptoXLibClient._clean_request_params({
            "nonce": self._get_current_timestamp_ms()
        })

        return await self._create_post("fund/allAccount", params = params, signed = True)

    async def create_order(self, pair: Pair, price: str, quantity: str, side: enums.OrderSide) -> dict:
        params = CryptoXLibClient._clean_request_params({
            "symbol": map_pair(pair),
            "price": price,
            "amount": quantity,
            "tradeType": side.value,
            "nonce": self._get_current_timestamp_ms()
        })

        return await self._create_post("trade/placeOrder", params = params, signed = True)

    # orders is a list of tuples where each tuple represents an order. Members of the tuple represent following attributes:
    # (price, quantity, side)
    async def create_multi_order(self, pair: Pair, orders: List[Tuple[str, str, enums.OrderSide]]) -> dict:
        orders_data = []
        for order in orders:
            orders_data.append({
                "price": order[0],
                "amount": order[1],
                "tradeType": order[2].value,
            })

        params = CryptoXLibClient._clean_request_params({
            "symbol": map_pair(pair),
            "ordersData": orders_data,
            "nonce": self._get_current_timestamp_ms()
        })

        return await self._create_post("trade/placeMultiOrder", params = params, signed = True)

    async def cancel_order(self, pair: Pair, order_id: str) -> dict:
        params = CryptoXLibClient._clean_request_params({
            "symbol": map_pair(pair),
            "orderId": order_id,
            "nonce": self._get_current_timestamp_ms()
        })

        return await self._create_post("trade/cancelOrder", params = params, signed = True)

    async def cancel_multi_order(self, pair: Pair, order_ids: List[str]) -> dict:
        params = CryptoXLibClient._clean_request_params({
            "symbol": map_pair(pair),
            "orderIds": ",".join(order_ids),
            "nonce": self._get_current_timestamp_ms()
        })

        return await self._create_post("trade/cancelMultiOrder", params = params, signed = True)

    async def cancel_all_orders(self, pair: Pair) -> dict:
        params = CryptoXLibClient._clean_request_params({
            "symbol": map_pair(pair),
            "nonce": self._get_current_timestamp_ms()
        })

        return await self._create_post("trade/cancelAllOrder", params = params, signed = True)

    async def get_order(self, pair: Pair, order_id: str) -> dict:
        params = CryptoXLibClient._clean_request_params({
            "symbol": map_pair(pair),
            "orderId": order_id,
            "nonce": self._get_current_timestamp_ms()
        })

        return await self._create_post("trade/orderInfo", params = params, signed = True)

    async def find_order(self, pair: Pair, state: enums.OrderState, side: enums.OrderSide = None) -> dict:
        params = CryptoXLibClient._clean_request_params({
            "symbol": map_pair(pair),
            "state": state.value,
            "nonce": self._get_current_timestamp_ms()
        })

        if side:
            params["tradeType"] = side.value

        return await self._create_post("trade/orderInfos", params = params, signed = True)

    async def get_orders(self, pair: Pair, order_ids: List[str]) -> dict:
        params = CryptoXLibClient._clean_request_params({
            "symbol": map_pair(pair),
            "orderIds": ",".join(order_ids),
            "nonce": self._get_current_timestamp_ms()
        })

        return await self._create_post("trade/multiOrderInfo", params = params, signed = True)