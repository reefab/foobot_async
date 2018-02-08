import aiohttp
import asyncio
import pytest
from aioresponses import aioresponses
from datetime import datetime
from foobot_async import *

client = FoobotClient('token', 'example@example.com')
loop = asyncio.get_event_loop()

def test_get_devices_request():

    with aioresponses() as mocked:
        mocked.get('https://api.foobot.io/v2/owner/example@example.com/device/',
                   status=200, body='''[{"uuid": "1234127987696AB",
                                       "userId": 2353,
                                       "mac": "013843C3C20A",
                                       "name": "FooBot"}]''')
        resp = loop.run_until_complete(client.get_devices())

        assert [dict(uuid="1234127987696AB",
                     userId= 2353,
                     mac= "013843C3C20A",
                     name= "FooBot")] == resp

def test_get_devices_with_session_request():
    session = aiohttp.ClientSession()
    client = FoobotClient('token', 'example@example.com', session)

    with aioresponses() as mocked:
        mocked.get('https://api.foobot.io/v2/owner/example@example.com/device/',
                   status=200, body='''[{"uuid": "1234127987696AB",
                                       "userId": 2353,
                                       "mac": "013843C3C20A",
                                       "name": "FooBot"}]''')
        resp = loop.run_until_complete(client.get_devices())

        assert [dict(uuid="1234127987696AB",
                     userId= 2353,
                     mac= "013843C3C20A",
                     name= "FooBot")] == resp

def test_failed_auth_request():
    with aioresponses() as mocked:
        mocked.get('https://api.foobot.io/v2/owner/example@example.com/device/',
                   status=401, body='{"message": "invalid key provided"}')

        with pytest.raises(AuthFailure):
            resp = loop.run_until_complete(client.get_devices())

def test_failed_bad_format_request():
    with aioresponses() as mocked:
        mocked.get('https://api.foobot.io/v2/owner/example@example.com/device/',
                   status=400, body='''{"state": 400,
                                        "message": "ParseException : Bad date format : bad date format [test]",
                                        "requestedUri": "/v2/device/26025766336015C0/datapoint/test/last/test/",
                                        "stack": "[obfuscated]",
                                        "propagatedException": null}''')

        with pytest.raises(BadFormat):
            resp = loop.run_until_complete(client.get_devices())

def test_forbidden_access_request():
    with aioresponses() as mocked:
        mocked.get('https://api.foobot.io/v2/owner/example@example.com/device/',
                   status=403, body='''{"{"state": 403, "message": null,
                                         "stack": "403 - Forbidden",
                                         "propagatedException": null }":
                                         "invalid key provided"}''')

        with pytest.raises(ForbiddenAccess):
            resp = loop.run_until_complete(client.get_devices())

def test_overquota_request():
    with aioresponses() as mocked:
        mocked.get('https://api.foobot.io/v2/owner/example@example.com/device/',
                   status=429, body='')

        with pytest.raises(TooManyRequests):
            resp = loop.run_until_complete(client.get_devices())

def test_internal_error_request():
    with aioresponses() as mocked:
        mocked.get('https://api.foobot.io/v2/owner/example@example.com/device/',
                   status=500, body='')

        with pytest.raises(InternalError):
            resp = loop.run_until_complete(client.get_devices())

def test_unhandled_error_request():
    with aioresponses() as mocked:
        mocked.get('https://api.foobot.io/v2/owner/example@example.com/device/',
                   status=404, body='')

        with pytest.raises(FoobotClientError):
            resp = loop.run_until_complete(client.get_devices())

def test_get_last_data_request():
    body = '''{"uuid": "1234127987696AB",
               "start": 1518131274,
               "end": 1518131874,
               "sensors": ["time", "pm", "tmp", "hum", "co2", "voc", "allpollu"],
               "units": [ "s", "ugm3", "C", "pc", "ppm", "ppb", "%" ],
               "datapoints": [ [ 1518131274, 135.70001, 21.046001, 46.6885, 1178.0,
                               325.5, 131.19643 ] ] }'''

    with aioresponses() as mocked:
        mocked.get('https://api.foobot.io/v2/device/1234127987696AB/datapoint/600/last/601/',
                   status=200, body=body)

        resp = loop.run_until_complete(client.get_last_data("1234127987696AB",
                                                       600, 601))
        assert dict(time = 1518131274,
                    pm = 135.70001,
                    tmp = 21.046001,
                    hum = 46.6885,
                    co2 = 1178.0,
                    voc = 325.5,
                    allpollu= 131.19643) == resp[0]

def test_get_historical_data_request():
    body = '''{"uuid": "1234127987696AB",
               "start": 1518131274,
               "end": 1518131874,
               "sensors": ["time", "pm", "tmp", "hum", "co2", "voc", "allpollu"],
               "units": [ "s", "ugm3", "C", "pc", "ppm", "ppb", "%" ],
               "datapoints": [ [ 1518131274, 135.70001, 21.046001, 46.6885, 1178.0,
                               325.5, 131.19643 ] ] }'''

    with aioresponses() as mocked:
        mocked.get('https://api.foobot.io/v2/device/1234127987696AB/datapoint/1518121274/1518131274/3600/',
                   status=200, body=body)

        resp = loop.run_until_complete(client.get_historical_data("1234127987696AB",
                                                                   datetime.utcfromtimestamp(1518121274),
                                                                   datetime.utcfromtimestamp(1518131274),
                                                                   3600))
        assert dict(time = 1518131274,
                    pm = 135.70001,
                    tmp = 21.046001,
                    hum = 46.6885,
                    co2 = 1178.0,
                    voc = 325.5,
                    allpollu= 131.19643) == resp[0]
