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

    def test_make_field_xml(self):
        xml = utils.make_field_xml('123', 'T&C')
        self.assertEqual('<field id="123">T&amp;C</field>', xml)

        xml = utils.make_field_xml('123', 'T&C', pre='\t', post='\n')
        self.assertEqual('\t<field id="123">T&amp;C</field>\n', xml)

        xml = utils.make_field_xml('123', None, pre='\t', post='\n')
        self.assertEqual('\t<field id="123" />\n', xml)

        xml = utils.make_field_xml('123', u'Úñíçôdé')
        self.assertEqual(u'<field id="123">Úñíçôdé</field>', xml)

    def test__format_row_xml(self):
        row = {'f1': 'v1', 'f2': 'v2'}
        xml = self.bamboo._format_row_xml(row)
        self.assertIn('<field id="f1">v1</field>', xml)
        self.assertIn('<field id="f2">v2</field>', xml)

    def test_transform_tabular_data(self):
        xml = """<?xml version="1.0"?>
                 <table>
                   <row id="321" employeeId="123">
                     <field id="customFieldA">123 Value A</field>
                     <field id="customFieldB">123 Value B</field>
                   </row>
                   <row id="999" employeeId="321">
                     <field id="customFieldA">321 &amp; Value A</field>
                   </row>
                 </table>"""
        table = {'123': [{
                         'customFieldA': '123 Value A',
                         'customFieldB': '123 Value B',
                         'row_id': '321'}],
                 '321': [{
                         'customFieldA': '321 & Value A',
                         'row_id': '999'}]}
        self.assertEqual(table, utils.transform_tabular_data(xml))

    def test_transform_tabular_data_single_row(self):
        xml = """<?xml version="1.0"?>
                 <table>
                   <row id="321" employeeId="123">
                     <field id="customFieldA">123 Value A</field>
                   </row>
                 </table>"""
        table = {'123': [{'customFieldA': '123 Value A', 'row_id': '321'}]}
        self.assertEqual(table, utils.transform_tabular_data(xml))

    def test_transform_tabular_data_empty_table(self):
        xml = """<?xml version="1.0"?>
                     <table/>"""
        table = {}
        self.assertEqual(table, utils.transform_tabular_data(xml))

    def test_transform_tabular_data_empty_field(self):
        xml = """<?xml version="1.0"?>
                 <table>
                   <row id="321" employeeId="123">
                     <field id="customFieldA">123 Value A</field>
                     <field id="customFieldC"></field>
                   </row>
                   <row id="999" employeeId="321">
                     <field id="customFieldB">321 Value B</field>
                   </row>
                 </table>"""
        table = {'123': [{'customFieldA': '123 Value A',
                          'customFieldC': None,
                          'row_id': '321'}],
                 '321': [{'customFieldB': '321 Value B',
                          'row_id': '999'}]}

        self.assertEqual(table, utils.transform_tabular_data(xml))
