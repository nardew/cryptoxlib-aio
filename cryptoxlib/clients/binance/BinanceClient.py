import ssl
import logging
import hmac
import hashlib
from multidict import CIMultiDictProxy
from typing import List, Optional

from cryptoxlib.CryptoXLibClient import CryptoXLibClient, RestCallType
from cryptoxlib.clients.binance import enums
from cryptoxlib.clients.binance.exceptions import BinanceException
from cryptoxlib.clients.binance.functions import map_pair
from cryptoxlib.Pair import Pair
from cryptoxlib.WebsocketMgr import WebsocketMgr, Subscription
from cryptoxlib.clients.binance.BinanceWebsocket import BinanceWebsocket, BinanceTestnetWebsocket


LOG = logging.getLogger(__name__)


class BinanceDefaultClient(CryptoXLibClient):
    def __init__(self, api_key: str = None, sec_key: str = None, api_trace_log: bool = False,
                 ssl_context: ssl.SSLContext = None) -> None:
        super().__init__(api_trace_log, ssl_context)

        self.api_key = api_key
        self.sec_key = sec_key

    def _sign_payload(self, rest_call_type: RestCallType, resource: str, data: dict = None, params: dict = None, headers: dict = None) -> None:
        params_string = ""
        data_string = ""

        if params is not None:
            params_string = '&'.join([f"{key}={val}" for key, val in params.items()])

        if data is not None:
            data_string = '&'.join(["{}={}".format(param[0], param[1]) for param in data])

        m = hmac.new(self.sec_key.encode('utf-8'), (params_string + data_string).encode('utf-8'), hashlib.sha256)

        params['signature'] = m.hexdigest()

    def _preprocess_rest_response(self, status_code: int, headers: 'CIMultiDictProxy[str]', body: Optional[dict]) -> None:
        if str(status_code)[0] != '2':
            raise BinanceException(f"BinanceException: status [{status_code}], response [{body}]")

    def _get_header(self):
        header = {
            'Accept': 'application/json',
            "X-MBX-APIKEY": self.api_key
        }

        return header


