"""Unittests for time off api
"""

import httpretty
import os
import sys
import unittest

from json import dumps
from requests import HTTPError

# Force parent directory onto path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyBambooHR import PyBambooHR

class test_time_off(unittest.TestCase):
    # Used to store the cached instance of PyBambooHR
    bamboo = None

    def setUp(self):
        if self.bamboo is None:
            self.bamboo = PyBambooHR(subdomain='test', api_key='testingnotrealapikey')

    @httpretty.activate
    def test_get_time_off_requests(self):
        body = [{"id": "1342", "employeeId": "4", "status": {"lastChanged": "2019-09-12", "lastChangedByUserId": "2369", "status": "approved"}, "name": "Charlotte Abbott", "start": "2019-05-30", "end": "2019-06-01", "created": "2019-09-11", "type": {"id": "78", "name": "Vacation", "icon": "palm-trees"}, "amount": {"unit": "hours", "amount": "24"}, "actions": {"view": True, "edit": True, "cancel": False, "approve": False, "deny": False, "bypass": False}, "dates": {"2019-05-30": "24"}, "notes": {"manager": "Home sick with the flu."}}]
        httpretty.register_uri(httpretty.GET,
            "https://api.bamboohr.com/api/gateway.php/test/v1/time_off/requests",
            body=dumps(body),
            content_type="application/json")

        response = self.bamboo.get_time_off_requests()
        self.assertIsNotNone(response)
        self.assertTrue(len(response) > 0)
        self.assertEquals(response[0]['id'], '1342')
        return

    @httpretty.activate
    def test_get_time_off_policies(self):
        body = [{'id': '70', 'timeOffTypeId': '77', 'name': 'Testing Manual Policy', 'effectiveDate': None, 'type': 'manual'}]
        httpretty.register_uri(httpretty.GET,
            "https://api.bamboohr.com/api/gateway.php/test/v1/meta/time_off/policies",
            body=dumps(body),
            content_type="application/json")
        response = self.bamboo.get_time_off_policies()
        self.assertIsNotNone(response)
        self.assertTrue(len(response) > 0)
        self.assertEquals(response[0]['id'], '70')
        return

    @httpretty.activate
    def test_get_time_off_types(self):
        body = {'timeOffTypes': [{'id': '78', 'name': 'Vacation', 'units': 'hours', 'color': None, 'icon': 'palm-trees'}]}
        httpretty.register_uri(httpretty.GET,
            "https://api.bamboohr.com/api/gateway.php/test/v1/meta/time_off/types",
            body=dumps(body),
            content_type="application/json")
        response = self.bamboo.get_time_off_types()
        self.assertIsNotNone(response)
        self.assertTrue(len(response) > 0)
        self.assertEquals(response[0]['id'], '78')
        return