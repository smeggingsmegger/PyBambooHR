#!/usr/bin/env python
#encoding:utf-8
#author:smeggingsmegger/Scott Blevins
#project:PyBambooHR
#repository:http://github.com/smeggingsmegger/PyBambooHR
#license:agpl-3.0 (http://www.gnu.org/licenses/agpl-3.0.en.html)

"""Unittests for employees api
"""

import httpretty
import os
import sys
import unittest

from json import dumps

# Force parent directory onto path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyBambooHR import PyBambooHR

class test_reports(unittest.TestCase):
    # Used to store the cached instance of PyBambooHR
    bamboo = None

    # Another instance, using underscore keys
    bamboo_u = None

    # Common report response body:
    body = None

    def setUp(self):
        if self.body is None:
            self.body = dumps({"title":"Template","fields":[{"id":"fullName2","type":"text","name":"Last Name, First Name"},{"id":"employeeNumber","type":"employee_number","name":"Employee #"},{"id":"hireDate","type":"date","name":"Hire date"}],"employees":[{"id":"123","fullName2":"Person, Test","employeeNumber":"00001","hireDate":"2010-12-15"},{"id":"124","fullName2":"Guy, Someother","employeeNumber":"00002","hireDate":"2008-10-13"},{"id":"125","fullName2":"Here, Someone","employeeNumber":"00003","hireDate":"2011-03-04"}]})

        if self.bamboo is None:
            self.bamboo = PyBambooHR(subdomain='test', api_key='testingnotrealapikey')

        if self.bamboo_u is None:
            self.bamboo_u = PyBambooHR(subdomain='test', api_key='testingnotrealapikey', underscore_keys=True)

    @httpretty.activate
    def test_request_company_report(self):
        httpretty.register_uri(httpretty.GET, "https://api.bamboohr.com/api/gateway.php/test/v1/reports/1?format=json&fd=yes",
                               status=200, body=self.body, content_type="application/json")

        result = self.bamboo.request_company_report(1, report_format='json', filter_duplicates=True)
        self.assertIsNotNone(result['fields'])
        self.assertEquals('123', result['employees'][0]['id'])

    @httpretty.activate
    def test_company_report_format_failure(self):
        httpretty.register_uri(httpretty.GET, "https://api.bamboohr.com/api/gateway.php/test/v1/reports/1?format=json&fd=yes",
                               status=200, body=self.body, content_type="application/json")

        self.assertRaises(UserWarning, self.bamboo.request_company_report, 1, report_format='gif', filter_duplicates=True)

    @httpretty.activate
    def test_request_custom_report(self):
        httpretty.register_uri(httpretty.POST, "https://api.bamboohr.com/api/gateway.php/test/v1/reports/custom/?format=xls",
                               status=200, body=self.body, content_type="application/vnd.ms-excel")

        result = self.bamboo.request_custom_report(['id', 'firstName', 'lastName', 'workEmail'], report_format='xls')
        self.assertEquals(result.headers['status'], '200')
        self.assertEquals(result.headers['content-type'], 'application/vnd.ms-excel')

    @httpretty.activate
    def test_company_custom_format_failure(self):
        httpretty.register_uri(httpretty.GET, "https://api.bamboohr.com/api/gateway.php/test/v1/reports/1?format=json&fd=yes",
                               status=200, body=self.body, content_type="application/json")

        self.assertRaises(UserWarning, self.bamboo.request_custom_report, 1, report_format='gif')

