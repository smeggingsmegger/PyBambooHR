#!/usr/bin/env python
#encoding:utf-8
#author:smeggingsmegger/Scott Blevins
#project:PyBambooHR
#repository:http://github.com/smeggingsmegger/PyBambooHR
#license:mit (http://opensource.org/licenses/MIT)

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

        self.employee_fields = {
            "address1": ("text", "The employee's first address line"),
            "address2": ("text", "The employee's second address line"),
            "age": ("integer", "The employee's age. Not editable. To change update dateOfBirth, instead."),
            "bestEmail": ("email", "The employee's work email if set, otherwise their home email"),
            "birthday": ("text", "The employee's month and day of birth. Not editable. To change update dateOfBirth, instead."),
            "city": ("text", "The employee's city"),
            "country": ("country", "The employee's country"),
            "dateOfBirth": ("date", "The date the employee was born"),
            "department": ("list", "The employee's CURRENT department."),
            "division": ("list", "The employee's CURRENT division"),
            "eeo": ("list", "The employee's EEO job category. These are defined by the U.S. Equal Employment Opportunity Commission"),
            "employeeNumber": ("text", "Employee number (assigned by your company)"),
            "employmentStatus": ("status", "DEPRECATED. Please use 'status' instead. The employee's employee status (Active,Inactive)"),
            "employmentHistoryStatus": ("list", "The employee's CURRENT employment status. Options are customized by account."),
            "ethnicity": ("list", "The employee's ethnicity"),
            "exempt": ("list", "The FLSA employee exemption code (Exempt or Non-exempt)"),
            "firstName": ("text", "The employee's first name"),
            "flsaCode": ("list", "The employee's FLSA code. Ie: 'Exempt', 'Non-excempt'"),
            "fullName1": ("text", "Employee's first and last name. Example: John Doe. Ready only."),
            "fullName2": ("text", "Employee's last and first name. Example: Doe, John. Read only."),
            "fullName3": ("text", "Employee's full name with nickname. Example: Doe, John Quentin (JDog). Read only."),
            "fullName4": ("text", "employee's full name without nickname. Last name first. Example: Doe, John Quentin. Read only"),
            "fullName5": ("text", "employee's full name without nickname. First name first. Example: John Quentin Doe. Read only"),
            "displayName": ("text", "employee's name displayed in a format configured by the user. Read only"),
            "gender": ("gender", "The employee's gender. Legal values are 'Male', 'Female'"),
            "hireDate": ("date", "The date the employee was hired"),
            "homeEmail": ("email", "The employee's home email address"),
            "homePhone": ("phone", "The employee's home phone number"),
            "id": ("integer", "Employee id (automatically assigned by BambooHR). Not editable."),
            "jobTitle": ("list", "The CURRENT value of the employee's job title, updating this field will create a new row in position history"),
            "lastChanged": ("timestamp", "The date and time that the employee record was last changed"),
            "lastName": ("text", "The employee's last name"),
            "location": ("list", "The employee's CURRENT location"),
            "maritalStatus": ("list", "The employee's marital status ('Single' or 'Married')"),
            "middleName": ("text", "The employee's middle name"),
            "mobilePhone": ("phone", "The employee's mobile phone number"),
            "nickname": ("text", "The employee's nickname"),
            "payChangeReason": ("list", "The reason for the employee's last pay rate change."),
            "payGroup": ("list", "The custom pay group that the employee belongs to."),
            "payGroupId": ("integer", "The id value corresponding to the pay group that an employee belongs to"),
            "payRate": ("currency", "The employee's CURRENT pay rate. ie: $8.25"),
            "payRateEffectiveDate": ("date", "The date most recent change was made."),
            "payType": ("pay_type", "The employee's CURRENT pay type. ie: 'hourly','salary','commission','exception hourly','monthly','piece rate','contract','daily'"),
            "ssn": ("ssn", "The employee's social security number"),
            "sin": ("sin", "The employee's Canadian Social Insurance Number"),
            "state": ("state", "The employee's state/province"),
            "stateCode": ("text", "The 2 character abbreviation for the employee's state (US only). Not editable."),
            "status": ("status", "'status' indicates whether you are using BambooHR to track data about this employee. Valid values are 'Active', 'Inactive'."),
            "supervisor": ("employee", "The emloyee’s CURRENT supervisor. Not editable."),
            "supervisorId": ("integer", "The 'employeeNumber' of the employee's CURRENT supervisor. Not editable."),
            "supervisorEId": ("integer", "The 'id' of the employee's CURRENT supervisor. Not editable."),
            "terminationDate": ("date", "The date the employee was terminated"),
            "workEmail": ("email", "The employee's work email address"),
            "workPhone": ("phone", "The employee's work phone number, without extension"),
            "workPhonePlusExtension": ("text", "The employee's work phone and extension. Not editable."),
            "workPhoneExtension": ("text", "The employees work phone extension (if any)"),
            "zipcode": ("text", "The employee's zipcode"),
            "photoUploaded": ("bool", "The employee has uploaded a photo"),
            "rehireDate": ("date", "The date the employee was rehired"),
            "adpCompanyCode": ("list", ""),
            "adpFileNumber": ("text", ""),
            "standardHoursPerWeek": ("integer", ""),
            "earningsDate": ("date", ""),
            "earningsPriorYear": ("currency", ""),
            "bonusDate": ("date", ""),
            "bonusAmount": ("currency", ""),
            "bonusReason": ("list", ""),
            "bonusComment": ("text", ""),
            "commisionDate": ("date", ""),
            "commissionAmount": ("currency", ""),
            "commissionComment": ("text", ""),
            "commissionComment": ("text", ""),
            "benefitClassDate": ("date", ""),
            "benefitClassClass": ("list", ""),
            "benefitClassChangeReason": ("list", ""),
        }

    def _format_employee_xml(self, employee):
        xml_fields = ''
        for key in employee:
            if not self.employee_fields.get(key):
                raise UserWarning("You passed in an invalid field")
            else:
                xml_fields += '\t<field id="{0}">{1}</field>\n'.format(key, employee[key])

        # Really cheesy way to build XML... this should probably be replaced at some point.
        xml = "<employee>\n{}</employee>".format(xml_fields)
        return xml

    def add_employee(self, employee):
        if not employee.get('firstName') or not employee.get('lastName'):
            raise UserWarning("The 'firstName' and 'lastName' keys are required.")

        xml = self._format_employee_xml(employee)
        url = self.base_url + 'employees/'
        r = requests.post(url, data=xml, headers=self.headers, auth=(self.api_key, ''))
        return {'url': r.headers['location'], 'id': r.headers['location'].replace(url, "")}

    def update_employee(self, id, employee):
        xml = self._format_employee_xml(employee)
        url = self.base_url + 'employees/{0}'.format(id)
        r = requests.post(url, data=xml, headers=self.headers, auth=(self.api_key, ''))
        return_value = r.status_code == 200
        return return_value

    def get_employee_directory(self):
        url = self.base_url + 'employees/directory'
        r = requests.get(url, headers=self.headers, auth=(self.api_key, ''))
        return r.json()

    def get_employee(self, employee_id, field_list=None):

        get_fields = []

        if field_list:
            for f in field_list:
                if not self.employee_fields.get(f):
                    raise UserWarning("You passed in an invalid field")
                else:
                    get_fields.append(f)
        else:
            for field in self.employee_fields:
                get_fields.append(field)

        payload = {
            'fields': ",".join(get_fields)
        }

        url = self.base_url + "employees/{0}".format(employee_id)
        r = requests.get(url, headers=self.headers, params=payload, auth=(self.api_key, ''))
        return r.json()
