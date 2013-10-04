#!/usr/bin/env python
#encoding:utf-8
#author:smeggingsmegger/Scott Blevins
#project:PyBambooHR
#repository:http://github.com/smeggingsmegger/PyBambooHR
#license:agpl-3.0 (http://www.gnu.org/licenses/agpl-3.0.en.html)

"""Unittests for misc. functions
"""

import httpretty
import os
import sys
import unittest

# Force parent directory onto path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyBambooHR import PyBambooHR

class test_misc(unittest.TestCase):
    # Used to store the cached instance of PyBambooHR
    bamboo = None

    def setUp(self):
        if self.bamboo is None:
            self.bamboo = PyBambooHR(subdomain='test', api_key='testingnotrealapikey')

    def test_employee_xml(self):
        employee = {
            'firstName': 'Test',
            'lastName': 'Person'
        }
        xml = self.bamboo._format_employee_xml(employee)
        self.assertIn('<field id="firstName">Test</field>', xml)
        self.assertIn('<field id="lastName">Person</field>', xml)