class BinanceClient(BinanceDefaultClient):
    API_V3 = "api/v3/"

    def __init__(self, api_key: str = None, sec_key: str = None, api_trace_log: bool = False,
                 api_cluster: enums.APICluster = enums.APICluster.CLUSTER_DEFAULT,
                 ssl_context: ssl.SSLContext = None) -> None:
        super().__init__(api_key = api_key, sec_key = sec_key, api_trace_log = api_trace_log, ssl_context = ssl_context)

        self.rest_api_uri = f"https://{api_cluster.value}.binance.com/"

    def _get_rest_api_uri(self) -> str:
        return self.rest_api_uri

    def _get_websocket_mgr(self, subscriptions: List[Subscription], startup_delay_ms: int = 0,
                           ssl_context = None) -> WebsocketMgr:
        return BinanceWebsocket(subscriptions = subscriptions, binance_client = self, api_key = self.api_key,
                                sec_key = self.sec_key, ssl_context = ssl_context)

    async def ping(self) -> dict:
        return await self._create_get("ping", api_variable_path = BinanceClient.API_V3)

    async def get_exchange_info(self) -> dict:
        return await self._create_get("exchangeInfo", api_variable_path = BinanceClient.API_V3)

    async def get_time(self) -> dict:
        return await self._create_get("time", api_variable_path = BinanceClient.API_V3)

    async def get_orderbook(self, pair: Pair, limit: enums.DepthLimit = None) -> dict:
        params = BinanceClient._clean_request_params({
            "symbol": map_pair(pair),
        })

        if limit:
            params['limit'] = limit.value

        return await self._create_get("depth", params = params, api_variable_path = BinanceClient.API_V3)

    async def get_trades(self, pair: Pair, limit: int = None) -> dict:
        params = BinanceClient._clean_request_params({
            "symbol": map_pair(pair),
            "limit": limit
        })

        return await self._create_get("trades", params = params, api_variable_path = BinanceClient.API_V3)

    async def get_historical_trades(self, pair: Pair, limit: int = None, from_id: int = None) -> dict:
        params = BinanceClient._clean_request_params({
            "symbol": map_pair(pair),
            "limit": limit,
            "fromId": from_id
        })

        return await self._create_get("historicalTrades", params = params, headers = self._get_header(), api_variable_path = BinanceClient.API_V3)

    async def get_aggregate_trades(self, pair: Pair, limit: int = None, from_id: int = None,
                                   start_tmstmp_ms: int = None, end_tmstmp_ms: int = None) -> dict:
        params = BinanceClient._clean_request_params({
            "symbol": map_pair(pair),
            "limit": limit,
            "fromId": from_id,
            "startTime": start_tmstmp_ms,
            "endTime": end_tmstmp_ms
        })

        return await self._create_get("aggTrades", params = params, api_variable_path = BinanceClient.API_V3)

    async def get_candelsticks(self, pair: Pair, limit: int = None, interval: enums.CandelstickInterval = None,
                               start_tmstmp_ms: int = None, end_tmstmp_ms: int = None) -> dict:
        params = BinanceClient._clean_request_params({
            "symbol": map_pair(pair),
            "limit": limit,
            "startTime": start_tmstmp_ms,
            "endTime": end_tmstmp_ms
        })

        if interval:
            params['interval'] = interval.value

        return await self._create_get("klines", params = params, api_variable_path = BinanceClient.API_V3)

    async def get_average_price(self, pair: Pair) -> dict:
        params = BinanceClient._clean_request_params({
            "symbol": map_pair(pair)
        })

        return await self._create_get("avgPrice", params = params, api_variable_path = BinanceClient.API_V3)

    async def get_24h_price_ticker(self, pair: Pair = None) -> dict:
        params = {}
        if pair is not None:
            params['symbol'] = map_pair(pair)

        return await self._create_get("ticker/24hr", params = params, api_variable_path = BinanceClient.API_V3)

    async def get_price_ticker(self, pair: Pair = None) -> dict:
        params = {}
        if pair is not None:
            params['symbol'] = map_pair(pair)

        return await self._create_get("ticker/price", params = params, api_variable_path = BinanceClient.API_V3)

    async def get_best_orderbook_ticker(self, pair: Optional[Pair] = None) -> dict:
        params = {}
        if pair is not None:
            params['symbol'] = map_pair(pair)

        return await self._create_get("ticker/bookTicker", headers = self._get_header(), params = params, api_variable_path = BinanceClient.API_V3)

    async def create_order(self, pair: Pair, side: enums.OrderSide, type: enums.OrderType,
                           quantity: str,
                           price: str = None,
                           stop_price: str = None,
                           quote_order_quantity: str = None,
                           time_in_force: enums.TimeInForce = None,
                           new_client_order_id: str = None,
                           iceberg_quantity: str = None,
                           new_order_response_type: enums.OrderResponseType = None,
                           recv_window_ms: int = None) -> dict:
        params = BinanceClient._clean_request_params({
            "symbol": map_pair(pair),
            "side": side.value,
            "type": type.value,
            "quantity": quantity,
            "quoteOrderQty": quote_order_quantity,
            "price": price,
            "stopPrice": stop_price,
            "newClientOrderId": new_client_order_id,
            "icebergQty": iceberg_quantity,
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        })

        if time_in_force:
            params['timeInForce'] = time_in_force.value

        if new_order_response_type:
            params['newOrderRespType'] = new_order_response_type.value

        return await self._create_post("order", params = params, headers = self._get_header(), signed = True, api_variable_path = BinanceClient.API_V3)

    async def create_test_order(self, pair: Pair, side: enums.OrderSide, type: enums.OrderType,
                                quantity: str,
                                price: str = None,
                                stop_price: str = None,
                                quote_order_quantity: str = None,
                                time_in_force: enums.TimeInForce = None,
                                new_client_order_id: str = None,
                                iceberg_quantity: str = None,
                                new_order_response_type: enums.OrderResponseType = None,
                                recv_window_ms: int = None) -> dict:
        params = BinanceClient._clean_request_params({
            "symbol": map_pair(pair),
            "side": side.value,
            "type": type.value,
            "quantity": quantity,
            "quoteOrderQty": quote_order_quantity,
            "price": price,
            "stopPrice": stop_price,
            "newClientOrderId": new_client_order_id,
            "icebergQty": iceberg_quantity,
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        })

        if time_in_force:
            params['timeInForce'] = time_in_force.value

        if new_order_response_type:
            params['newOrderRespType'] = new_order_response_type.value

        return await self._create_post("order/test", params = params, headers = self._get_header(),
                                       signed = True, api_variable_path = BinanceClient.API_V3)

    async def get_order(self, pair: Pair, order_id: int = None, orig_client_order_id: int = None,
                        recv_window_ms: int = None) -> dict:
        params = BinanceClient._clean_request_params({
            "symbol": map_pair(pair),
            "orderId": order_id,
            "origClientOrderId": orig_client_order_id,
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        })

        return await self._create_get("order", params = params, headers = self._get_header(), signed = True, api_variable_path = BinanceClient.API_V3)

    async def cancel_order(self, pair: Pair, order_id: str = None, orig_client_order_id: str = None,
                           new_client_order_id: str = None, recv_window_ms: int = None) -> dict:
        params = BinanceClient._clean_request_params({
            "symbol": map_pair(pair),
            "orderId": order_id,
            "origClientOrderId": orig_client_order_id,
            "newClientOrderId": new_client_order_id,
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        })

        return await self._create_delete("order", params = params, headers = self._get_header(), signed = True, api_variable_path = BinanceClient.API_V3)

    async def get_open_orders(self, pair: Pair = None, recv_window_ms: int = None) -> dict:
        params = BinanceClient._clean_request_params({
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        })

        if pair is not None:
            params['symbol'] = map_pair(pair)

        return await self._create_get("openOrders", params = params, headers = self._get_header(),
                                      signed = True, api_variable_path = BinanceClient.API_V3)

    async def get_all_orders(self, pair: Pair, order_id: int = None, limit: int = None, start_tmstmp_ms: int = None,
                             end_tmstmp_ms: int = None, recv_window_ms: int = None) -> dict:
        params = BinanceClient._clean_request_params({
            "symbol": map_pair(pair),
            "orderId": order_id,
            "startTime": start_tmstmp_ms,
            "endTime": end_tmstmp_ms,
            "limit": limit,
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        })

        return await self._create_get("allOrders", params = params, headers = self._get_header(), signed = True, api_variable_path = BinanceClient.API_V3)

    async def create_oco_order(self, pair: Pair, side: enums.OrderSide,
                               quantity: str,
                               price: str,
                               stop_price: str,
                               limit_client_order_id: str = None,
                               list_client_order_id: str = None,
                               limit_iceberg_quantity: str = None,
                               stop_client_order_id: str = None,
                               stop_limit_price: str = None,
                               stop_iceberg_quantity: str = None,
                               stop_limit_time_in_force: enums.TimeInForce = None,
                               new_order_response_type: enums.OrderResponseType = None,
                               recv_window_ms: int = None) -> dict:
        params = BinanceClient._clean_request_params({
            "symbol": map_pair(pair),
            "side": side.value,
            "quantity": quantity,
            "listClientOrderId": list_client_order_id,
            "limitClientOrderId": limit_client_order_id,
            "price": price,
            "stopClientOrderId": stop_client_order_id,
            "stopPrice": stop_price,
            "stopLimitPrice": stop_limit_price,
            "stopIcebergQty": stop_iceberg_quantity,
            "limitIcebergQty": limit_iceberg_quantity,
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        })

        if stop_limit_time_in_force:
            params['stopLimitTimeInForce'] = stop_limit_time_in_force.value

        if new_order_response_type:
            params['newOrderRespType'] = new_order_response_type.value

        return await self._create_post("order/oco", params = params, headers = self._get_header(),
                                       signed = True, api_variable_path = BinanceClient.API_V3)

    async def cancel_oco_order(self, pair: Pair, order_list_id: str = None, list_client_order_id: str = None,
                               new_client_order_id: str = None, recv_window_ms: int = None) -> dict:
        params = BinanceClient._clean_request_params({
            "symbol": map_pair(pair),
            "orderListId": order_list_id,
            "listClientOrderId": list_client_order_id,
            "newClientOrderId": new_client_order_id,
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        })

        return await self._create_delete("orderList", params = params, headers = self._get_header(),
                                         signed = True, api_variable_path = BinanceClient.API_V3)

    async def get_oco_order(self, order_list_id: int = None, orig_client_order_id: int = None,
                            recv_window_ms: int = None) -> dict:
        params = BinanceClient._clean_request_params({
            "orderListId": order_list_id,
            "origClientOrderId": orig_client_order_id,
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        })

        return await self._create_get("orderList", params = params, headers = self._get_header(), signed = True, api_variable_path = BinanceClient.API_V3)

    async def get_all_oco_orders(self, from_id: int = None, limit: int = None, start_tmstmp_ms: int = None,
                                 end_tmstmp_ms: int = None, recv_window_ms: int = None) -> dict:
        params = BinanceClient._clean_request_params({
            "fromId": from_id,
            "startTime": start_tmstmp_ms,
            "endTime": end_tmstmp_ms,
            "limit": limit,
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        })

        return await self._create_get("allOrderList", params = params, headers = self._get_header(),
                                      signed = True, api_variable_path = BinanceClient.API_V3)

    async def get_open_oco_orders(self, recv_window_ms: int = None) -> dict:
        params = BinanceClient._clean_request_params({
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        })

        return await self._create_get("openOrderList", params = params, headers = self._get_header(),
                                      signed = True, api_variable_path = BinanceClient.API_V3)

    async def get_account(self, recv_window_ms: Optional[int] = None) -> dict:
        params = BinanceClient._clean_request_params({
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        })

        return await self._create_get("account", headers = self._get_header(), params = params, signed = True, api_variable_path = BinanceClient.API_V3)

    async def get_account_trades(self, pair: Pair, limit: int = None, from_id: int = None,
                                 start_tmstmp_ms: int = None, end_tmstmp_ms: int = None) -> dict:
        params = BinanceClient._clean_request_params({
            "symbol": map_pair(pair),
            "limit": limit,
            "fromId": from_id,
            "startTime": start_tmstmp_ms,
            "endTime": end_tmstmp_ms,
            "timestamp": self._get_current_timestamp_ms()
        })

        return await self._create_get("myTrades", params = params, headers = self._get_header(), signed = True, api_variable_path = BinanceClient.API_V3)

    async def get_listen_key(self):
        return await self._create_post("userDataStream", headers = self._get_header(), api_variable_path = BinanceClient.API_V3)


