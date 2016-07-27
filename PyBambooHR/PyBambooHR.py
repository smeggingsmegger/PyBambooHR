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

import datetime
import requests
from . import utils
from .utils import make_field_xml
from os.path import basename

# Python 3 basestring compatibility:
try:
    unicode = unicode
except NameError:
    # unicode is undefined: We are running Python 3
    unicode = str
    basestring = (str, bytes)
else:
    # unicode is defined: We are running Python 2
    bytes = str


class PyBambooHR(object):
    """
    The PyBambooHR class is initialized with an API key, company subdomain,
    and an optional datatype argument (defaults to JSON). This class implements
    methods for basic CRUD operations for employees and more.
    """
    def __init__(self, subdomain='', api_key='', datatype='JSON',
                 underscore_keys=False):
        """PyBambooHR __init__

        Using the subdomain, __init__ initializes the base_url for our API
        calls.  This method also sets up some headers for our HTTP requests
        as well as our authentication (API key).

        @param api_key: String containing a valid API Key created in BambooHR.
        @param subdomain: String containing a valid company subdomain for a
        company in BambooHR.
        @param datatype: String 'JSON' or 'XML'. Sets the Accept header for
        return type in our HTTP requests to BambooHR.
        """
        if not api_key:
            raise ValueError('The `api_key` argument can not be empty. Please'
                             'provide a valid BambooHR API key.')

        if not subdomain:
            raise ValueError('The `subdomain` argument can not be empty. Please'
                             'provide a valid BambooHR company subdomain.')

        # API Version
        self.api_version = 'v1'

        # Global headers
        self.headers = {}

        # Referred to in the documentation as [ Company ] sometimes.
        self.subdomain = subdomain

        # All requests will start with this url
        self.base_url = (
            'https://api.bamboohr.com/api/gateway.php/{0}/{1}/'.format(
                self.subdomain, self.api_version))

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

        # These can be used as a reference for available fields, also used to
        # validate fields in get_employee and to grab all available data if
        # no fields are passed in the same function.
        self.employee_fields = {
            "address1": ("text", "The employee's first address line"),
            "address2": ("text", "The employee's second address line"),
            "age": ("integer", "The employee's age. Not editable. To change"
                               " update dateOfBirth, instead."),
            "bestEmail": ("email", "The employee's work email if set,"
                                   " otherwise their home email"),
            "birthday": ("text", "The employee's month and day of birth. Not"
                                 " editable. To change update dateOfBirth,"
                                 " instead."),
            "city": ("text", "The employee's city"),
            "country": ("country", "The employee's country"),
            "dateOfBirth": ("date", "The date the employee was born"),
            "department": ("list", "The employee's CURRENT department."),
            "division": ("list", "The employee's CURRENT division"),
            "eeo": ("list", "The employee's EEO job category. These are"
                            " defined by the U.S. Equal Employment"
                            " Opportunity Commission"),
            "employeeNumber": ("text", "Employee number (assigned by your"
                                       " company)"),
            "employmentStatus": ("status", "DEPRECATED. Please use 'status'"
                                           " instead. The employee's employee"
                                           " status (Active,Inactive)"),
            "employmentHistoryStatus": ("list", "The employee's CURRENT"
                                                " employment status. Options"
                                                " are customized by account."),
            "ethnicity": ("list", "The employee's ethnicity"),
            "exempt": ("list", "The FLSA employee exemption code (Exempt or"
                                " Non-exempt)"),
            "firstName": ("text", "The employee's first name"),
            "flsaCode": ("list", "The employee's FLSA code. Ie: 'Exempt',"
                                 " 'Non-excempt'"),
            "fullName1": ("text", "Employee's first and last name. Example:"
                                  " John Doe. Ready only."),
            "fullName2": ("text", "Employee's last and first name. Example:"
                                  " Doe, John. Read only."),
            "fullName3": ("text", "Employee's full name with nickname."
                                  " Example: Doe, John Quentin (JDog)."
                                  " Read only."),
            "fullName4": ("text", "Employee's full name without nickname."
                                  " Last name first. Example: Doe, John"
                                  " Quentin. Read only"),
            "fullName5": ("text", "Employee's full name without nickname."
                                  " First name first. Example: John Quentin"
                                  " Doe. Read only"),
            "displayName": ("text", "Employee's name displayed in a format"
                                    " configured by the user. Read only"),
            "gender": ("gender", "The employee's gender. Legal values are"
                                 "'Male', 'Female'"),
            "hireDate": ("date", "The date the employee was hired"),
            "homeEmail": ("email", "The employee's home email address"),
            "homePhone": ("phone", "The employee's home phone number"),
            "id": ("integer", "Employee id (automatically assigned by"
                              " BambooHR). Not editable."),
            "jobTitle": ("list", "The CURRENT value of the employee's job"
                                 " title, updating this field will create"
                                 " a new row in position history"),
            "lastChanged": ("timestamp", "The date and time that the employee"
                                         " record was last changed"),
            "lastName": ("text", "The employee's last name"),
            "location": ("list", "The employee's CURRENT location"),
            "maritalStatus": ("list", "The employee's marital status"
                                      " ('Single' or 'Married')"),
            "middleName": ("text", "The employee's middle name"),
            "mobilePhone": ("phone", "The employee's mobile phone number"),
            "nickname": ("text", "The employee's nickname"),
            "payChangeReason": ("list", "The reason for the employee's last"
                                        " pay rate change."),
            "payGroup": ("list", "The custom pay group to which the employee"
                                 " belongs."),
            "payGroupId": ("integer", "The id value corresponding to the"
                                      " pay group to which the employee"
                                      " belongs"),
            "payRate": ("currency", "The employee's CURRENT pay rate,"
                                    " e.g. $8.25"),
            "payRateEffectiveDate": ("date", "The date most recent pay change"
                                             " was made."),
            "payType": ("pay_type", "The employee's CURRENT pay type,"
                                    " e.g. 'hourly','salary','commission',"
                                    "'exception hourly','monthly',"
                                    "'piece rate','contract','daily'"),
            "ssn": ("ssn", "The employee's social security number"),
            "sin": ("sin", "The employee's Canadian Social Insurance Number"),
            "state": ("state", "The employee's state/province"),
            "stateCode": ("text", "The 2 character abbreviation for the"
                                  " employee's state (US only). Not editable."),
            "status": ("status", "Indicates whether you are using BambooHR"
                                 " to track data about this employee."
                                 " Valid values are 'Active', 'Inactive'."),
            "supervisor": ("employee", "The employee's CURRENT supervisor."
                                       " Not editable."),
            "supervisorId": ("integer", "The 'employeeNumber' of the"
                                        " employee's CURRENT supervisor."
                                        " Not editable."),
            "supervisorEId": ("integer", "The 'id' of the employee's CURRENT"
                                         " supervisor. Not editable."),
            "terminationDate": ("date", "The date the employee was terminated"),
            "workEmail": ("email", "The employee's work email address"),
            "workPhone": ("phone", "The employee's work phone number,"
                                   " without extension"),
            "workPhonePlusExtension": ("text", "The employee's work phone and"
                                               " extension. Not editable."),
            "workPhoneExtension": ("text", "The employees work phone extension"
                                           " (if any)"),
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
        """Turn an employee dictionary into valid employee xml.

        @param employee: Dictionary containing employee information.
        """
        xml_fields = ''
        for key in employee:
            if not self.employee_fields.get(key):
                raise UserWarning("You passed in an invalid field")
            else:
                xml_fields += make_field_xml(key, employee[key],
                                             pre='\t', post='\n')

        # Really cheesy way to build XML... this should probably be replaced
        # at some point.
        xml = "<employee>\n{}</employee>".format(xml_fields)
        return xml

    def _format_row_xml(self, row):
        """Turn a row dictionary into valid xml.

        Utility function for entering or updating a row into the table

        @param employee: Dictionary containing row data information.
        """
        xml_fields = ''
        for k, v in row.iteritems():
            xml_fields += make_field_xml(k, v, pre='\t', post='\n')

        xml = "<row>\n{}</row>".format(xml_fields)
        return xml

    def _format_report_xml(self, fields, title='My Custom Report',
                           report_format='pdf'):
        """Turn an employee dictionary into valid employee xml.

        @param fields: List containing report fields.
        """
        xml_fields = ''
        for field in fields:
            xml_fields += make_field_xml(field, None, pre='\t\t', post='\n')

        # Really cheesy way to build XML... this should probably be replaced
        # at some point.
        xml = ('<report output="{0}">\n\t<title>{1}</title>\n\t'
               '<fields>\n{2}\t</fields>\n</report>'.format(report_format,
                   title, xml_fields))
        return xml

    def add_employee(self, employee):
        """Create new employee from a dictionary.

        API method documentation at
        http://www.bamboohr.com/api/documentation/employees.php#addEmployee

        @param employee: Dictionary containing employee information.
        @return: Dictionary containing new employee URL and ID.
        """
        employee = utils.camelcase_keys(employee)
        if not employee.get('firstName') or not employee.get('lastName'):
            raise UserWarning(
                "The 'firstName' and 'lastName' keys are required.")

        xml = self._format_employee_xml(employee)
        url = self.base_url + 'employees/'
        r = requests.post(url, data=xml, headers=self.headers,
                          auth=(self.api_key, ''))
        r.raise_for_status()

        return {'url': r.headers['location'],
                'id': r.headers['location'].replace(url, "")}

    def update_employee(self, id, employee):
        """Update an exiisting employee from a dictionary.

        API method documentation
        http://www.bamboohr.com/api/documentation/employees.php#updateEmployee

        @param id: String containing the employee id you want to update.
        @param employee: Dictionary containing employee information.
        @return: Boolean representing request success (i.e. Status Code == 200).
        """
        employee = utils.camelcase_keys(employee)
        xml = self._format_employee_xml(employee)
        url = self.base_url + 'employees/{0}'.format(id)
        r = requests.post(url, data=xml, headers=self.headers,
                          auth=(self.api_key, ''))
        r.raise_for_status()

        return True

    def get_employee_directory(self):
        """Returns globally shared company directory.

        API method documentation at
        http://www.bamboohr.com/api/documentation/employees.php#getEmployeeDirectory

        @return: A list of employee dictionaries which is a list of employees
        in the directory.
        """
        url = self.base_url + 'employees/directory'
        r = requests.get(url, headers=self.headers, auth=(self.api_key, ''))
        r.raise_for_status()

        data = r.json()
        employees = data['employees']
        if self.underscore_keys:
            employees = [utils.underscore_keys(employee) for employee in employees]

        return employees

    def get_employee(self, employee_id, field_list=None):
        """Return a single employee, based on employee id

        API method documentation at
        http://www.bamboohr.com/api/documentation/employees.php#getEmployee

        @param employee_id: String of the employee id.
        @param field_list: List of fields to return with the employee
        dictionary.
        @return: A dictionary containing employee information from the
        specified field list.
        """
        get_fields = []

        field_list = [utils.underscore_to_camelcase(field)
                      for field in field_list] if field_list else None

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
        r = requests.get(url, headers=self.headers, params=payload,
                         auth=(self.api_key, ''))
        r.raise_for_status()

        employee = r.json()

        if self.underscore_keys:
            employee = utils.underscore_keys(employee)

        return employee

    def get_employee_photo(self, employee_id, photo_size='small'):
        """Get employee photo data.

        @param employee_id: String of the employee id.
        @param photo_size: String of the size of photo to fetch. Default 'small'
        @return A tuple whose first element is the photo data and second element
        is the content type header.
        """
        url = self.base_url + "employees/{0}/photo".format(employee_id)
        if photo_size:
            url = url + "/{}".format(photo_size)
        r = requests.get(url, headers=self.headers, auth=(self.api_key, ''))
        r.raise_for_status()

        return r.content, r.headers.get('content-type', '')

    def upload_employee_file(self, employee_id, file_path, category_id, share,
                             override_file_name=None):
        """Upload a file for an employee.

        @param employee_id: String, the employee id
        @param file_path: String, the path of the file to upload
        @param category_id: String, the category id to which we upload the file
        @param share: Boolean indicating if the file is shared with employee
        @param override_file_name: String, name of the file once uploaded,
        overrides the local file name
        """

        file_name = (override_file_name if override_file_name 
                     else basename(file_path))

        with open(file_path, "rb") as f:
            params = {"file": f,
                      "fileName": (None, file_name),
                      "category": (None, str(category_id)),
                      "share": (None, "yes" if share else "no")}

            url = self.base_url + "employees/{0}/files/".format(employee_id)
            r = requests.post(url, headers=self.headers,
                              auth=(self.api_key, ''), files=params)
            r.raise_for_status()
        return True

    def add_row(self, table_name, employee_id, row):
        """Add row to a BambooHR table

        API method documentation at 
        http://www.bamboohr.com/api/documentation/tables.php

        @param table_name: String, table's name
        @param employee_id: String, employee id
        @param row: Dictionary containing row information
        """
        row = utils.camelcase_keys(row)
        xml = self._format_row_xml(row)
        url = self.base_url + \
            "employees/{0}/tables/{1}/".format(employee_id, table_name)
        r = requests.post(url, data=xml, headers=self.headers,
                          auth=(self.api_key, ''))
        r.raise_for_status()

        return True

    def update_row(self, table_name, employee_id, row_id, row):
        """Update a BambooHR table row

        API method documentation at
        http://www.bamboohr.com/api/documentation/tables.php

        @param table_name: String of table's name
        @param employee_id: String of employee id
        @param row_id: String of id of row in table to update
        @param row: Dicionary containing row information
        """
        row = utils.camelcase_keys(row)
        xml = self._format_row_xml(row)
        url = (self.base_url + 
               "employees/{0}/tables/{1}/{2}/".format(employee_id,
                   table_name, row_id))
        r = requests.post(url, data=xml, headers=self.headers,
                          auth=(self.api_key, ''))
        r.raise_for_status()

        return True

    def request_company_report(self, report_id, report_format='json',
                               output_filename=None, filter_duplicates=True):
        """Return company report by report id

        API method documentation at 
        http://www.bamboohr.com/api/documentation/employees.php#requestCompanyReport

        Success Response: 200
        The report will be generated in the requested format.
        The HTTP Content-type header will be set with the mime type for
        the response.

        @param report_id: String, the report id.
        @param report_format: String, the format to receive the report.
            Possible values: csv, pdf, xls, xml, json
        @param output_filename: Optional String, name of local file where
            results will be written
        @param filter_duplicates: Boolean (default true), if we should
            apply standard duplicate field filtering
        @return: A result in the format specified. (Will vary depending
            on format requested.)
        """
        if report_format not in self.report_formats:
            raise UserWarning("You requested an invalid report type."
                "Valid values are: {0}".format(','.join(
                    [k for k in self.report_formats])))

        filter_duplicates = 'yes' if filter_duplicates else 'no'
        url = self.base_url + "reports/{0}?format={1}&fd={2}".format(
            report_id, report_format, filter_duplicates)
        r = requests.get(url, headers=self.headers, auth=(self.api_key, ''))
        r.raise_for_status()

        if report_format == 'json':
            # return list/dict for json type
            result = r.json()
        elif report_format in ('csv', 'xml'):
            # return text for csv type
            result = r.text
        else:
            # return requests object for everything else after
            # saving the file to the location specified.
            result = r

        if output_filename:
            with open(output_filename, 'wb') as handle:
                for block in r.iter_content(1024):
                    if not block:
                        break
                    handle.write(block)

        return result

    def request_custom_report(self, field_list, report_format='xls',
                              title="My Custom Report", output_filename=None):
        """Return a custom report by field list

        API method documentation at
        http://www.bamboohr.com/api/documentation/employees.php#requestCustomReport

        Success Response: 200
        The report will be generated in the requested format.
        The HTTP Content-type header will be set with the mime type for the
        response.

        @param fields: List of report fields
        @param report_format: String, the format to receive the report.
        Possible values: csv, pdf, xls, xml, json
        @param output_filename: Optional String, name of local file where
        results will be written
        """
        if report_format not in self.report_formats:
            raise UserWarning("You requested an invalid report type."
                "Valid values are: {0}".format(','.join(
                    [k for k in self.report_formats])))

        get_fields = []
        field_list = [utils.underscore_to_camelcase(field)
                      for field in field_list] if field_list else None
        if field_list:
            for f in field_list:
                if not self.employee_fields.get(f):
                    raise UserWarning("You passed in an invalid field")
                else:
                    get_fields.append(f)
        else:
            for field in self.employee_fields:
                get_fields.append(field)

        xml = self._format_report_xml(get_fields, title=title,
                                      report_format=report_format)
        url = self.base_url + "reports/custom/?format={0}".format(report_format)
        r = requests.post(url, data=xml, headers=self.headers,
                          auth=(self.api_key, ''))
        r.raise_for_status()

        if report_format == 'json':
            # return list/dict for json type
            result = r.json()
        elif report_format in ('csv', 'xml'):
            # return text for csv type
            result = r.text
        else:
            # return requests object for everything else after saving the
            # file to the location specified.
            result = r

        if output_filename:
            with open(output_filename, 'wb') as handle:
                for block in r.iter_content(1024):
                    if not block:
                        break
                    handle.write(block)

        return result

    def get_tabular_data(self, table_name, employee_id='all'):
        """Retrieve tabular data for one or all employees

        employee_id argument is 'all' (the default).
        API method documentation at
        See http://www.bamboohr.com/api/documentation/tables.php for a list of available tables.

        @param employee_id: Integer (string or numeric), the employee
            id who's tabular data you wish to retrieve. If set to 'all' (default)
            it will retrieve for all employees.
        @return A dictionary with employee ID as key and a list of
            dictionaries, each dictionary showing the values of the table's
            fields for a particular date, which is stored by key 'date'
            in the dictionary.
        """
        url = self.base_url + 'employees/{}/tables/{}'.format(employee_id,
                                                              table_name)
        r = requests.get(url, headers=self.headers, auth=(self.api_key, ''))
        r.raise_for_status()

        return utils.transform_tabular_data(r.content)

    def get_employee_changes(self, since=None):
        """Return a list of employee changes.


        Returns a list of dictionaries, each with id, action,
        and lastChanged keys, representing the employee records
        that have changed since the datetime object passed in
        the since parameter.

        @param since: Datetime, the starting time for the results

        @return List of dictionaries, each with id, action, and lastChanged
            keys.
        """
        if not isinstance(since, datetime.datetime):
            raise ValueError("Error: since argument must be a"
                             "datetime.datetime instance")

        url = self.base_url + 'employees/changed/'
        params = {'since': since.strftime('%Y-%m-%dT%H:%M:%SZ')}
        r = requests.get(url, params=params, headers=self.headers,
                         auth=(self.api_key, ''))
        r.raise_for_status()

        return utils.transform_change_list(r.content)

    def get_whos_out(self, start_date=None, end_date=None):
        """Return which employees are out, including Holidays

        @param start_date: Datetime, the start date for our results.
        @param end_date: Datetime, the end date for our results.
        @return: A list of employees who or out during the time interval.
        """
        start_date = utils.resolve_date_argument(start_date)
        end_date = utils.resolve_date_argument(end_date)

        url = self.base_url + 'time_off/whos_out'
        params = {}
        if start_date:
            params['start'] = start_date
        if end_date:
            params['end'] = end_date
        r = requests.get(url, params=params, headers=self.headers,
                         auth=(self.api_key, ''))
        r.raise_for_status()
        return r.json()
        # return utils.transform_whos_out(r.content)

    def get_time_off_requests(self, start_date=None, end_date=None,
                              status=None, type=None, employee_id=None):
        """Return time off requests for an employee

        API documentation at
        http://www.bamboohr.com/api/documentation/time_off.php

        @param employee_id: Optional String or Integer, the employee id to
            which we limit results
        @param start_date: Optional Datetime, the start date for our results
        @param end_date: Optional Datetime, the end date for our results
        @param type: Optional String, comma separated list of types IDs
            to which we limit the results
        @param status: Optional String, comma separated list of statuses to
            which we limit the result. Allowed values are "approved",
            "denied", "superceded", "requested", "canceled"
        @return: List of time off requests
        """
        start_date = utils.resolve_date_argument(start_date)
        end_date = utils.resolve_date_argument(end_date)

        params = {}
        if start_date:
            params['start'] = start_date
        if end_date:
            params['end'] = end_date
        if status:
            params['status'] = status
        if type:
            params['type'] = type
        if employee_id:
            params['employeeId'] = employee_id

        r = self._query('time_off/requests', params, raw=True)
        return r.json()
        # return utils.transform_time_off(r.content)

    def _query(self, api_path, params, raw=False):
        """Query BambooHR API

        Runs
        @param url: String, the api path component of the URL,
            e.g. /time_off/requests
        @param params: Dictionary, the paramaters for the API call
        @param raw: Boolean (default False), if the results should
            be left in raw form or converted from JSON to a dictionary
        @return: results from API call
        @raises: Exception on non 200 response, or failure to convert
            result from JSON when requested
        """
        url = self.base_url + api_path
        r = requests.get(url, params=params, headers=self.headers,
                         auth=(self.api_key, ''))
        r.raise_for_status()
        if raw:
            return r
        else:
            return r.json()
