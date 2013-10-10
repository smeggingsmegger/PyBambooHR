#!/usr/bin/env python
#encoding:utf-8
#author:smeggingsmegger/Scott Blevins
#project:PyBambooHR
#repository:http://github.com/smeggingsmegger/PyBambooHR
#license:mit (http://opensource.org/licenses/MIT)

"""
PyBambooHR.py contains a class by the same name with functions that correspond
to BambooHR API calls defined at http://www.bamboohr.com/api/documentation/.
"""

import requests

from utils import camelcase_keys, underscore_keys, underscore_to_camelcase

class PyBambooHR(object):
    """
    The PyBambooHR class is initialized with an API key, company subdomain,
    and an optional datatype argument (defaults to JSON). This class implements
    methods for basic CRUD operations for employees and more.
    """
    def __init__(self, api_key='', subdomain='', datatype='JSON', underscore_keys=False):
        """
        Using the subdomain, __init__ initializes the base_url for our API calls.
        This method also sets up some headers for our HTTP requests as well as our authentication (API key).

        @param api_key: String containing a valid API Key created in BambooHR.
        @param subdomain: String containing a valid company subdomain for a company in BambooHR.
        @param datatype: String of 'JSON' or 'XML'. Sets the Accept header for return type in our HTTP requests to BambooHR.
        """
        if not api_key:
            raise ValueError('The `api_key` argument can not be empty. Please provide a valid BambooHR API key.')

        if not subdomain:
            raise ValueError('The `subdomain` argument can not be empty. Please provide a valid BambooHR company subdomain.')

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

        # Some people will want to use underscore keys for employee data...
        self.underscore_keys = underscore_keys

        # We are focusing on JSON for now.
        if self.datatype == 'XML':
            raise NotImplemented("Returning XML is not currently supported.")

        if self.datatype == 'JSON':
            self.headers.update({'Accept': 'application/json'})

        # Report formats
        self.report_formats = {
            'csv': 'text/csv',
            'pdf': 'application/pdf',
            'xls': 'application/vnd.ms-excel',
            'xml': 'application/xml',
            'json': 'application/json'
        }

        # These can be used as a reference for available fields, also used to validate
        # fields in get_employee and to grab all available data if no fields are passed in
        # the same function.
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
        """
        Utility method for turning an employee dictionary into valid employee xml.

        @param employee: Dictionary containing employee information.
        """
        xml_fields = ''
        for key in employee:
            if not self.employee_fields.get(key):
                raise UserWarning("You passed in an invalid field")
            else:
                xml_fields += '\t<field id="{0}">{1}</field>\n'.format(key, employee[key])

        # Really cheesy way to build XML... this should probably be replaced at some point.
        xml = "<employee>\n{}</employee>".format(xml_fields)
        return xml

    def _format_report_xml(self, fields, title='My Custom Report', report_format='pdf'):
        """
        Utility method for turning an employee dictionary into valid employee xml.

        @param fields: List containing report fields.
        """
        xml_fields = ''
        for field in fields:
            xml_fields += '\t\t<field id="{0}" />\n'.format(field)

        # Really cheesy way to build XML... this should probably be replaced at some point.
        xml = '''<report output="{0}">\n\t<title>{1}</title>\n\t<fields>\n{2}\t</fields>\n</report>'''.format(report_format, title, xml_fields)
        return xml

    def add_employee(self, employee):
        """
        API method for creating a new employee from a dictionary.
        http://www.bamboohr.com/api/documentation/employees.php#addEmployee

        @param employee: Dictionary containing employee information.
        @return: Dictionary contianing new employee URL and ID.
        """
        employee = camelcase_keys(employee)
        if not employee.get('firstName') or not employee.get('lastName'):
            raise UserWarning("The 'firstName' and 'lastName' keys are required.")

        xml = self._format_employee_xml(employee)
        url = self.base_url + 'employees/'
        r = requests.post(url, data=xml, headers=self.headers, auth=(self.api_key, ''))
        return {'url': r.headers['location'], 'id': r.headers['location'].replace(url, "")}

    def update_employee(self, id, employee):
        """
        API method for updating an existing employee from a dictionary.
        http://www.bamboohr.com/api/documentation/employees.php#updateEmployee

        @param id: String of containing the employee id you want to update.
        @param employee: Dictionary containing employee information.
        @return: Boolean of request success (Status Code == 200).
        """
        employee = camelcase_keys(employee)
        xml = self._format_employee_xml(employee)
        url = self.base_url + 'employees/{0}'.format(id)
        r = requests.post(url, data=xml, headers=self.headers, auth=(self.api_key, ''))
        return_value = r.status_code == 200
        return return_value

    def get_employee_directory(self):
        """
        API method for returning a globally shared company directory.
        http://www.bamboohr.com/api/documentation/employees.php#getEmployeeDirectory

        @return: A list of employee dictionaries which is a list of employees in the directory.
        """
        url = self.base_url + 'employees/directory'
        r = requests.get(url, headers=self.headers, auth=(self.api_key, ''))
        data = r.json()
        employees = data['employees']
        if self.underscore_keys:
            employees = [underscore_keys(employee) for employee in employees]

        return employees

    def get_employee(self, employee_id, field_list=None):
        """
        API method for returning a single employee based on employee id.
        http://www.bamboohr.com/api/documentation/employees.php#getEmployee

        @param employee_id: String of the employee id.
        @param field_list: List of fields to return with the employee dictionary.
        @return: A dictionary containing employee information from the specified field list.
        """
        get_fields = []

        field_list = [underscore_to_camelcase(field) for field in field_list] if field_list else None

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
        employee = r.json()

        if self.underscore_keys:
            employee = underscore_keys(employee)

        return employee

    def request_company_report(self, report_id, report_format='json', output_filename=None, filter_duplicates=True):
        """
        API method for returning a company report by report ID.
        http://www.bamboohr.com/api/documentation/employees.php#requestCompanyReport
        Success Response: 200
        The report will be generated in the requested format.
        The HTTP Content-type header will be set with the mime type for the response.

        @param report_id: String of the report id.
        @param report_format: String of the format to receive the report. (csv, pdf, xls, xml, json)
        @param output_filename: String (optional) if a filename/location is passed, the results will be saved to disk
        @param filter_duplicates: Boolean. True: apply standard duplicate field filtering (Default True)
        @return: A result in the format specified. (Will vary depending on format requested.)
        """
        if report_format not in self.report_formats:
            raise UserWarning("You requested an invalid report type. Valid values are: {0}".format(','.join([k for k in self.report_formats])))

        filter_duplicates = 'yes' if filter_duplicates else 'no'
        url = self.base_url + "reports/{0}?format={1}&fd={2}".format(report_id, report_format, filter_duplicates)
        r = requests.get(url, headers=self.headers, auth=(self.api_key, ''))

        if report_format == 'json':
            # return list/dict for json type
            result = r.json()
        elif report_format in ('csv', 'xml'):
            # return text for csv type
            result = r.text
        else:
            # return requests object for everything else after saving the file to the location specified.
            result = r

        if output_filename:
            with open(output_filename, 'wb') as handle:
                for block in r.iter_content(1024):
                    if not block:
                        break
                    handle.write(block)

        return result

    def request_custom_report(self, field_list, report_format='xls', title="My Custom Report", output_filename=None):
        """
        API method for returning a custom report by field list.
        http://www.bamboohr.com/api/documentation/employees.php#requestCustomReport
        Success Response: 200
        The report will be generated in the requested format.
        The HTTP Content-type header will be set with the mime type for the response.

        @param fields: List of report fields
        @param report_format: String of the format to receive the report. (csv, pdf, xls, xml)
        @param output_filename: String (optional) if a filename/location is passed, the results will be saved to disk
        @return: A result in the format specified. (Will vary depending on format requested.)
        """
        report_formats = self.report_formats
        report_formats.pop('json')

        if report_format not in report_formats:
            raise UserWarning("You requested an invalid report type. Valid values are: {0}".format(','.join([k for k in report_formats])))

        get_fields = []
        field_list = [underscore_to_camelcase(field) for field in field_list] if field_list else None
        if field_list:
            for f in field_list:
                if not self.employee_fields.get(f):
                    raise UserWarning("You passed in an invalid field")
                else:
                    get_fields.append(f)
        else:
            for field in self.employee_fields:
                get_fields.append(field)

        xml = self._format_report_xml(get_fields, title=title, report_format=report_format)
        url = self.base_url + "reports/custom/?format={0}".format(report_format)
        r = requests.post(url, data=xml, headers=self.headers, auth=(self.api_key, ''))


        if report_format in ('csv', 'xml'):
            # return text for csv type
            result = r.text
        else:
            # return requests object for everything else after saving the file to the location specified.
            result = r

        if output_filename:
            with open(output_filename, 'wb') as handle:
                for block in r.iter_content(1024):
                    if not block:
                        break
                    handle.write(block)

        return result
