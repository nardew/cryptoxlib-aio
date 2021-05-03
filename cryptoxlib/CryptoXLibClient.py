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
from typing import List, Optional, Dict

from cryptoxlib.version_conversions import async_create_task
from cryptoxlib.Timer import Timer
from cryptoxlib.exceptions import CryptoXLibException
from cryptoxlib.WebsocketMgr import Subscription, WebsocketMgr

LOG = logging.getLogger(__name__)


class RestCallType(enum.Enum):
    GET = "GET"
    POST = "POST"
    DELETE = "DELETE"
    PUT = "PUT"


class SubscriptionSet(object):
    SUBSCRIPTION_SET_ID_SEQ = 0

    def __init__(self, subscriptions: List[Subscription]):
        self.subscription_set_id = SubscriptionSet.SUBSCRIPTION_SET_ID_SEQ
        SubscriptionSet.SUBSCRIPTION_SET_ID_SEQ += 1

        self.subscriptions: List[Subscription] = subscriptions
        self.websocket_mgr: Optional[WebsocketMgr] = None

    def find_subscription(self, subscription: Subscription) -> Optional[Subscription]:
        for s in self.subscriptions:
            if s.internal_subscription_id == subscription.internal_subscription_id:
                return s

        return None


class CryptoXLibClient(ABC):
    def __init__(self, api_trace_log: bool = False, ssl_context: ssl.SSLContext = None) -> None:
        self.api_trace_log = api_trace_log

        self.rest_session = None
        self.subscription_sets: Dict[int, SubscriptionSet] = {}

        if ssl_context is not None:
            self.ssl_context = ssl_context
        else:
            self.ssl_context = ssl.create_default_context()

    @abstractmethod
    def _get_rest_api_uri(self) -> str:
        pass

    @abstractmethod
    def _sign_payload(self, rest_call_type: RestCallType, resource: str, data: dict = None, params: dict = None, headers: dict = None) -> None:
        pass

    @abstractmethod
    def _preprocess_rest_response(self, status_code: int, headers: 'CIMultiDictProxy[str]', body: Optional[dict]) -> None:
        pass

    @abstractmethod
    def _get_websocket_mgr(self, subscriptions: List[Subscription], startup_delay_ms: int = 0,
                           ssl_context = None) -> WebsocketMgr:
        pass

    async def close(self) -> None:
        session = self._get_rest_session()
        if session is not None:
            await session.close()

    async def _create_get(self, resource: str, params: dict = None, headers: dict = None, signed: bool = False,
                          api_variable_path: str = None) -> dict:
        return await self._create_rest_call(RestCallType.GET, resource, None, params, headers, signed, api_variable_path)

    async def _create_post(self, resource: str, data: dict = None, params: dict = None, headers: dict = None, signed: bool = False,
                           api_variable_path: str = None) -> dict:
        return await self._create_rest_call(RestCallType.POST, resource, data, params, headers, signed, api_variable_path)

    async def _create_delete(self, resource: str, data:dict = None,  params: dict = None, headers: dict = None, signed: bool = False,
                             api_variable_path: str = None) -> dict:
        return await self._create_rest_call(RestCallType.DELETE, resource, data, params, headers, signed, api_variable_path)

    async def _create_put(self, resource: str, data: dict = None, params: dict = None, headers: dict = None, signed: bool = False,
                          api_variable_path: str = None) -> dict:
        return await self._create_rest_call(RestCallType.PUT, resource, data, params, headers, signed, api_variable_path)

    async def _create_rest_call(self, rest_call_type: RestCallType, resource: str, data: dict = None, params: dict = None, headers: dict = None, signed: bool = False,
                                api_variable_path: str = None) -> dict:
        with Timer('RestCall'):
            # ensure headers is always a valid object
            if headers is None:
                headers = {}

            # add signature into the parameters
            if signed:
                self._sign_payload(rest_call_type, resource, data, params, headers)

            resource_uri = self._get_rest_api_uri()
            if api_variable_path is not None:
                resource_uri += api_variable_path
            resource_uri += resource

            if rest_call_type == RestCallType.GET:
                rest_call = self._get_rest_session().get(resource_uri, json = data, params = params, headers = headers, ssl = self.ssl_context)
            elif rest_call_type == RestCallType.POST:
                rest_call = self._get_rest_session().post(resource_uri, json = data, params = params, headers = headers, ssl = self.ssl_context)
            elif rest_call_type == RestCallType.DELETE:
                rest_call = self._get_rest_session().delete(resource_uri, json = data, params = params, headers = headers, ssl = self.ssl_context)
            elif rest_call_type == RestCallType.PUT:
                rest_call = self._get_rest_session().put(resource_uri, json = data, params = params, headers = headers, ssl = self.ssl_context)
            else:
                raise Exception(f"Unsupported REST call type {rest_call_type}.")

            LOG.debug(f"> rest type [{rest_call_type.name}], uri [{resource_uri}], params [{params}], headers [{headers}], data [{data}]")
            async with rest_call as response:
                status_code = response.status
                headers = response.headers
                body = await response.text()

                LOG.debug(f"<: status [{status_code}], response [{body}]")

                if len(body) > 0:
                    try:
                        body = json.loads(body)
                    except json.JSONDecodeError:
                        body = {
                            "raw": body
                        }

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
            trace_config.on_request_start.append(CryptoXLibClient._on_request_start)
            trace_config.on_request_end.append(CryptoXLibClient._on_request_end)
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

    def compose_subscriptions(self, subscriptions: List[Subscription]) -> int:
        subscription_set = SubscriptionSet(subscriptions = subscriptions)
        self.subscription_sets[subscription_set.subscription_set_id] = subscription_set

        return subscription_set.subscription_set_id

    async def add_subscriptions(self, subscription_set_id: int, subscriptions: List[Subscription]) -> None:
        await self.subscription_sets[subscription_set_id].websocket_mgr.subscribe(subscriptions)

    async def unsubscribe_subscriptions(self, subscriptions: List[Subscription]) -> None:
        for subscription in subscriptions:
            subscription_found = False
            for id, subscription_set in self.subscription_sets.items():
                if subscription_set.find_subscription(subscription) is not None:
                    subscription_found = True
                    await subscription_set.websocket_mgr.unsubscribe(subscriptions)

            if not subscription_found:
                raise CryptoXLibException(f"No active subscription {subscription.subscription_id} found.")

    async def unsubscribe_subscription_set(self, subscription_set_id: int) -> None:
        return await self.unsubscribe_subscriptions(self.subscription_sets[subscription_set_id].subscriptions)

    async def unsubscribe_all(self) -> None:
        for id, _ in self.subscription_sets.items():
            await self.unsubscribe_subscription_set(id)

    async def start_websockets(self, websocket_start_time_interval_ms: int = 0) -> None:
        if len(self.subscription_sets) < 1:
            raise CryptoXLibException("ERROR: There are no subscriptions to be started.")

        tasks = []
        startup_delay_ms = 0
        for id, subscription_set in self.subscription_sets.items():
            subscription_set.websocket_mgr = self._get_websocket_mgr(subscription_set.subscriptions, startup_delay_ms, self.ssl_context)
            tasks.append(async_create_task(
                subscription_set.websocket_mgr.run())
            )
            startup_delay_ms += websocket_start_time_interval_ms

        done, pending = await asyncio.wait(tasks, return_when = asyncio.FIRST_EXCEPTION)
        for task in done:
            try:
                task.result()
            except Exception as e:
                LOG.error(f"Unrecoverable exception occurred while processing messages: {e}")
                LOG.info(f"Remaining websocket managers scheduled for shutdown.")

                await self.shutdown_websockets()

                if len(pending) > 0:
                    await asyncio.wait(pending, return_when = asyncio.ALL_COMPLETED)

                LOG.info("All websocket managers shut down.")
                raise

    async def shutdown_websockets(self):
        for id, subscription_set in self.subscription_sets.items():
            await subscription_set.websocket_mgr.shutdown()
