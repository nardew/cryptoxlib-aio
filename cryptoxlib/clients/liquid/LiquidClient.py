import ssl
import logging
import jwt
from multidict import CIMultiDictProxy
from typing import List, Optional

from cryptoxlib.CryptoXLibClient import CryptoXLibClient, RestCallType
from cryptoxlib.clients.liquid import enums
from cryptoxlib.clients.liquid.exceptions import LiquidException
from cryptoxlib.WebsocketMgr import WebsocketMgr, Subscription
from cryptoxlib.clients.liquid.LiquidWebsocket import LiquidWebsocket

LOG = logging.getLogger(__name__)


class LiquidClient(CryptoXLibClient):
    REST_API_URI = "https://api.liquid.com/"

    def __init__(self, api_key: str = None, sec_key: str = None, api_trace_log: bool = False,
                 ssl_context: ssl.SSLContext = None) -> None:
        super().__init__(api_trace_log, ssl_context)

        self.api_key = api_key
        self.sec_key = sec_key

    def _get_rest_api_uri(self) -> str:
        return self.REST_API_URI

    def _sign_payload(self, rest_call_type: RestCallType, resource: str, data: dict = None, params: dict = None, headers: dict = None) -> None:
        authentication_payload = {
            "path": "/" + resource,
            "nonce": self._get_unix_timestamp_ns(),
            "token_id": self.api_key
        }

        LOG.debug(f"Authentication payload: {authentication_payload}")

        signature = jwt.encode(authentication_payload, self.sec_key, 'HS256')
        headers["X-Quoine-Auth"] = signature.decode('utf-8')

    def _preprocess_rest_response(self, status_code: int, headers: 'CIMultiDictProxy[str]', body: Optional[dict]) -> None:
        if str(status_code)[0] != '2':
            raise LiquidException(f"LiquidException: status [{status_code}], response [{body}]")

    def _get_websocket_mgr(self, subscriptions: List[Subscription], startup_delay_ms: int = 0,
                           ssl_context = None) -> WebsocketMgr:
        return LiquidWebsocket(subscriptions, self.api_key, self.sec_key, ssl_context)

    @staticmethod
    def _get_headers() -> dict:
        return {
            'X-Quoine-API-Version': '2',
            'Content-Type': 'application/json'
        }

    async def get_products(self) -> dict:
        return await self._create_get("products", headers = self._get_headers())

    async def get_product(self, product_id: str) -> dict:
        return await self._create_get("products/" + product_id, headers = self._get_headers())

    async def get_order_book(self, product_id: str, full: bool = False) -> dict:
        params = {}

        if full:
            params['full'] = 1

        return await self._create_get("products/" + product_id + "/price_levels", params = params, headers = self._get_headers())

    async def get_order(self, order_id: str) -> dict:
        return await self._create_get("orders/" + order_id, headers = self._get_headers(), signed = True)

    async def create_order(self, product_id: str, order_type: enums.OrderType, order_side: enums.OrderSide,
                           quantity: str, price: str, client_order_id: str = None) -> dict:
        data = CryptoXLibClient._clean_request_params({
            "product_id": int(product_id),
            "price": price,
            "quantity": quantity,
            "order_type": order_type.value,
            "side": order_side.value,
            "client_order_id": client_order_id
        })

        return await self._create_post("orders", data = data, headers = self._get_headers(), signed = True)

    async def cancel_order(self, order_id: str) -> dict:
        return await self._create_put("orders/" + order_id + "/cancel", headers = self._get_headers(), signed = True)

    async def get_crypto_accounts(self) -> dict:
        return await self._create_get("crypto_accounts", headers = self._get_headers(), signed = True)

    async def get_fiat_accounts(self) -> dict:
        return await self._create_get("fiat_accounts", headers = self._get_headers(), signed = True)

    async def get_account_details(self, currency: str):
        return await self._create_get(f"accounts/{currency}", headers = self._get_headers(), signed = True)

    async def get_currencies(self) -> dict:
        return await self._create_get("currencies", headers = self._get_headers())