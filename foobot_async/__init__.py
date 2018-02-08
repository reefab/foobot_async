BASE_URL = "https://api.foobot.io/v2/"
DEVICE_URL = BASE_URL + 'owner/{username}/device/'
DATA_URL = BASE_URL + "device/{uuid}/datapoint/{period:d}/last/{average_by:d}/"

import asyncio
import aiohttp
import async_timeout
from datetime import datetime
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
    def get_data(self, uuid, period, average_by):
        return (yield from self._get(DATA_URL.format(uuid= uuid,
                                                     period= trunc(period),
                                                     average_by= trunc(average_by))))

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