class BinanceTestnetClient(BinanceClient):
    REST_API_URI = "https://testnet.binance.vision/"

    def __init__(self, api_key: str = None, sec_key: str = None, api_trace_log: bool = False,
                 ssl_context: ssl.SSLContext = None) -> None:
        super().__init__(api_key = api_key, sec_key = sec_key, api_trace_log = api_trace_log, ssl_context = ssl_context)

    def _get_rest_api_uri(self) -> str:
        return BinanceTestnetClient.REST_API_URI

    def _get_websocket_mgr(self, subscriptions: List[Subscription], startup_delay_ms: int = 0,
                           ssl_context = None) -> WebsocketMgr:
        return BinanceTestnetWebsocket(subscriptions = subscriptions, binance_client = self, api_key = self.api_key,
                                sec_key = self.sec_key, ssl_context = ssl_context)


class BinanceUSDSMFuturesClient(BinanceDefaultClient):
    def __init__(self, api_key: str = None, sec_key: str = None, api_trace_log: bool = False,
                 ssl_context: ssl.SSLContext = None) -> None:
        raise Exception("USDS-M Futures are not implemented at the moment!")


class BinanceUSDSMFuturesTestnetClient(BinanceDefaultClient):
    def __init__(self, api_key: str = None, sec_key: str = None, api_trace_log: bool = False,
                 ssl_context: ssl.SSLContext = None) -> None:
        raise Exception("USDS-M Futures are not implemented at the moment!")


class BinanceCOINMFuturesClient(BinanceDefaultClient):
    def __init__(self, api_key: str = None, sec_key: str = None, api_trace_log: bool = False,
                 ssl_context: ssl.SSLContext = None) -> None:
        raise Exception("COIN-M Futures are not implemented at the moment!")


class BinanceCOINMFuturesTestnetClient(BinanceDefaultClient):
    def __init__(self, api_key: str = None, sec_key: str = None, api_trace_log: bool = False,
                 ssl_context: ssl.SSLContext = None) -> None:
        raise Exception("COIN-M Futures are not implemented at the moment!")


class BinanceVanillaOptionsClient(BinanceDefaultClient):
    def __init__(self, api_key: str = None, sec_key: str = None, api_trace_log: bool = False,
                 ssl_context: ssl.SSLContext = None) -> None:
        raise Exception("Vanilla Options are not implemented at the moment!")


class BinanceVanillaOptionsTestnetClient(BinanceDefaultClient):
    def __init__(self, api_key: str = None, sec_key: str = None, api_trace_log: bool = False,
                 ssl_context: ssl.SSLContext = None) -> None:
        raise Exception("Vanilla Options are not implemented at the moment!")