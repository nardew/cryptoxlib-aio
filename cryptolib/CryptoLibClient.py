import asyncio
import aiohttp
import ssl
import logging
import datetime
import json
import enum
import time
from abc import ABC, abstractmethod
from multidict import CIMultiDictProxy
from typing import List, Optional

from cryptolib.Timer import Timer
from cryptolib.CryptoLibException import CryptoLibException
from cryptolib.WebsocketMgr import Subscription, WebsocketMgr

LOG = logging.getLogger(__name__)


class RestCallType(enum.Enum):
    GET = enum.auto()
    POST = enum.auto()
    DELETE = enum.auto()
    PUT = enum.auto()


class CryptoLibClient(ABC):
    def __init__(self, api_trace_log: bool = False, ssl_context: ssl.SSLContext = None) -> None:
        self.api_trace_log = api_trace_log

        self.rest_session = None
        self.subscription_sets = set()

        if ssl_context is not None:
            self.ssl_context = ssl_context
        else:
            self.ssl_context = ssl.create_default_context()

        self.subscription_sets = []

    @abstractmethod
    def _get_rest_api_uri(self) -> str:
        pass

    @abstractmethod
    def _sign_payload(self, resource: str, data: dict = None, params: dict = None, headers: dict = None) -> None:
        pass

    @abstractmethod
    def _preprocess_rest_response(self, status_code: int, headers: CIMultiDictProxy[str], body: Optional[dict]) -> None:
        pass

    @abstractmethod
    def _get_websocket_mgr(self, subscriptions: List[Subscription], ssl_context = None) -> WebsocketMgr:
        pass

    async def close(self) -> None:
        session = self._get_rest_session()
        if session is not None:
            await session.close()

    async def _create_get(self, resource: str, params: dict = None, headers: dict = None, signed: bool = False) -> dict:
        return await self._create_rest_call(RestCallType.GET, resource, None, params, headers, signed)

    async def _create_post(self, resource: str, data: dict = None, params: dict = None, headers: dict = None, signed: bool = False) -> dict:
        return await self._create_rest_call(RestCallType.POST, resource, data, params, headers, signed)

    async def _create_delete(self, resource: str, params: dict = None, headers: dict = None, signed: bool = False) -> dict:
        return await self._create_rest_call(RestCallType.DELETE, resource, None, params, headers, signed)

    async def _create_put(self, resource: str, params: dict = None, headers: dict = None, signed: bool = False) -> dict:
        return await self._create_rest_call(RestCallType.PUT, resource, None, params, headers, signed)

    async def _create_rest_call(self, rest_call_type: RestCallType, resource: str, data: dict = None, params: dict = None, headers: dict = None, signed: bool = False) -> dict:
        with Timer('RestCall'):
            # add signature into the parameters
            if signed:
                self._sign_payload(resource, params, data, headers)

            if rest_call_type == RestCallType.GET:
                rest_call = self._get_rest_session().get(self._get_rest_api_uri() + resource, json = data, params = params, headers = headers, ssl = self.ssl_context)
            elif rest_call_type == RestCallType.POST:
                rest_call = self._get_rest_session().post(self._get_rest_api_uri() + resource, json = data, params = params, headers = headers, ssl = self.ssl_context)
            elif rest_call_type == RestCallType.DELETE:
                rest_call = self._get_rest_session().delete(self._get_rest_api_uri() + resource, json = data, params = params, headers = headers, ssl = self.ssl_context)
            elif rest_call_type == RestCallType.PUT:
                rest_call = self._get_rest_session().put(self._get_rest_api_uri() + resource, json = data, params = params, headers = headers, ssl = self.ssl_context)
            else:
                raise Exception(f"Unsupported REST call type {rest_call_type}.")

            LOG.debug(f"> rest type [{rest_call_type.name}], resource [{resource}], params [{params}], headers [{headers}], data [{data}]")
            async with rest_call as response:
                status_code = response.status
                headers = response.headers
                body = await response.text()

                LOG.debug(f"<: status [{status_code}], response [{body}]")

                if len(body) > 0:
                    body = json.loads(body)

                self._preprocess_rest_response(status_code, headers, body)

                return {
                    "status_code": status_code,
                    "headers": headers,
                    "response": body
                }

    def _get_rest_session(self) -> aiohttp.ClientSession:
        if self.rest_session is not None:
            return self.rest_session

        if self.api_trace_log:
            trace_config = aiohttp.TraceConfig()
            trace_config.on_request_start.append(CryptoLibClient._on_request_start)
            trace_config.on_request_end.append(CryptoLibClient._on_request_end)
            trace_configs = [trace_config]
        else:
            trace_configs = None

        self.rest_session = aiohttp.ClientSession(trace_configs=trace_configs)

        return self.rest_session

    @staticmethod
    def _clean_request_params(params: dict) -> dict:
        clean_params = {}
        for key, value in params.items():
            if value is not None:
                clean_params[key] = str(value)

        return clean_params

    @staticmethod
    async def _on_request_start(session, trace_config_ctx, params) -> None:
        LOG.debug(f"> Context: {trace_config_ctx}")
        LOG.debug(f"> Params: {params}")

    @staticmethod
    async def _on_request_end(session, trace_config_ctx, params) -> None:
        LOG.debug(f"< Context: {trace_config_ctx}")
        LOG.debug(f"< Params: {params}")

    @staticmethod
    def _get_current_timestamp_ms() -> int:
        return int(datetime.datetime.now(tz = datetime.timezone.utc).timestamp() * 1000)

    @staticmethod
    def _get_unix_timestamp_ns() -> int:
        return int(time.time_ns() * 10**9)

    def compose_subscriptions(self, subscriptions: List[Subscription]) -> None:
        self.subscription_sets.append(subscriptions)

    async def start_websockets(self) -> None:
        if len(self.subscription_sets):
            done, pending = await asyncio.wait(
                [asyncio.create_task(self._get_websocket_mgr(subscriptions, self.ssl_context).run()) for
                 subscriptions in self.subscription_sets],
                return_when = asyncio.FIRST_EXCEPTION
            )
            for task in done:
                try:
                    task.result()
                except Exception as e:
                    LOG.exception(f"Unrecoverable exception occurred while processing messages: {e}")
                    LOG.info("All websockets scheduled for shutdown")
                    for task in pending:
                        if not task.cancelled():
                            task.cancel()
        else:
            raise CryptoLibException("ERROR: There are no subscriptions to be started.")