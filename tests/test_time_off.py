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

    @httpretty.activate
    def test_create_time_off_request(self):
        body = {'id': '1675', 'employeeId': '111', 'start': '2040-02-01', 'end': '2040-02-02', 'created': '2019-12-24', 'status': {'status': 'requested', 'lastChanged': '2019-12-24 02:29:45', 'lastChangedByUserId': '2479'}, 'name': 'xdd xdd', 'type': {'id': '78', 'name': 'Vacation'}, 'amount': {'unit': 'hours', 'amount': '2'}, 'notes': {'employee': 'Going overseas with family', 'manager': 'Enjoy!'}, 'dates': {'2040-02-01': '1', '2040-02-02': '1'}, 'comments': [{'employeeId': '111', 'comment': 'Enjoy!', 'commentDate': '2019-12-24', 'commenterName': 'Test use'}], 'approvers': [{'userId': '2479', 'displayName': 'Test user', 'employeeId': '111', 'photoUrl': 'https://resources.bamboohr.com/employees/photos/initials.php?initials=testuser'}], 'actions': {'view': True, 'edit': True, 'cancel': True, 'approve': True, 'deny': True, 'bypass': True}, 'policyType': 'discretionary', 'usedYearToDate': 0, 'balanceOnDateOfRequest': 0}
        httpretty.register_uri(httpretty.PUT,
            "https://api.bamboohr.com/api/gateway.php/test/v1/employees/111/time_off/request",
            body=dumps(body),
            content_type="application/json")
        data = {
            'status': 'requested',
            'employee_id': '111',
            'start': '2040-02-01',
            'end': '2040-02-02',
            'timeOffTypeId': '78',
            'amount': '2',
            'dates': [
                { 'ymd': '2040-02-01', 'amount': '1' },
                { 'ymd': '2040-02-02', 'amount': '1' }
            ],
            'notes': [
                { 'type': 'employee', 'text': 'Going overseas with family' },
                { 'type': 'manager', 'text': 'Enjoy!' }
            ]
        }
        response = self.bamboo.create_time_off_request(data)
        self.assertIsNotNone(response)
        self.assertEquals(response['id'], '1675')
        return

    @httpretty.activate
    def test_update_time_off_request_status(self):
        body = {'id': '1675', 'employeeId': '111', 'start': '2040-02-01', 'end': '2040-02-02', 'created': '2019-12-24', 'status': {'status': 'declined', 'lastChanged': '2019-12-24 02:29:45', 'lastChangedByUserId': '2479'}, 'name': 'xdd xdd', 'type': {'id': '78', 'name': 'Vacation'}, 'amount': {'unit': 'hours', 'amount': '2'}, 'notes': {'employee': 'Going overseas with family', 'manager': 'Enjoy!'}, 'dates': {'2040-02-01': '1', '2040-02-02': '1'}, 'comments': [{'employeeId': '111', 'comment': 'Enjoy!', 'commentDate': '2019-12-24', 'commenterName': 'Test use'}], 'approvers': [{'userId': '2479', 'displayName': 'Test user', 'employeeId': '111', 'photoUrl': 'https://resources.bamboohr.com/employees/photos/initials.php?initials=testuser'}], 'actions': {'view': True, 'edit': True, 'cancel': True, 'approve': True, 'deny': True, 'bypass': True}, 'policyType': 'discretionary', 'usedYearToDate': 0, 'balanceOnDateOfRequest': 0}
        httpretty.register_uri(httpretty.PUT,
            "https://api.bamboohr.com/api/gateway.php/test/v1/time_off/requests/1675/status",
            body=dumps(body),
            content_type="application/json")
        data = {
            'status': 'declined',
            'note': 'Have fun!'
        }
        response = self.bamboo.update_time_off_request_status(body['id'] ,data)
        self.assertIsNotNone(response)
        self.assertTrue(response)
        return