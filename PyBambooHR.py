#!/usr/bin/env python
#encoding:utf-8
#author:smeggingsmegger/Scott Blevins
#project:PyBambooHR
#repository:http://github.com/smeggingsmegger/PyBambooHR
#license:agpl-3.0 (http://www.gnu.org/licenses/agpl-3.0.en.html)

"""
"""

import requests

class PyBambooHR(object):
    def __init__(self, datatype='JSON', api_key='', subdomain=''):
        # API Version
        self.api_version = 'v1'

        # Global headers
        self.headers = {}

        # Referred to in the documentation as [ Company ] sometimes.
        self.subdomain = subdomain

        # All requests will start with this url
        self.base_url = 'https://api.bamboohr.com/api/gateway.php/{0}/{1}/'.format(self.subdomain, self.api_version)

        # JSON or XML
        self.datatype = datatype

        # You must create an API key through the BambooHR interface
        self.api_key = api_key

        # We are focusing on JSON for now.
        if self.datatype == 'XML':
            raise NotImplemented("Returning XML is not currently supported.")

        if self.datatype == 'JSON':
            self.headers.update({'Accept': 'application/json'})

    def get_employee_directory(self):
        url = self.base_url + 'employees/directory'
        r = requests.get(url, headers=self.headers, auth=(self.api_key, ''))
        return r.json()

    def get_employee(self, employee_id, field_list=None):
        fields = {
            'address1': ('text', "The employee's first address line"),
            'address2': ('text', "The employee's second address line"),
            'age': ('integer', "The employee's age. Not editable. To change update dateOfBirth, instead."),
            'benefitClassChangeReason': ('list', ''),
            'benefitClassClass': ('list', ''),
            'bestEmail': ('email', "The employee's work email if set, otherwise their home email"),
            'birthday': ('text', "The employee's month and day of birth. Not editable. To change update dateOfBirth, instead."),
            'city': ('text', "The employee's city"),
            'country': ('country', "The employee's country"),
            'dateOfBirth': ('date', 'The date the employee was born'),
            'department': ('list', "The employee's CURRENT department."),
            'division': ('list', "The employee's CURRENT division"),
            'eeo': ('list', "The employee's EEO job category. These are defined by the U.S. Equal Employment Opportunity Commission"),
            'employeeNumber': ('text', 'Employee number (assigned by your company)'),
            'employmentHistoryStatus': ('list', "The employee's CURRENT employment status. Options are customized by account."),
            'employmentStatus': ('status', 'DEPRECATED. Please use "status" instead. The employee\'s employee status (Active,Inactive)'),
            'ethnicity': ('list', "The employee's ethnicity"),
            'exempt': ('list', 'The FLSA employee exemption code (Exempt or Non-exempt)'),
            'firstName': ('text', "The employee's first name"),
            'flsaCode': ('list', '''The employee's FLSA code. Ie: "Exempt", "Non-excempt"'''),
            'fullName1': ('text', "Employee's first and last name. Example: John Doe. Ready only."),
            'fullName2': ('textfullName2', 'textfullName2'),
            'photoUploaded': ('bool', 'The employee has uploaded a photo'),
            'rehireDate': ('date', 'TherehireDateemrehireDate'),
            'sin': ('sin', "The employee's Canadian Social Insurance Number"),
            'state': ('state', "The employee's state/province"),
            'stateCode': ('text', "The 2 character abbreviation for the employee's state (US only). Not editable."),
            'status': ('status', '"status" indicates whether you are using BambooHR to track data about this employee. Valid values are "Active", "Inactive".'),
            'supervisor': ('employee', "The emloyee's CURRENT supervisor. Not editable."),
            'supervisorEId': ('integer', "The 'id' of the employee's CURRENT supervisor. Not editable."),
            'supervisorId': ('integer', "The 'employeeNumber' of the employee's CURRENT supervisor. Not editable."),
            'terminationDate': ('date', 'The date the employee was terminated'),
            'workEmail': ('email', "The employee's work email address"),
            'workPhone': ('phone', "The employee's work phone number, without extension"),
            'workPhoneExtension': ('text', 'The employees work phone extension (if any)'),
            'workPhonePlusExtension': ('text', "The employee's work phone and extension. Not editable."),
            'zipcode': ('text', "The employee's zipcode")
        }

        get_fields = []

        if field_list:
            for f in field_list:
                if not fields.get(f):
                    raise UserWarning("You passed in an invalid field")
                else:
                    get_fields.append(f)
        else:
            for field in fields:
                get_fields.append(field)

        payload = {
            'fields': ",".join(get_fields)
        }

        url = self.base_url + "employees/{0}".format(employee_id)
        r = requests.get(url, headers=self.headers, params=payload, auth=(self.api_key, ''))
        return r.json()
