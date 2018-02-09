BASE_URL = "https://api.foobot.io/v2/"
DEVICE_URL = BASE_URL + 'owner/{username}/device/'
LAST_DATA_URL = BASE_URL + "device/{uuid}/datapoint/{period:d}/last/{average_by:d}/"
HISTORICAL_DATA_URL = BASE_URL + "device/{uuid}/datapoint/{start:d}/{end:d}/{average_by:d}/"

import asyncio
import aiohttp
import async_timeout
from datetime import datetime, timezone
from math import trunc

class FoobotClient(object):
    """Foobot API client"""

    def __init__(self, token, username, session=None,
                 timeout=aiohttp.client.DEFAULT_TIMEOUT):
        self._headers = {'X-API-KEY-TOKEN': token,
                         'content-type': 'application/json'}
        self._username = username
        self._timeout = timeout
        if session is not None:
            self._session = session
        else:
            self._session = aiohttp.ClientSession()

    @asyncio.coroutine
    def get_devices(self):
        return (yield from self._get(DEVICE_URL.format(username= self._username)))

    @asyncio.coroutine
    def get_last_data(self, uuid, period=0, average_by=0):
        return self.parse_data((yield from self._get(
            LAST_DATA_URL.format(uuid= uuid,
                period= trunc(period),
                average_by= trunc(average_by)))))

    @asyncio.coroutine
    def get_historical_data(self, uuid, start, end, average_by=0):
        return self.parse_data((yield from self._get(
            HISTORICAL_DATA_URL.format(uuid= uuid,
                start = trunc(start.replace(tzinfo=timezone.utc).timestamp()),
                end = trunc(end.replace(tzinfo=timezone.utc).timestamp()),
                average_by= trunc(average_by)))))

    def parse_data(self, response):
        parsed = []
        items = response['sensors']
        for datapoint in response['datapoints']:
            line = {}
            for index, data in enumerate(datapoint):
                line[items[index]] = data
            parsed.append(line)
        return parsed

    @asyncio.coroutine
    def _get(self, path, **kwargs):
        with async_timeout.timeout(self._timeout):
            resp = yield from self._session.get(
                    path, headers=dict(self._headers, **kwargs))
            if resp.status == 400:
                raise BadFormat(resp.text())
            elif resp.status == 401:
                raise AuthFailure(resp.text())
            elif resp.status == 403:
                raise ForbiddenAccess(resp.text())
            elif resp.status == 429:
                raise TooManyRequests(resp.text())
            elif resp.status == 500:
                raise InternalError(resp.text())
            elif resp.status != 200:
                raise FoobotClientError(resp.text())
            return (yield from resp.json())

class FoobotClientError(Exception):
    pass

class AuthFailure(FoobotClientError):
    pass

class BadFormat(FoobotClientError):
    pass

class ForbiddenAccess(FoobotClientError):
    pass

class TooManyRequests(FoobotClientError):
    pass

class InternalError(FoobotClientError):
    pass
