#!/usr/bin/env python
#encoding:utf-8
#author:smeggingsmegger/Scott Blevins
#project:PyBambooHR
#repository:http://github.com/smeggingsmegger/PyBambooHR
#license:agpl-3.0 (http://www.gnu.org/licenses/agpl-3.0.en.html)

"""Unittests for tvdb_api
"""

import httpretty
import os
import sys
import unittest

# Force parent directory onto path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyBambooHR import PyBambooHR

class test_employees(unittest.TestCase):
    # Used to store the cached instance of PyBambooHR
    bamboo = None

    def setUp(self):
        if self.bamboo is None:
            self.bamboo = PyBambooHR(subdomain='test', api_key='testingnotrealapikey')

    @httpretty.activate
    def test_get_employee_specific_fields(self):
        # Request specific fields
        httpretty.register_uri(httpretty.GET, "https://api.bamboohr.com/api/gateway.php/test/v1/employees/123",
                               body='{"workEmail": "user@test.com", "workPhone": "555-555-5555", "id": "123"}',
                               content_type="application/json")

        employee = self.bamboo.get_employee(123, ['workPhone', 'workEmail'])
        self.assertIsNotNone(employee)
        self.assertEquals(employee['workEmail'], 'user@test.com')
        self.assertEquals(employee['workPhone'], '555-555-5555')
        self.assertEquals(employee['id'], '123')

    @httpretty.activate
    def test_get_employee_all_fields(self):
        # Request all fields
        # NOTE: We are mocking this so we aren't getting all fields- we are just adding city.
        httpretty.register_uri(httpretty.GET, "https://api.bamboohr.com/api/gateway.php/test/v1/employees/123",
                               body='{"workEmail": "user@test.com", "workPhone": "555-555-5555", "id": "123", "city": "Testville"}',
                               content_type="application/json")

        employee = self.bamboo.get_employee(123)
        self.assertIsNotNone(employee)
        self.assertEquals(employee['workEmail'], 'user@test.com')
        self.assertEquals(employee['workPhone'], '555-555-5555')
        self.assertEquals(employee['city'], 'Testville')
        self.assertEquals(employee['id'], '123')
