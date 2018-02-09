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
    """
    Foobot API client

    :param token: API secret key used for authentication, see main doc on how 
        to obtain one
    :type token: str
    :param username: Your username for your Foobot account
    :type username: str
    :param session: aiohttp session to use or None
    :type session: object or None
    :param timeout: seconds to wait for before triggering a timeout
    :type timeout: integer
    """

    def __init__(self, token, username, session=None,
                 timeout=aiohttp.client.DEFAULT_TIMEOUT):
        """
        Creates a new :class:`FoobotClient` instance.
        """
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
        """
        Get a list of devices associated with that account.

        :returns: list of devices
        :raises: FoobotClientError, AuthFailure, BadFormat, ForbiddenAccess,
                 TooManyRequests, InternalError

        .. note::
            each device returned will be a dictionary with the following data:
                * uuid: id of the device, used for querying data from them. Not actually a UUID.
                * userId: id of the user
                * mac: MAC of the device, non colon seperated (eg: "013843C3C20A")
                * name: Name of the device as configured in the app
        """
        return (yield from self._get(DEVICE_URL.format(username= self._username)))

    @asyncio.coroutine
    def get_last_data(self, uuid, period=0, average_by=0):
        """
        Get the data from one device for period till now.

        :param uuid: Id of the device
        :type uuid: str
        :param period: Number of seconds between start time of search and now
        :type period: integer
        :param average_by: amount of seconds to average data over.
            0 or 300 for no average. Use 3600 (average hourly) or a multiple for
            long range requests (e.g. more than 1 day)
        :type average_by: integer
        :returns: list of datapoints
        :raises: FoobotClientError, AuthFailure, BadFormat, ForbiddenAccess,
                 TooManyRequests, InternalError

        .. note::
            Use period = 0 and averageBy = 0 to get the very last data point.
            If you only need one average for a period, the average_by needs to
            be bigger than the period (eg, for a 10 minutes average: period = 600,
            average_by = 601)

        .. seealso:: :func:`parse_data` for return data syntax
        """
        return self.parse_data((yield from self._get(
            LAST_DATA_URL.format(uuid= uuid,
                period= trunc(period),
                average_by= trunc(average_by)))))

    @asyncio.coroutine
    def get_historical_data(self, uuid, start, end, average_by=0):
        """
        Get the data from one device for a specified time range.

        .. note::
            Can fetch a maximum of 42 days of data.
            To speed up query processing, you can use a combination of average factor
            multiple of 1H in seconds (e.g. 3600), and o'clock start and end times

        :param uuid: Id of the device
        :type uuid: str
        :param start: start of the range
        :type start: datetime
        :param end: end of the range
        :type end: datetime
        :param average_by: amount of seconds to average data over.
            0 or 300 for no average. Use 3600 (average hourly) or a multiple for
            long range requests (e.g. more than 1 day)
        :type average_by: integer
        :returns: list of datapoints
        :raises: FoobotClientError, AuthFailure, BadFormat, ForbiddenAccess,
                 TooManyRequests, InternalError

        .. seealso:: :func:`parse_data` for return data syntax
        """
        return self.parse_data((yield from self._get(
            HISTORICAL_DATA_URL.format(uuid= uuid,
                start = trunc(start.replace(tzinfo=timezone.utc).timestamp()),
                end = trunc(end.replace(tzinfo=timezone.utc).timestamp()),
                average_by= trunc(average_by)))))

    def parse_data(self, response):
        """
        Convert the weird list format used for datapoints to a more usable
        dictionnary one 

        :param response: dictionnary from API json response
        :type response: dict
        :returns: list of datapoints

        .. note::
            Datapoint content:
                * time: UTC timestamp, unit: seconds
                * pm: Particulate Matter, unit: ugm3
                * tmp: temperature, unit: C
                * hum: humidity, unit: %
                * co2: Carbon Dioxide, unit: ppm
                * voc: Volatile Organic Compounds, unit: ppb
                * allpollu: `foobot index <https://help.foobot.io/hc/en-us/articles/204814371-What-does-central-number-mean->`_, unit: %
        """
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
