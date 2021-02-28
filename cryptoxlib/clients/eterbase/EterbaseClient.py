import ssl
import logging
import datetime
import hmac
import hashlib
import json
import base64
from multidict import CIMultiDictProxy
from typing import List, Optional

from cryptoxlib.CryptoXLibClient import CryptoXLibClient, RestCallType
from cryptoxlib.clients.eterbase import enums
from cryptoxlib.clients.eterbase.exceptions import EterbaseRestException
from cryptoxlib.WebsocketMgr import WebsocketMgr, Subscription
from cryptoxlib.clients.eterbase.EterbaseWebsocket import EterbaseWebsocket


LOG = logging.getLogger(__name__)


class EterbaseClient(CryptoXLibClient):
    REST_API_URI = "https://api.eterbase.exchange/api/v1/"

    def __init__(self, account_id: str = None, api_key: str = None, sec_key: str = None, api_trace_log: bool = False,
                 ssl_context: ssl.SSLContext = None) -> None:
        super().__init__(api_trace_log, ssl_context)

        self.account_id = account_id
        self.api_key = api_key
        self.sec_key = sec_key

    def _get_rest_api_uri(self) -> str:
        return self.REST_API_URI

    def _sign_payload(self, rest_call_type: RestCallType, resource: str, data: dict = None, params: dict = None, headers: dict = None) -> None:
        http_date = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")

        headers["Date"] = http_date
        message = 'date' + ':' + ' ' + http_date + "\n" + rest_call_type.value + ' ' + '/api/v1/' + resource + ' HTTP/1.1'
        headers_line = 'date request-line'
        if data is not None:
            headers_line += ' digest'
            digest = "SHA-256=" + base64.b64encode(hashlib.new("sha256", json.dumps(data).encode('utf-8')).digest()).decode()
            message += "\ndigest" + ':' + ' ' + digest
            headers['Digest'] = digest
        signature = base64.b64encode(hmac.new(self.sec_key.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).digest()).decode()
        headers["Authorization"] = 'hmac username="' + self.api_key + \
                                   '",algorithm="hmac-sha256",headers="' + headers_line + '",' + \
                                   'signature="' + signature + '"'
        headers["Content-Type"] = "application/json"

    def _preprocess_rest_response(self, status_code: int, headers: 'CIMultiDictProxy[str]', body: Optional[dict]) -> None:
        if str(status_code)[0] != '2':
            raise EterbaseRestException(status_code, body)

    def _get_websocket_mgr(self, subscriptions: List[Subscription], startup_delay_ms: int = 0,
                           ssl_context = None) -> WebsocketMgr:
        return EterbaseWebsocket(subscriptions = subscriptions, eterbase_client = self,
                                 account_id = self.account_id,
                                 ssl_context = ssl_context,
                                 startup_delay_ms = startup_delay_ms)

    async def get_ping(self) -> dict:
        return await self._create_get("ping")

    async def get_currencies(self) -> dict:
        return await self._create_get("assets")

    async def get_markets(self) -> dict:
        return await self._create_get("markets")

    async def get_balances(self) -> dict:
        return await self._create_get(f"accounts/{self.account_id}/balances", signed = True)

    async def get_token(self) -> dict:
        return await self._create_get(f"wstoken", signed = True)

    async def create_order(self, pair_id: str, side: enums.OrderSide, type: enums.OrderType, amount: str,
                           price: str = None, stop_price: str = None, time_in_force: enums.TimeInForce = None,
                           client_id: str = None, post_only: bool = None, cost: str = None) -> dict:
        data = {
            "accountId": self.account_id,
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
