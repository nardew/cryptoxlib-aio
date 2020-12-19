import ssl
import logging
import datetime
import pytz
from multidict import CIMultiDictProxy
from typing import List, Optional

from cryptoxlib.CryptoXLibClient import CryptoXLibClient, RestCallType
from cryptoxlib.clients.eterbase import enums
from cryptoxlib.clients.eterbase.exceptions import EterbaseException, EterbaseRestException
from cryptoxlib.clients.eterbase.functions import map_pair
from cryptoxlib.Pair import Pair
from cryptoxlib.WebsocketMgr import WebsocketMgr, Subscription
from cryptoxlib.clients.eterbase.EterbaseWebsocket import BitpandaWebsocket


LOG = logging.getLogger(__name__)


class EterbaseClient(CryptoXLibClient):
    REST_API_URI = "https://api.eterbase.exchange/api/v1/"

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
            raise EterbaseRestException(status_code, body)

    def _get_websocket_mgr(self, subscriptions: List[Subscription], startup_delay_ms: int = 0,
                           ssl_context = None) -> WebsocketMgr:
        return BitpandaWebsocket(subscriptions = subscriptions, api_key = self.api_key, ssl_context = ssl_context,
                                 startup_delay_ms = startup_delay_ms)

    async def get_ping(self) -> dict:
        return await self._create_get("ping")

    async def get_currencies(self) -> dict:
        return await self._create_get("assets")

    async def get_markets(self) -> dict:
        return await self._create_get("markets")

    async def get_balances(self, account_id: str) -> dict:
        return await self._create_get(f"accounts/{account_id}/balances", signed = True)

    async def create_order(self, account_id: str, pair_id: str, side: enums.OrderSide, type: enums.OrderType, amount: str,
                           price: str = None, stop_price: str = None, time_in_force: enums.TimeInForce = None,
                           client_id: str = None, post_only: bool = None, cost: str = None) -> dict:
        data = {
            "accountId": account_id,
            "marketId": pair_id,
            "side": side.value,
            "type": type.value,
            "qty": amount,
            "limitPrice": price,
            "stopPrice": stop_price,
            "refId": client_id,
            "postOnly": post_only,
            "cost": cost
        }

        if time_in_force is not None:
            data['timeInForce'] = time_in_force.value

        return await self._create_post("orders", data = data, signed = True)

    async def cancel_order(self, order_id: str) -> dict:
        return await self._create_delete(f"orders/{order_id}", signed = True)
