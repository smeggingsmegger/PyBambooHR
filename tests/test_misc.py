#!/usr/bin/env python
#encoding:utf-8
#author:smeggingsmegger/Scott Blevins
#project:PyBambooHR
#repository:http://github.com/smeggingsmegger/PyBambooHR
#license:agpl-3.0 (http://www.gnu.org/licenses/agpl-3.0.en.html)

"""Unittests for misc. functions
"""

import os
import sys
import unittest

# Force parent directory onto path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyBambooHR import PyBambooHR, utils


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

    def test_init_value_errors(self):
        self.assertRaises(ValueError, PyBambooHR, {'subdomain': 'test'})
        self.assertRaises(ValueError, PyBambooHR, {'api_key': 'testingnotrealapikey'})
        self.assertIsNotNone(PyBambooHR(subdomain='test', api_key='testingnotrealapikey'))

    def test_xml(self):
        xml = """<?xml version="1.0"?>
                     <table>
                       <row id="321" employeeId="123">
                           <field id="customFieldA">123 Value A</field>
                           <field id="customFieldB">123 Value B</field>
                       </row>
                       <row id="999" employeeId="321">
                           <field id="customFieldA">321 Value A</field>
                           <field id="customFieldB">321 Value B</field>
                       </row>
                     </table>"""
        obj = utils._parse_xml(xml)

        row_id_one = obj['table']['row'][0]['@id']
        row_id_two = obj['table']['row'][1]['@id']

        self.assertEqual('321', row_id_one)
        self.assertEqual('999', row_id_two)

        employee_id_one = obj['table']['row'][0]['@employeeId']
        employee_id_two = obj['table']['row'][1]['@employeeId']

        self.assertEqual('123', employee_id_one)
        self.assertEqual('321', employee_id_two)

        rows = utils._extract(obj, 'table', 'row')

        self.assertEqual('123 Value A', rows[0]['field'][0]['#text'])
        self.assertEqual('123 Value B', rows[0]['field'][1]['#text'])

        self.assertEqual('321 Value A', rows[1]['field'][0]['#text'])
        self.assertEqual('321 Value B', rows[1]['field'][1]['#text'])
