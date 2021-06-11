import ssl
import logging
from typing import List, Optional

from cryptoxlib.CryptoXLibClient import CryptoXLibClient
from cryptoxlib.clients.binance.BinanceCommonClient import BinanceCommonClient
from cryptoxlib.clients.binance import enums
from cryptoxlib.clients.binance.functions import map_pair
from cryptoxlib.Pair import Pair
from cryptoxlib.WebsocketMgr import WebsocketMgr, Subscription
from cryptoxlib.clients.binance.BinanceWebsocket import BinanceWebsocket, BinanceTestnetWebsocket

LOG = logging.getLogger(__name__)


class BinanceClient(BinanceCommonClient):
    API_V3 = "api/v3/"
    SAPI_V1 = "sapi/v1/"

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
        params = CryptoXLibClient._clean_request_params({
            "symbol": map_pair(pair),
        })

        if limit:
            params['limit'] = limit.value

        return await self._create_get("depth", params = params, api_variable_path = BinanceClient.API_V3)

    async def get_trades(self, pair: Pair, limit: int = None) -> dict:
        params = CryptoXLibClient._clean_request_params({
            "symbol": map_pair(pair),
            "limit": limit
        })

        return await self._create_get("trades", params = params, api_variable_path = BinanceClient.API_V3)

    async def get_historical_trades(self, pair: Pair, limit: int = None, from_id: int = None) -> dict:
        params = CryptoXLibClient._clean_request_params({
            "symbol": map_pair(pair),
            "limit": limit,
            "fromId": from_id
        })

        return await self._create_get("historicalTrades", params = params, headers = self._get_header(), api_variable_path = BinanceClient.API_V3)

    async def get_aggregate_trades(self, pair: Pair, limit: int = None, from_id: int = None,
                                   start_tmstmp_ms: int = None, end_tmstmp_ms: int = None) -> dict:
        params = CryptoXLibClient._clean_request_params({
            "symbol": map_pair(pair),
            "limit": limit,
            "fromId": from_id,
            "startTime": start_tmstmp_ms,
            "endTime": end_tmstmp_ms
        })

        return await self._create_get("aggTrades", params = params, api_variable_path = BinanceClient.API_V3)

    async def get_candlesticks(self, pair: Pair, limit: int = None, interval: enums.Interval = None,
                               start_tmstmp_ms: int = None, end_tmstmp_ms: int = None) -> dict:
        params = CryptoXLibClient._clean_request_params({
            "symbol": map_pair(pair),
            "limit": limit,
            "startTime": start_tmstmp_ms,
            "endTime": end_tmstmp_ms
        })

        if interval:
            params['interval'] = interval.value

        return await self._create_get("klines", params = params, api_variable_path = BinanceClient.API_V3)

    async def get_average_price(self, pair: Pair) -> dict:
        params = CryptoXLibClient._clean_request_params({
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

    async def get_orderbook_ticker(self, pair: Optional[Pair] = None) -> dict:
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
        params = CryptoXLibClient._clean_request_params({
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
        params = CryptoXLibClient._clean_request_params({
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
        params = CryptoXLibClient._clean_request_params({
            "symbol": map_pair(pair),
            "orderId": order_id,
            "origClientOrderId": orig_client_order_id,
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        })

        return await self._create_get("order", params = params, headers = self._get_header(), signed = True, api_variable_path = BinanceClient.API_V3)

    async def cancel_order(self, pair: Pair, order_id: str = None, orig_client_order_id: str = None,
                           new_client_order_id: str = None, recv_window_ms: int = None) -> dict:
        params = CryptoXLibClient._clean_request_params({
            "symbol": map_pair(pair),
            "orderId": order_id,
            "origClientOrderId": orig_client_order_id,
            "newClientOrderId": new_client_order_id,
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        })

        return await self._create_delete("order", params = params, headers = self._get_header(), signed = True, api_variable_path = BinanceClient.API_V3)

    async def get_open_orders(self, pair: Pair = None, recv_window_ms: int = None) -> dict:
        params = CryptoXLibClient._clean_request_params({
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        })

        if pair is not None:
            params['symbol'] = map_pair(pair)

        return await self._create_get("openOrders", params = params, headers = self._get_header(),
                                      signed = True, api_variable_path = BinanceClient.API_V3)

    async def get_all_orders(self, pair: Pair, order_id: int = None, limit: int = None, start_tmstmp_ms: int = None,
                             end_tmstmp_ms: int = None, recv_window_ms: int = None) -> dict:
        params = CryptoXLibClient._clean_request_params({
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
        params = CryptoXLibClient._clean_request_params({
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
        params = CryptoXLibClient._clean_request_params({
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
        params = CryptoXLibClient._clean_request_params({
            "orderListId": order_list_id,
            "origClientOrderId": orig_client_order_id,
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        })

        return await self._create_get("orderList", params = params, headers = self._get_header(), signed = True, api_variable_path = BinanceClient.API_V3)

    async def get_all_oco_orders(self, from_id: int = None, limit: int = None, start_tmstmp_ms: int = None,
                                 end_tmstmp_ms: int = None, recv_window_ms: int = None) -> dict:
        params = CryptoXLibClient._clean_request_params({
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
        params = CryptoXLibClient._clean_request_params({
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        })

        return await self._create_get("openOrderList", params = params, headers = self._get_header(),
                                      signed = True, api_variable_path = BinanceClient.API_V3)

    async def get_account(self, recv_window_ms: Optional[int] = None) -> dict:
        params = CryptoXLibClient._clean_request_params({
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        })

        return await self._create_get("account", headers = self._get_header(), params = params, signed = True, api_variable_path = BinanceClient.API_V3)

    async def get_account_trades(self, pair: Pair, limit: int = None, from_id: int = None,
                                 start_tmstmp_ms: int = None, end_tmstmp_ms: int = None) -> dict:
        params = CryptoXLibClient._clean_request_params({
            "symbol": map_pair(pair),
            "limit": limit,
            "fromId": from_id,
            "startTime": start_tmstmp_ms,
            "endTime": end_tmstmp_ms,
            "timestamp": self._get_current_timestamp_ms()
        })

        return await self._create_get("myTrades", params = params, headers = self._get_header(), signed = True, api_variable_path = BinanceClient.API_V3)

    async def get_spot_listen_key(self):
        return await self._create_post("userDataStream", headers = self._get_header(), api_variable_path = BinanceClient.API_V3)

    async def keep_alive_spot_listen_key(self, listen_key: str):
        params = {
            "listenKey": listen_key
        }

        return await self._create_put("userDataStream", headers = self._get_header(), params = params, api_variable_path = BinanceClient.API_V3)

    async def get_isolated_margin_listen_key(self, pair: Pair):
        params = {
            "symbol": map_pair(pair)
        }

        return await self._create_post("userDataStream/isolated", headers = self._get_header(), params = params, api_variable_path = BinanceClient.SAPI_V1)

    async def keep_alive_isolated_margin_listen_key(self, listen_key: str, pair: Pair):
        params = {
            "listenKey": listen_key,
            "symbol": map_pair(pair)
        }

        return await self._create_put("userDataStream/isolated", headers = self._get_header(), params = params, api_variable_path = BinanceClient.SAPI_V1)

    async def get_cross_margin_listen_key(self):
        return await self._create_post("userDataStream", headers = self._get_header(), api_variable_path = BinanceClient.SAPI_V1)

    async def keep_alive_cross_margin_listen_key(self, listen_key: str):
        params = {
            "listenKey": listen_key
        }

        return await self._create_put("userDataStream", headers = self._get_header(), params = params, api_variable_path = BinanceClient.SAPI_V1)

    ## MARGIN ENDPOINTS

    async def margin_transfer(
            self,
            asset: str,
            amount: str,
            transfer_type: enums.CrossMarginTransferType,
            recv_window_ms: Optional[int] = None) -> dict:
        """
        Cross Margin Account Transfer (MARGIN)

        From the official original Binance REST API documentation:

        POST /sapi/v1/margin/transfer (HMAC SHA256)

        asset      STRING  YES  The asset being transferred, e.g., BTC
        amount     DECIMAL YES  The amount to be transferred
        type       INT     YES  1: transfer from main account to cross margin account
                                2: transfer from cross margin account to main account
        recvWindow LONG    NO   The value cannot be greater than 60000
        timestamp  LONG    YES
        """
        params = {
            "asset": asset,
            "amount": amount,
            "type": transfer_type.value,
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        }
        params = BinanceClient._clean_request_params(params)

        return await self._create_post(
            "margin/transfer",
            headers = self._get_header(),
            params = params,
            signed = True,
            api_variable_path = BinanceClient.SAPI_V1)

    async def margin_borrow(
            self,
            asset: str,
            amount: str,
            pair: Optional[Pair] = None,
            recv_window_ms: Optional[int] = None) -> dict:
        """
        Margin Account Borrow (MARGIN)

        From the official original Binance REST API documentation:

        POST /sapi/v1/margin/loan (HMAC SHA256)

        asset     STRING     YES
        isIsolated     STRING     NO     for isolated margin or not, "TRUE", "FALSE"，default "FALSE"
        symbol     STRING     NO     isolated symbol
        amount     DECIMAL     YES
        recvWindow     LONG     NO     The value cannot be greater than 60000
        timestamp     LONG     YES

        If isIsolated = TRUE, symbol must be sent
        isIsolated = FALSE for crossed margin loan
        """
        params = {
            "asset": asset,
            "amount": amount,
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        }
        if pair is None:
            params["isIsolated"] = "FALSE"
        else:
            params["isIsolated"] = "TRUE"
            params["symbol"] = map_pair(pair)
        params = BinanceClient._clean_request_params(params)

        return await self._create_post(
            "margin/loan",
            headers = self._get_header(),
            params = params,
            signed = True,
            api_variable_path = BinanceClient.SAPI_V1)

    async def margin_repay(
            self,
            asset: str,
            amount: str,
            pair: Optional[Pair] = None,
            recv_window_ms: Optional[int] = None) -> dict:
        """
        Margin Account Repay (MARGIN)

        From the official original Binance REST API documentation:

        POST /sapi/v1/margin/repay (HMAC SHA256)

        Repay loan for margin account.

        asset     STRING     YES
        isIsolated     STRING     NO     for isolated margin or not, "TRUE", "FALSE"，default "FALSE"
        symbol     STRING     NO     isolated symbol
        amount     DECIMAL     YES
        recvWindow     LONG     NO     The value cannot be greater than 60000
        timestamp     LONG     YES

        If "isIsolated" = "TRUE", "symbol" must be sent
        "isIsolated" = "FALSE" for crossed margin repay
        """
        params = {
            "asset": asset,
            "amount": amount,
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        }
        if pair is None:
            params["isIsolated"] = "FALSE"
        else:
            params["isIsolated"] = "TRUE"
            params["symbol"] = map_pair(pair)
        params = BinanceClient._clean_request_params(params)

        return await self._create_post(
            "margin/repay",
            headers = self._get_header(),
            params = params,
            signed = True,
            api_variable_path = BinanceClient.SAPI_V1)

    async def get_margin_asset(self, asset: str) -> dict:
        """
        Query Margin Asset (MARKET_DATA)

        From the official original Binance REST API documentation:

        GET /sapi/v1/margin/asset

        asset     STRING     YES
        """
        params = {
            "asset": asset,
        }
        params = BinanceClient._clean_request_params(params)

        return await self._create_get(
            "margin/asset",
            headers = self._get_header(),
            params = params,
            api_variable_path = BinanceClient.SAPI_V1)

    async def get_margin_pair(self, pair: Pair) -> dict:
        """
        Query Cross Margin Pair (MARKET_DATA)

        From the official original Binance REST API documentation:

        GET /sapi/v1/margin/pair

        symbol     STRING     YES
        """
        params = {
            "symbol": map_pair(pair),
        }
        params = BinanceClient._clean_request_params(params)

        return await self._create_get(
            "margin/pair",
            headers = self._get_header(),
            params = params,
            api_variable_path = BinanceClient.SAPI_V1)

    async def get_margin_all_assets(self) -> dict:
        """
        Get All Margin Assets (MARKET_DATA)

        From the official original Binance REST API documentation:

        GET /sapi/v1/margin/allAssets

        Parameters: None
        """

        return await self._create_get(
            "margin/allAssets",
            headers = self._get_header(),
            api_variable_path = BinanceClient.SAPI_V1)

    async def get_margin_all_pairs(self) -> dict:
        """
        Get All Cross Margin Pairs (MARKET_DATA)

        From the official original Binance REST API documentation:

        GET /sapi/v1/margin/allPairs

        Parameters: None
        """

        return await self._create_get(
            "margin/allPairs",
            headers = self._get_header(),
            api_variable_path = BinanceClient.SAPI_V1)

    async def get_margin_price_index(self, pair: Pair) -> dict:
        """
        Query Margin PriceIndex (MARKET_DATA)

        From the official original Binance REST API documentation:

        GET /sapi/v1/margin/priceIndex

        Weight: 1

        Official Binance REST API documentation:
        Parameters:
        Name     Type     Mandatory
        symbol     STRING     YES
        """
        params = {
            "symbol": map_pair(pair),
        }
        params = BinanceClient._clean_request_params(params)

        return await self._create_get(
            "margin/priceIndex",
            headers = self._get_header(),
            params = params,
            api_variable_path = BinanceClient.SAPI_V1)

    async def create_margin_order(self,
                                pair: Pair,
                                side: enums.OrderSide,
                                order_type: enums.OrderType,
                                quantity: str = None,
                                is_isolated: Optional[bool] = False,
                                quote_order_quantity: Optional[str] = None,
                                price: Optional[str] = None,
                                stop_price: Optional[str] = None,
                                new_client_order_id: Optional[str] = None,
                                iceberg_quantity: Optional[str] = None,
                                new_order_response_type: Optional[enums.OrderResponseType] = None,
                                side_effect_type: Optional[enums.SideEffectType] = None,
                                time_in_force: Optional[enums.TimeInForce] = None,
                                recv_window_ms: Optional[int] = None) -> dict:
        """
        Margin Account New Order (TRADE)

        From the official original Binance REST API documentation:

        POST /sapi/v1/margin/order (HMAC SHA256)

        Post a new order for margin account.

        Official Binance REST API documentation:
        Parameters:
        Name             Type     Mandatory Description
        symbol           STRING   YES
        side             ENUM     YES       BUY SELL
        type             ENUM     YES
        quantity         DECIMAL  NO
        isIsolated       STRING   NO        for isolated margin or not, "TRUE", "FALSE"，default "FALSE"
        quoteOrderQty    DECIMAL  NO
        price            DECIMAL  NO
        stopPrice        DECIMAL  NO        Used with STOP_LOSS, STOP_LOSS_LIMIT, TAKE_PROFIT, TAKE_PROFIT_LIMIT orders.
        newClientOrderId STRING   NO        A unique id among open orders. Automatically generated if not sent.
        icebergQty       DECIMAL  NO        Used with LIMIT, STOP_LOSS_LIMIT, and TAKE_PROFIT_LIMIT to create
                                            an iceberg order.
        newOrderRespType ENUM     NO        Set the response JSON. ACK, RESULT, or FULL;
                                            MARKET and LIMIT order types default to FULL, all other orders
                                            default to ACK.
        sideEffectType   ENUM     NO        NO_SIDE_EFFECT, MARGIN_BUY, AUTO_REPAY; default NO_SIDE_EFFECT.
        timeInForce      ENUM     NO        GTC,IOC,FOK
        recvWindow       LONG     NO        The value cannot be greater than 60000
        timestamp        LONG    YES
        """
        params = {
            "symbol": map_pair(pair),
            "side": side.value,
            "type": order_type.value,
            "quantity": quantity,
            "quoteOrderQty": quote_order_quantity,
            "price": price,
            "stopPrice": stop_price,
            "isIsolated": ("TRUE" if is_isolated else "FALSE"),
            "newClientOrderId": new_client_order_id,
            "icebergQty": iceberg_quantity,
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        }

        if time_in_force is not None:
            params['timeInForce'] = time_in_force.value
        elif order_type in [enums.OrderType.LIMIT, enums.OrderType.STOP_LOSS_LIMIT, enums.OrderType.TAKE_PROFIT_LIMIT]:
            # default time_in_force for LIMIT orders
            params['timeInForce'] = enums.TimeInForce.GOOD_TILL_CANCELLED.value

        if new_order_response_type is not None:
            params['newOrderRespType'] = new_order_response_type.value

        if side_effect_type is not None:
            params["sideEffectType"] = side_effect_type.value

        params = BinanceClient._clean_request_params(params)

        return await self._create_post(
            "margin/order",
            headers = self._get_header(),
            params = params,
            signed = True,
            api_variable_path = BinanceClient.SAPI_V1)

    async def cancel_margin_order(self,
                                  pair: Pair,
                                  is_isolated: Optional[bool] = False,
                                  order_id: Optional[str] = None,
                                  orig_client_order_id: Optional[str] = None,
                                  new_client_order_id: Optional[str] = None,
                                  recv_window_ms: Optional[int] = None) -> dict:
        """
        Margin Account Cancel Order (TRADE)

        From the official original Binance REST API documentation:

        DELETE /sapi/v1/margin/order (HMAC SHA256)

        Cancel an active order for margin account.

        Weight: 1

        Official Binance REST API documentation:
        Parameters:
        Name              Type   Mandatory Description
        symbol            STRING YES
        isIsolated        STRING NO        for isolated margin or not, "TRUE", "FALSE"，default "FALSE"
        orderId           LONG   NO
        origClientOrderId STRING NO
        newClientOrderId  STRING NO        Used to uniquely identify this cancel. Automatically generated by default.
        recvWindow        LONG   NO        The value cannot be greater than 60000
        timestamp         LONG   YES

        Either orderId or origClientOrderId must be sent.
        """
        params = {
            "symbol": map_pair(pair),
            "isIsolated": ("TRUE" if is_isolated else "FALSE"),
            "orderId": order_id,
            "origClientOrderId": orig_client_order_id,
            "newClientOrderId": new_client_order_id,
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        }
        params = BinanceClient._clean_request_params(params)

        return await self._create_delete(
            "margin/order",
            headers = self._get_header(),
            params = params,
            signed = True,
            api_variable_path = BinanceClient.SAPI_V1)

    async def cancel_margin_open_orders(self, pair: Pair, is_isolated: Optional[bool] = False,
                                       recv_window_ms: Optional[int] = None) -> dict:
        """
        Margin Account Cancel all Open Orders on a Symbol (TRADE)

        From the official original Binance REST API documentation:

        DELETE /sapi/v1/margin/openOrders (HMAC SHA256)

        Cancels all active orders on a symbol for margin account.
        This includes OCO orders.

        Weight: 1

        Official Binance REST API documentation:
        Parameters
        Name       Type   Mandatory Description
        symbol     STRING YES
        isIsolated STRING NO        for isolated margin or not, "TRUE", "FALSE"，default "FALSE"
        recvWindow LONG   NO        The value cannot be greater than 60000
        timestamp  LONG   YES
        """
        params = {
            "symbol": map_pair(pair),
            "isIsolated": ("TRUE" if is_isolated else "FALSE"),
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        }
        params = BinanceClient._clean_request_params(params)

        return await self._create_delete(
            "margin/openOrders",
            headers = self._get_header(),
            params = params,
            signed = True,
            api_variable_path = BinanceClient.SAPI_V1)

    async def get_margin_transfer_history(
            self,
            asset: Optional[str] = None,
            transfer_type: Optional[enums.TransferType] = None,
            start_timestamp_ms: Optional[int] = None,
            end_timestamp_ms: Optional[int] = None,
            page_num: Optional[int] = None,
            page_size: Optional[int] = None,
            is_archived: Optional[bool] = False,
            recv_window_ms: Optional[int] = None) -> dict:
        """
        Get Cross Margin Transfer History (USER_DATA)

        From the official original Binance REST API documentation:

        GET /sapi/v1/margin/transfer (HMAC SHA256)

        Weight: 1

        Official Binance REST API documentation:
        Parameters:
        Name     Type     Mandatory     Description
        asset     STRING     No
        type     STRING     NO     Transfer Type: ROLL_IN, ROLL_OUT
        startTime     LONG     NO
        endTime     LONG     NO
        current     LONG     NO     Currently querying page. Start from 1. Default:1
        size     LONG     NO     Default:10 Max:100
        archived     STRING     NO     Default: false. Set to true for archived data from 6 months ago
        recvWindow     LONG     NO     The value cannot be greater than 60000
        timestamp     LONG     YES

        Response in descending order
        Returns data for last 7 days by default
        Set archived to true to query data from 6 months ago
        """
        params = {
            "asset": asset,
            "archived": ("TRUE" if is_archived else "FALSE"),
            "startTime": start_timestamp_ms,
            "endTime": end_timestamp_ms,
            "current": (1 if page_num is None else page_num),
            "size": (10 if page_size is None else page_size),
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        }

        if transfer_type is not None:
            params["type"] = transfer_type.value

        params = BinanceClient._clean_request_params(params)

        return await self._create_get(
            "margin/transfer",
            headers = self._get_header(),
            params = params,
            signed = True,
            api_variable_path = BinanceClient.SAPI_V1)

    async def get_margin_loan(self,
                              asset: str,
                              pair: Optional[Pair] = None,
                              tx_id: Optional[int] = None,
                              start_timestamp_ms: Optional[int] = None,
                              end_timestamp_ms: Optional[int] = None,
                              page_num: Optional[int] = None,
                              page_size: Optional[int] = None,
                              is_archived: Optional[bool] = False,
                              recv_window_ms: Optional[int] = None) -> dict:
        """
        Query Loan Record (USER_DATA)

        From the official original Binance REST API documentation:

        GET /sapi/v1/margin/loan (HMAC SHA256)

        Weight: 1

        Official Binance REST API documentation:
        Parameters:
        Name     Type     Mandatory     Description
        asset     STRING     YES
        isolatedSymbol     STRING     NO     isolated symbol
        txId     LONG     NO     the tranId in POST /sapi/v1/margin/loan
        startTime     LONG     NO
        endTime     LONG     NO
        current     LONG     NO     Currently querying page. Start from 1. Default:1
        size     LONG     NO     Default:10 Max:100
        archived     STRING     NO     Default: false. Set to true for archived data from 6 months ago
        recvWindow     LONG     NO     The value cannot be greater than 60000
        timestamp     LONG     YES

        txId or startTime must be sent. txId takes precedence.
        Response in descending order
        If isolatedSymbol is not sent, crossed margin data will be returned
        Set archived to true to query data from 6 months ago
        """
        params = {
            "asset": asset,
            "txId": tx_id,
            "startTime": start_timestamp_ms,
            "endTime": end_timestamp_ms,
            "current": (1 if page_num is None else page_num),
            "size": (10 if page_size is None else page_size),
            "archived": ("TRUE" if is_archived else "FALSE"),
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        }
        if pair is not None:
            params["isolatedSymbol"] = map_pair(pair)

        params = BinanceClient._clean_request_params(params)

        return await self._create_get(
            "margin/loan",
            headers = self._get_header(),
            params = params,
            signed = True,
            api_variable_path = BinanceClient.SAPI_V1)

    async def get_margin_repay(self,
                               asset: str,
                               pair: Optional[Pair] = None,
                               tx_id: Optional[int] = None,
                               start_timestamp_ms: Optional[int] = None,
                               end_timestamp_ms: Optional[int] = None,
                               page_num: Optional[int] = None,
                               page_size: Optional[int] = None,
                               is_archived: Optional[bool] = False,
                               recv_window_ms: Optional[int] = None) -> dict:
        """
        Query Repay Record (USER_DATA)

        From the official original Binance REST API documentation:

        GET /sapi/v1/margin/repay (HMAC SHA256)

        Weight: 1

        Official Binance REST API documentation:
        Parameters:
        Name     Type     Mandatory     Description
        asset     STRING     YES
        isolatedSymbol     STRING     NO     isolated symbol
        txId     LONG     NO     return of /sapi/v1/margin/repay
        startTime     LONG     NO
        endTime     LONG     NO
        current     LONG     NO     Currently querying page. Start from 1. Default:1
        size     LONG     NO     Default:10 Max:100
        archived     STRING     NO     Default: false. Set to true for archived data from 6 months ago
        recvWindow     LONG     NO     The value cannot be greater than 60000
        timestamp     LONG     YES

        txId or startTime must be sent. txId takes precedence.
        Response in descending order
        If isolatedSymbol is not sent, crossed margin data will be returned
        Set archived to true to query data from 6 months ago
        """
        params = {
            "asset": asset,
            "txId": tx_id,
            "startTime": start_timestamp_ms,
            "endTime": end_timestamp_ms,
            "current": (1 if page_num is None else page_num),
            "size": (10 if page_size is None else page_size),
            "archived": ("TRUE" if is_archived else "FALSE"),
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        }
        if pair is not None:
            params["isolatedSymbol"] = map_pair(pair)

        params = BinanceClient._clean_request_params(params)

        return await self._create_get(
            "margin/repay",
            headers = self._get_header(),
            params = params,
            signed = True,
            api_variable_path = BinanceClient.SAPI_V1)

    async def get_margin_interest_history(self,
                                          asset: str,
                                          pair: Optional[Pair] = None,
                                          start_timestamp_ms: Optional[int] = None,
                                          end_timestamp_ms: Optional[int] = None,
                                          page_num: Optional[int] = None,
                                          page_size: Optional[int] = None,
                                          is_archived: Optional[bool] = False,
                                          recv_window_ms: Optional[int] = None) -> dict:
        """
        Get Interest History (USER_DATA)

        From the official original Binance REST API documentation:

        GET /sapi/v1/margin/interestHistory (HMAC SHA256)

        Weight: 1

        Official Binance REST API documentation:
        Parameters:
        Name     Type     Mandatory     Description
        asset     STRING     NO
        isolatedSymbol     STRING     NO     isolated symbol
        startTime     LONG     NO
        endTime     LONG     NO
        current     LONG     NO     Currently querying page. Start from 1. Default:1
        size     LONG     NO     Default:10 Max:100
        archived     STRING     NO     Default: false. Set to true for archived data from 6 months ago
        recvWindow     LONG     NO     The value cannot be greater than 60000
        timestamp     LONG     YES

        Response in descending order
        If isolatedSymbol is not sent, crossed margin data will be returned
        Set archived to true to query data from 6 months ago
        type in response has 4 enums:
        PERIODIC interest charged per hour
        ON_BORROW first interest charged on borrow
        PERIODIC_CONVERTED interest charged per hour converted into BNB
        ON_BORROW_CONVERTED first interest charged on borrow converted into BNB
        """
        params = {
            "asset": asset,
            "startTime": start_timestamp_ms,
            "endTime": end_timestamp_ms,
            "current": (1 if page_num is None else page_num),
            "size": (10 if page_size is None else page_size),
            "archived": ("TRUE" if is_archived else "FALSE"),
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        }
        if pair is not None:
            params["isolatedSymbol"] = map_pair(pair)

        params = BinanceClient._clean_request_params(params)

        return await self._create_get(
            "margin/interestHistory",
            headers = self._get_header(),
            params = params,
            signed = True,
            api_variable_path = BinanceClient.SAPI_V1)

    async def get_margin_force_liquidation_record(self,
                                              pair: Optional[Pair] = None,
                                              start_timestamp_ms: Optional[int] = None,
                                              end_timestamp_ms: Optional[int] = None,
                                              page_num: Optional[int] = None,
                                              page_size: Optional[int] = None,
                                              recv_window_ms: Optional[int] = None) -> dict:
        """
        Get Force Liquidation Record (USER_DATA)

        From the official original Binance REST API documentation:

        GET /sapi/v1/margin/forceLiquidationRec (HMAC SHA256)

        Weight: 1

        Official Binance REST API documentation:
        Parameters:
        Name     Type     Mandatory     Description
        isolatedSymbol     STRING     NO
        startTime     LONG     NO
        endTime     LONG     NO
        current     LONG     NO     Currently querying page. Start from 1. Default:1
        size     LONG     NO     Default:10 Max:100
        recvWindow     LONG     NO     The value cannot be greater than 60000
        timestamp     LONG     YES

        Response in descending order
        """
        params = {
            "startTime": start_timestamp_ms,
            "endTime": end_timestamp_ms,
            "current": (1 if page_num is None else page_num),
            "size": (10 if page_size is None else page_size),
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        }
        if pair is not None:
            params["isolatedSymbol"] = map_pair(pair)

        params = BinanceClient._clean_request_params(params)

        return await self._create_get(
            "margin/forceLiquidationRec",
            headers = self._get_header(),
            params = params,
            signed = True,
            api_variable_path = BinanceClient.SAPI_V1)

    async def get_margin_account(self, recv_window_ms: Optional[int] = None) -> dict:
        """
        Query Cross Margin Account Details (USER_DATA)

        From the official original Binance REST API documentation:

        GET /sapi/v1/margin/account (HMAC SHA256)

        Weight: 1

        Official Binance REST API documentation:
        Parameters:
        Name     Type     Mandatory     Description
        recvWindow     LONG     NO     The value cannot be greater than 60000
        timestamp     LONG     YES
        """
        params = {
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        }
        params = BinanceClient._clean_request_params(params)

        return await self._create_get(
            "margin/account",
            headers = self._get_header(),
            params = params,
            signed = True,
            api_variable_path = BinanceClient.SAPI_V1)

    async def get_margin_order(self,
                               pair: Pair,
                               is_isolated: Optional[bool] = False,
                               order_id: Optional[str] = None,
                               orig_client_order_id: Optional[str] = None,
                               recv_window_ms: Optional[int] = None) -> dict:
        """
        Query Margin Account's Order (USER_DATA)

        From the official original Binance REST API documentation:

        GET /sapi/v1/margin/order (HMAC SHA256)

        Weight: 1

        Official Binance REST API documentation:
        Parameters:
        Name     Type     Mandatory     Description
        symbol     STRING     YES
        isIsolated     STRING     NO     for isolated margin or not, "TRUE", "FALSE"，default "FALSE"
        orderId     STRING     NO
        origClientOrderId     STRING     NO
        recvWindow     LONG     NO     The value cannot be greater than 60000
        timestamp     LONG     YES

        Either orderId or origClientOrderId must be sent.
        For some historical orders cumulativeQuoteQty will be < 0, meaning the data is not available at this time.
        """
        params = {
            "symbol": map_pair(pair),
            "isIsolated": ("TRUE" if is_isolated else "FALSE"),
            "orderId": order_id,
            "origClientOrderId": orig_client_order_id,
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        }

        params = BinanceClient._clean_request_params(params)

        return await self._create_get(
            "margin/order",
            headers = self._get_header(),
            params = params,
            signed = True,
            api_variable_path = BinanceClient.SAPI_V1)

    async def get_margin_open_orders(self,
                                    pair: Optional[Pair] = None,
                                    is_isolated: Optional[bool] = False,
                                    recv_window_ms: Optional[int] = None) -> dict:
        """
        Query Margin Account's Open Orders (USER_DATA)

        From the official original Binance REST API documentation:

        GET /sapi/v1/margin/openOrders (HMAC SHA256)

        Weight: 1

        Official Binance REST API documentation:
        Parameters:
        Name     Type     Mandatory     Description
        symbol     STRING     NO
        isIsolated     STRING     NO     for isolated margin or not, "TRUE", "FALSE"，default "FALSE"
        recvWindow     LONG     NO     The value cannot be greater than 60000
        timestamp     LONG     YES

        If the symbol is not sent, orders for all symbols will be returned in an array.
        When all symbols are returned, the number of requests counted against the rate limiter
        is equal to the number of symbols currently trading on the exchange.
        If isIsolated ="TRUE", symbol must be sent
        """
        params = {
            "isIsolated": ("TRUE" if is_isolated else "FALSE"),
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        }
        if pair is not None:
            params["symbol"] = map_pair(pair)

        params = BinanceClient._clean_request_params(params)

        return await self._create_get(
            "margin/openOrders",
            headers = self._get_header(),
            params = params,
            signed = True,
            api_variable_path = BinanceClient.SAPI_V1)

    async def get_margin_all_orders(self,
                                   pair: Pair,
                                   is_isolated: Optional[bool] = False,
                                   order_id: Optional[int] = None,
                                   start_timestamp_ms: Optional[int] = None,
                                   end_timestamp_ms: Optional[int] = None,
                                   limit: Optional[int] = None,
                                   recv_window_ms: Optional[int] = None) -> dict:
        """
        Query Margin Account's All Orders (USER_DATA)

        GET /sapi/v1/margin/allOrders (HMAC SHA256)

        From the official original Binance REST API documentation:

        Weight: 1

        Request Limit: 60times/min per IP

        Official Binance REST API documentation:
        Parameters:
        Name     Type     Mandatory     Description
        symbol     STRING     YES
        isIsolated     STRING     NO     for isolated margin or not, "TRUE", "FALSE"，default "FALSE"
        orderId     LONG     NO
        startTime     LONG     NO
        endTime     LONG     NO
        limit     INT     NO     Default 500; max 500.
        recvWindow     LONG     NO     The value cannot be greater than 60000
        timestamp     LONG     YES

        If orderId is set, it will get orders >= that orderId. Otherwise most recent orders are returned.
        For some historical orders cumulativeQuoteQty will be < 0, meaning the data is not available at this time.
        """
        params = {
            "symbol": map_pair(pair),
            "isIsolated": ("TRUE" if is_isolated else "FALSE"),
            "orderId": order_id,
            "startTime": start_timestamp_ms,
            "endTime": end_timestamp_ms,
            "limit": limit,
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        }

        params = BinanceClient._clean_request_params(params)

        return await self._create_get(
            "margin/allOrders",
            headers = self._get_header(),
            params = params,
            signed = True,
            api_variable_path = BinanceClient.SAPI_V1)

    async def get_margin_my_trades(
            self,
            pair: Pair,
            is_isolated: Optional[bool] = False,
            start_timestamp_ms: Optional[int] = None,
            end_timestamp_ms: Optional[int] = None,
            from_id: Optional[int] = None,
            limit: Optional[int] = None,
            recv_window_ms: Optional[int] = None) -> dict:
        """
        Query Margin Account's Trade List (USER_DATA)

        From the official original Binance REST API documentation:

        GET /sapi/v1/margin/myTrades (HMAC SHA256)

        Weight: 1

        Official Binance REST API documentation:
        Parameters:
        Name     Type     Mandatory     Description
        symbol     STRING     YES
        isIsolated     STRING     NO     for isolated margin or not, "TRUE", "FALSE"，default "FALSE"
        startTime     LONG     NO
        endTime     LONG     NO
        fromId     LONG     NO     TradeId to fetch from. Default gets most recent trades.
        limit     INT     NO     Default 500; max 1000.
        recvWindow     LONG     NO     The value cannot be greater than 60000
        timestamp     LONG     YES

        If fromId is set, it will get trades >= that fromId. Otherwise most recent trades are returned
        """
        params = {
            "symbol": map_pair(pair),
            "isIsolated": ("TRUE" if is_isolated else "FALSE"),
            "startTime": start_timestamp_ms,
            "endTime": end_timestamp_ms,
            "limit": limit,
            "fromId": from_id,
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        }

        params = BinanceClient._clean_request_params(params)

        return await self._create_get(
            "margin/myTrades",
            headers = self._get_header(),
            params = params,
            signed = True,
            api_variable_path = BinanceClient.SAPI_V1)

    async def get_margin_max_borrowable(
            self, asset: str, pair: Optional[Pair] = None, recv_window_ms: Optional[int] = None) -> dict:
        """
        Query Max Borrow (USER_DATA)

        From the official original Binance REST API documentation:

        GET /sapi/v1/margin/maxBorrowable (HMAC SHA256)

        Weight: 5

        Official Binance REST API documentation:
        Parameters:
        Name     Type     Mandatory     Description
        asset     STRING     YES
        isolatedSymbol     STRING     NO     isolated symbol
        recvWindow     LONG     NO     The value cannot be greater than 60000
        timestamp     LONG     YES

        If isolatedSymbol is not sent, crossed margin data will be sent.
        borrowLimit is also available from https://www.binance.com/en/margin-fee
        """
        params = {
            "asset": asset,
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        }
        if pair is not None:
            params["isolatedSymbol"] = map_pair(pair)

        params = BinanceClient._clean_request_params(params)

        return await self._create_get(
            "margin/maxBorrowable",
            headers = self._get_header(),
            params = params,
            signed = True,
            api_variable_path = BinanceClient.SAPI_V1)

    async def get_margin_max_transferable(
            self,
            asset: str,
            pair: Optional[Pair] = None,
            recv_window_ms: Optional[int] = None) -> dict:
        """
        Query Max Transfer-Out Amount (USER_DATA)

        From the official original Binance REST API documentation:

        GET /sapi/v1/margin/maxTransferable (HMAC SHA256)

        Weight: 5

        Official Binance REST API documentation:
        Parameters:
        Name     Type     Mandatory     Description
        asset     STRING     YES
        isolatedSymbol     STRING     NO     isolated symbol
        recvWindow     LONG     NO     The value cannot be greater than 60000
        timestamp     LONG     YES

        If isolatedSymbol is not sent, crossed margin data will be sent
        """
        params = {
            "asset": asset,
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        }
        if pair is not None:
            params["isolatedSymbol"] = map_pair(pair)

        params = BinanceClient._clean_request_params(params)

        return await self._create_get(
            "margin/maxTransferable",
            headers = self._get_header(),
            params = params,
            signed = True,
            api_variable_path = BinanceClient.SAPI_V1)

    async def create_isolated_margin_account(self, pair: Pair, recv_window_ms: Optional[int] = None) -> dict:
        """
        Create Isolated Margin Account (MARGIN)

        From the official original Binance REST API documentation:

        POST /sapi/v1/margin/isolated/create (HMAC SHA256)

        Weight: 1

        Official Binance REST API documentation:
        Parameters:
        Name     Type     Mandatory     Description
        base     STRING     YES     Base asset of symbol
        quote     STRING     YES     Quote asset of symbol
        recvWindow     LONG     NO     No more than 60000
        timestamp     LONG     YES
        """
        params = {
            "base": pair.base,
            "quote": pair.quote,
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        }
        params = BinanceClient._clean_request_params(params)

        return await self._create_post(
            "margin/isolated/create",
            headers = self._get_header(),
            params = params,
            signed = True,
            api_variable_path = BinanceClient.SAPI_V1)

    async def margin_isolated_transfer(self,
                                            asset: str,
                                            pair: Pair,
                                            from_account_type: enums.AccountType,
                                            to_account_type: enums.AccountType,
                                            amount: str,
                                            recv_window_ms: Optional[int] = None) -> dict:
        """
        Isolated Margin Account Transfer (MARGIN)

        From the official original Binance REST API documentation:

        POST /sapi/v1/margin/isolated/transfer (HMAC SHA256)

        Weight: 1

        Official Binance REST API documentation:
        Parameters:
        Name     Type     Mandatory     Description
        asset     STRING     YES     asset,such as BTC
        symbol     STRING     YES
        transFrom     STRING     YES     "SPOT", "ISOLATED_MARGIN"
        transTo     STRING     YES     "SPOT", "ISOLATED_MARGIN"
        amount     DECIMAL     YES
        recvWindow     LONG     NO     No more than 60000
        timestamp     LONG     YES
        """
        params = {
            "asset": asset,
            "symbol": map_pair(pair),
            "transFrom": from_account_type.value,
            "transTo": to_account_type.value,
            "amount": amount,
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        }
        params = BinanceClient._clean_request_params(params)

        return await self._create_post(
            "margin/isolated/transfer",
            headers = self._get_header(),
            params = params,
            signed = True,
            api_variable_path = BinanceClient.SAPI_V1)

    async def get_margin_isolated_transfer(self,
                                           asset: str,
                                           pair: Pair,
                                           from_account_type: Optional[enums.AccountType] = None,
                                           to_account_type: Optional[enums.AccountType] = None,
                                           start_timestamp_ms: Optional[int] = None,
                                           end_timestamp_ms: Optional[int] = None,
                                           current: Optional[int] = None,
                                           size: Optional[int] = None,
                                           recv_window_ms: Optional[int] = None) -> dict:
        """
        Get Isolated Margin Transfer History (USER_DATA)

        From the official original Binance REST API documentation:

        GET /sapi/v1/margin/isolated/transfer (HMAC SHA256)

        Weight: 1

        Official Binance REST API documentation:
        Parameters:
        Name     Type     Mandatory     Description
        asset     STRING     NO
        symbol     STRING     YES
        transFrom     STRING     NO     "SPOT", "ISOLATED_MARGIN"
        transTo     STRING     NO     "SPOT", "ISOLATED_MARGIN"
        startTime     LONG     NO
        endTime     LONG     NO
        current     LONG     NO     Current page, default 1
        size     LONG     NO     Default 10, max 100
        recvWindow     LONG     NO     No more than 60000
        timestamp     LONG     YES
        """
        params = {
            "symbol": map_pair(pair),
            "asset": asset,
            "recvWindow": recv_window_ms,
            "starTime": start_timestamp_ms,
            "endTime": end_timestamp_ms,
            "current": current,
            "size": size,
            "timestamp": self._get_current_timestamp_ms()
        }

        if from_account_type is not None:
            params["transFrom"] = from_account_type.value

        if to_account_type is not None:
            params["transTo"] = to_account_type.value

        params = BinanceClient._clean_request_params(params)

        return await self._create_get(
            "margin/isolated/transfer",
            headers = self._get_header(),
            params = params,
            signed = True,
            api_variable_path = BinanceClient.SAPI_V1)

    async def get_margin_isolated_account(self, pairs: Optional[List[Pair]], recv_window_ms: Optional[int] = None) -> dict:
        """
        Query Isolated Margin Account Info (USER_DATA)

        From the official original Binance REST API documentation:

        GET /sapi/v1/margin/isolated/account (HMAC SHA256)

        Weight: 1

        Official Binance REST API documentation:
        Parameters:
        Name     Type     Mandatory     Description
        symbols     STRING     NO     Max 5 symbols can be sent; separated by ",". e.g. "BTCUSDT,BNBUSDT,ADAUSDT"
        recvWindow     LONG     NO     No more than 60000
        timestamp     LONG     YES

        If "symbols" is not sent, all isolated assets will be returned.
        If "symbols" is sent, only the isolated assets of the sent symbols will be returned.
        """
        params = {
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        }

        if pairs is not None:
            params["symbols"] = ",".join(map(map_pair, pairs))

        params = BinanceClient._clean_request_params(params)

        return await self._create_get(
            "margin/isolated/account",
            headers = self._get_header(),
            params = params,
            signed = True,
            api_variable_path = BinanceClient.SAPI_V1)

    async def get_margin_isolated_pair(self, pair: Pair, recv_window_ms: Optional[int] = None) -> dict:
        """
        Query Isolated Margin Symbol (USER_DATA)

        From the official original Binance REST API documentation:

        GET /sapi/v1/margin/isolated/pair (HMAC SHA256)

        Weight: 1

        Official Binance REST API documentation:
        Parameters:
        Name     Type     Mandatory     Description
        symbol     STRING     YES
        recvWindow     LONG     NO     No more than 60000
        timestamp     LONG     YES
        """
        params = {
            "symbol": map_pair(pair),
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        }
        params = BinanceClient._clean_request_params(params)

        return await self._create_get(
            "margin/isolated/pair",
            headers = self._get_header(),
            params = params,
            signed = True,
            api_variable_path = BinanceClient.SAPI_V1)

    async def get_margin_isolated_all_pairs(self, recv_window_ms: Optional[int] = None) -> dict:
        """
        Get All Isolated Margin Symbol(USER_DATA)

        From the official original Binance REST API documentation:

        GET /sapi/v1/margin/isolated/allPairs (HMAC SHA256)

        Weight: 1

        Official Binance REST API documentation:
        Parameters:
        Name     Type     Mandatory     Description
        recvWindow     LONG     NO     No more than 60000
        timestamp     LONG     YES
        """
        params = {
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        }
        params = BinanceClient._clean_request_params(params)

        return await self._create_get(
            "margin/isolated/allPairs",
            headers = self._get_header(),
            params = params,
            signed = True,
            api_variable_path = BinanceClient.SAPI_V1)

    async def toggle_bnb_burn(
            self,
            spot_bnb_burn: Optional[bool] = False,
            interest_bnb_burn: Optional[bool] = False,
            recv_window_ms: Optional[int] = None) -> dict:
        """
        Toggle BNB Burn On Spot Trade And Margin Interest (USER_DATA)

        From the official original Binance REST API documentation:

        POST /sapi/v1/bnbBurn (HMAC SHA256)

        Weight: 1

        Official Binance REST API documentation:
        Parameters:
        Name            Type   Mandatory Description
        spotBNBBurn     STRING NO        "true" or "false"; Determines whether to use BNB to pay
                                         for trading fees on SPOT
        interestBNBBurn STRING NO        "true" or "false"; Determines whether to use BNB to pay
                                         for margin loan's interest
        recvWindow      LONG   NO        No more than 60000
        timestamp       LONG   YES

        spotBNBBurn and interestBNBBurn should be sent at least one.
        """
        params = {
            "spotBNBBurn": ("true" if spot_bnb_burn else "false"),
            "interestBNBBurn": ("true" if interest_bnb_burn else "false"),
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        }
        params = BinanceClient._clean_request_params(params)

        return await self._create_post(
            "bnbBurn",
            headers = self._get_header(),
            params = params,
            signed = True,
            api_variable_path = BinanceClient.SAPI_V1)

    async def get_bnb_burn(self, recv_window_ms: Optional[int] = None) -> dict:
        """
        Get BNB Burn Status (USER_DATA)

        From the official original Binance REST API documentation:

        GET /sapi/v1/bnbBurn (HMAC SHA256)

        Weight: 1

        Official Binance REST API documentation:
        Parameters:
        Name     Type     Mandatory     Description
        recvWindow     LONG     NO     No more than 60000
        timestamp     LONG     YES
        """
        params = {
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        }
        params = BinanceClient._clean_request_params(params)

        return await self._create_get(
            "bnbBurn",
            headers = self._get_header(),
            params = params,
            signed = True,
            api_variable_path = BinanceClient.SAPI_V1)

    async def get_margin_interest_rate_history(
            self,
            asset: str,
            vip_level: Optional[str] = None,
            start_timestamp_ms: Optional[int] = None,
            end_timestamp_ms: Optional[int] = None,
            limit: Optional[int] = None,
            recv_window_ms: Optional[int] = None) -> dict:
        """
        Query Margin Interest Rate History (USER_DATA)

        From the official original Binance REST API documentation:

        GET /sapi/v1/margin/interestRateHistory

        Weight: 1

        Official Binance REST API documentation:
        Parameters:
        Name     Type     Mandatory     Description
        asset     STRING     YES
        vipLevel     STRING     NO     Default: user's vip level
        startTime     LONG     NO     Default: 7 days ago
        endTime     LONG     NO     Default: present. Maximum range: 3 months.
        limit     INT     NO     Default: 20. Maximum: 100
        recvWindow     LONG     NO     No more than 60000
        timestamp     LONG     YES

        X-MBX-APIKEY required
        """
        params = {
            "asset": asset,
            "vipLevel": vip_level,
            "startTime": start_timestamp_ms,
            "endTime": end_timestamp_ms,
            "recvWindow": recv_window_ms,
            "limit": limit,
            "timestamp": self._get_current_timestamp_ms()
        }

        params = BinanceClient._clean_request_params(params)

        return await self._create_get(
            "margin/interestRateHistory",
            headers = self._get_header(),
            params = params,
            signed = True,
            api_variable_path = BinanceClient.SAPI_V1)

    async def get_blvt_info(self, symbol: str = None) -> dict:
        params = BinanceClient._clean_request_params({
            "tokenName": symbol
        })

        return await self._create_get(
            "blvt/tokenInfo",
            headers = self._get_header(),
            params = params,
            api_variable_path = BinanceClient.SAPI_V1)

    async def blvt_subscribe(self, symbol: str, cost: str, recv_window_ms: int = None) -> dict:
        params = BinanceClient._clean_request_params({
            "tokenName": symbol,
            "cost": cost,
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        })

        return await self._create_post(
            "blvt/subscribe",
            headers = self._get_header(),
            params = params,
            signed = True,
            api_variable_path = BinanceClient.SAPI_V1)

    async def get_blvt_subscribtion_record(self, symbol: str = None, id: int = None, limit: int = None,
                                           start_tmstmp_ms: int = None, end_tmstmp_ms: int = None,
                                           recv_window_ms: int = None) -> dict:
        params = BinanceClient._clean_request_params({
            "tokenName": symbol,
            "id": id,
            "startTime": start_tmstmp_ms,
            "endTime": end_tmstmp_ms,
            "limit": limit,
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        })

        return await self._create_get(
            "blvt/subscribe/record",
            headers = self._get_header(),
            params = params,
            signed = True,
            api_variable_path = BinanceClient.SAPI_V1)

    async def blvt_redeem(self, symbol: str, amount: str, recv_window_ms: int = None) -> dict:
        params = BinanceClient._clean_request_params({
            "tokenName": symbol,
            "amount": amount,
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        })

        return await self._create_post(
            "blvt/redeem",
            headers = self._get_header(),
            params = params,
            signed = True,
            api_variable_path = BinanceClient.SAPI_V1)

    async def get_blvt_redemption_record(self, symbol: str = None, id: int = None, limit: int = None,
                                           start_tmstmp_ms: int = None, end_tmstmp_ms: int = None,
                                           recv_window_ms: int = None) -> dict:
        params = BinanceClient._clean_request_params({
            "tokenName": symbol,
            "id": id,
            "startTime": start_tmstmp_ms,
            "endTime": end_tmstmp_ms,
            "limit": limit,
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        })

        return await self._create_get(
            "blvt/redeem/record",
            headers = self._get_header(),
            params = params,
            signed = True,
            api_variable_path = BinanceClient.SAPI_V1)

    async def get_blvt_user_info(self, symbol: str = None, recv_window_ms: int = None) -> dict:
        params = BinanceClient._clean_request_params({
            "tokenName": symbol,
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        })

        return await self._create_get(
            "blvt/userLimit",
            headers = self._get_header(),
            params = params,
            signed = True,
            api_variable_path = BinanceClient.SAPI_V1)

    async def get_bswap_pools(self) -> dict:
        return await self._create_get(
            "bswap/pools",
            headers = self._get_header(),
            api_variable_path = BinanceClient.SAPI_V1)

    async def get_bswap_liquidity(self, pool_id: int = None, recv_window_ms: int = None) -> dict:
        params = BinanceClient._clean_request_params({
            "poolId": pool_id,
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        })

        return await self._create_get(
            "bswap/liquidity",
            headers = self._get_header(),
            params = params,
            signed = True,
            api_variable_path = BinanceClient.SAPI_V1)

    async def bswap_add_liquidity(self, pool_id: int, asset: str, quantity: str, recv_window_ms: int = None) -> dict:
        params = BinanceClient._clean_request_params({
            "poolId": pool_id,
            "asset": asset,
            "quantity": quantity,
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        })

        return await self._create_post(
            "bswap/liquidityAdd",
            headers = self._get_header(),
            params = params,
            signed = True,
            api_variable_path = BinanceClient.SAPI_V1)

    async def bswap_remove_liquidity(self, pool_id: int, asset: str, quantity: str, type: enums.LiquidityRemovalType,
                                     recv_window_ms: int = None) -> dict:
        params = BinanceClient._clean_request_params({
            "poolId": pool_id,
            "asset": asset,
            "shareAmount": quantity,
            "type": type.value,
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        })

        return await self._create_post(
            "bswap/liquidityRemove",
            headers = self._get_header(),
            params = params,
            signed = True,
            api_variable_path = BinanceClient.SAPI_V1)

    async def get_bswap_liquidity_operations(self, pool_id: int = None, operation_id: int = None,
                                             type: enums.LiquidityOperationType = None, limit: int = None,
                                             start_tmstmp_ms: int = None, end_tmstmp_ms: int = None,
                                             recv_window_ms: int = None) -> dict:
        params = BinanceClient._clean_request_params({
            "poolId": pool_id,
            "operationId": operation_id,
            "startTime": start_tmstmp_ms,
            "endTime": end_tmstmp_ms,
            "limit": limit,
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        })

        if type is not None:
            params['operation'] = type.value

        return await self._create_get(
            "bswap/liquidityOps",
            headers = self._get_header(),
            params = params,
            signed = True,
            api_variable_path = BinanceClient.SAPI_V1)

    async def get_bswap_quote(self, pair: Pair, qunatity: str,
                              recv_window_ms: int = None) -> dict:
        params = BinanceClient._clean_request_params({
            "quoteAsset": pair.quote,
            "baseAsset": pair.base,
            "quoteQty": qunatity,
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        })

        return await self._create_get(
            "bswap/quote",
            headers = self._get_header(),
            params = params,
            signed = True,
            api_variable_path = BinanceClient.SAPI_V1)

    async def bswap_swap(self, pair: Pair, qunatity: str,
                              recv_window_ms: int = None) -> dict:
        params = BinanceClient._clean_request_params({
            "quoteAsset": pair.quote,
            "baseAsset": pair.base,
            "quoteQty": qunatity,
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        })

        return await self._create_post(
            "bswap/swap",
            headers = self._get_header(),
            params = params,
            signed = True,
            api_variable_path = BinanceClient.SAPI_V1)

    async def get_bswap_swap_history(self, swap_id: int = None,
                                     status: enums.SwapStatusType = None, limit: int = None,
                                     start_tmstmp_ms: int = None, end_tmstmp_ms: int = None,
                                     quote_asset: str = None, base_asset: str = None,
                                     recv_window_ms: int = None) -> dict:
        params = BinanceClient._clean_request_params({
            "swapId": swap_id,
            "quoteAsset": quote_asset,
            "baseAsset": base_asset,
            "startTime": start_tmstmp_ms,
            "endTime": end_tmstmp_ms,
            "limit": limit,
            "recvWindow": recv_window_ms,
            "timestamp": self._get_current_timestamp_ms()
        })

        if status is not None:
            params['status'] = status.value

        return await self._create_get(
            "bswap/swap",
            headers = self._get_header(),
            params = params,
            signed = True,
            api_variable_path = BinanceClient.SAPI_V1)


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


class BinanceVanillaOptionsClient(BinanceCommonClient):
    def __init__(self, api_key: str = None, sec_key: str = None, api_trace_log: bool = False,
                 ssl_context: ssl.SSLContext = None) -> None:
        raise Exception("Vanilla Options are not implemented at the moment!")


class BinanceVanillaOptionsTestnetClient(BinanceCommonClient):
    def __init__(self, api_key: str = None, sec_key: str = None, api_trace_log: bool = False,
                 ssl_context: ssl.SSLContext = None) -> None:
        raise Exception("Vanilla Options are not implemented at the moment!")