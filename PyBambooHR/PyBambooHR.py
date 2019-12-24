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
from . import config
from .utils import make_field_xml
from os.path import basename

# Python 3 basestring compatibility:
try:
    unicode = unicode
except NameError:
    # unicode is undefined: We are running Python 3
    unicode = str

    # basestring is undefined: We are running Python 3
    try:
        basestring
    except NameError:
        basestring = str

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

    def __init__(self, subdomain='', api_key='', datatype='JSON', underscore_keys=False, timeout=60, **kwargs):
        """
        Using the subdomain, __init__ initializes the base_url for our API calls.
        This method also sets up some headers for our HTTP requests as well as our authentication (API key).

        @param api_key: String containing a valid API Key created in BambooHR.
        @param subdomain: String containing a valid company subdomain for a company in BambooHR.
        @param datatype: String of 'JSON' or 'XML'. Sets the Accept header for return type in our HTTP requests to BambooHR.
        """
        if not api_key:
            api_key = config.api_key

        if not subdomain:
            subdomain = config.subdomain

        # API Version
        self.api_version = 'v1'

        # Global headers
        self.headers = {}

        # Requests timeout
        self.timeout = timeout

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

        # Ask BambooHR for information that is scheduled in the future
        self.only_current = kwargs.get('only_current', False)

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

        # Whether or not to verify user fields. Defaults to False.
        self.verify_fields = kwargs.get('verify_fields', False)

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
            "preferredName": ("text", "The employee's preferred name."),
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
            "isPhotoUploaded": ("bool", "The employee has uploaded a photo"),
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
            "benefitClassDate": ("date", ""),
            "benefitClassClass": ("list", ""),
            "benefitClassChangeReason": ("list", ""),
        }

        # dicctionary with employees data
        self.employees = {}

    def _format_employee_xml(self, employee):
        """
        Utility method for turning an employee dictionary into valid employee xml.

        @param employee: Dictionary containing employee information.
        """
        xml_fields = ''
        for key in employee:
            if not self.employee_fields.get(key) and self.verify_fields:
                raise UserWarning("You passed in an invalid field")
            else:
                xml_fields += make_field_xml(key, employee[key], pre='\t', post='\n')

        # Really cheesy way to build XML... this should probably be replaced at some point.
        xml = "<employee>\n{}</employee>".format(xml_fields)
        return xml

    def _format_row_xml(self, row):
        """
        Utility method for turning an row dictionary into valid xml for
        entering or updating a row into the table

        @param employee: Dictionary containing row data information.
        """
        xml_fields = ''
        for k, v in row.iteritems():
            xml_fields += make_field_xml(k, v, pre='\t', post='\n')

        xml = "<row>\n{}</row>".format(xml_fields)
        return xml

    def _format_report_xml(
            self, fields, title='My Custom Report', report_format='pdf',
            last_changed=None):
        """
        Utility method for turning an employee dictionary into valid employee xml.

        @param fields: List containing report fields.
        """
        xml_fields = ''
        for field in fields:
            xml_fields += make_field_xml(field, None, pre='\t\t', post='\n')

        xml_filters = ''
        if last_changed and isinstance(last_changed, datetime.datetime):
            xml_filters = '''
                <filters>
                    <lastChanged includeNull="no">%s</lastChanged>
                </filters>
            ''' % last_changed.strftime('%Y-%m-%dT%H:%M:%SZ')

        # Really cheesy way to build XML... this should probably be replaced at some point.
        xml = '''<report output="{0}">\n\t<title>{1}</title>\n\t{2}<fields>\n{3}\t</fields>\n</report>'''.format(report_format, title, xml_filters, xml_fields)
        return xml

    def _format_time_off_xml(self, request_data):
        """
        Utility method for turning dictionary of time_off request data into valid xml.
        https://www.bamboohr.com/api/documentation/time_off.php#addRequest
        @param request_data: Dictionary containing incoming data for time off request
        """
        fields = ['status', 'start', 'end', 'timeOffTypeId', 'amount']
        xml = ''
        for f in fields:
            value = request_data.get(f)
            if value:
                xml += '\n\t<{0}>{1}</{0}>'.format(f, value)

        if request_data.get('notes') and len(request_data.get('notes')) > 0:
            notes = ''
            for n in request_data['notes']:
                f = n.get('type', 'employee')
                t = n.get('text', '')
                notes += '\n\t\t<note from="{0}">{1}</note>'.format(f, t)
            xml += '\n\t<notes>{0}\n\t</notes>'.format(notes)

        if request_data.get('dates') and len(request_data.get('dates')) > 0:
            dates = ''
            for d in request_data['dates']:
                dates += '\n\t\t<date ymd="{0}" amount="{1}" />'.format(d['ymd'], d['amount'])
            xml += '\n\t<dates>{0}\n\t</dates>'.format(dates)

        return '<request>{0}\n</request>'.format(xml)

    def add_employee(self, employee):
        """
        API method for creating a new employee from a dictionary.
        http://www.bamboohr.com/api/documentation/employees.php#addEmployee

        @param employee: Dictionary containing employee information.
        @return: Dictionary contianing new employee URL and ID.
        """
        employee = utils.camelcase_keys(employee)
        if not employee.get('firstName') or not employee.get('lastName'):
            raise UserWarning("The 'firstName' and 'lastName' keys are required.")

        xml = self._format_employee_xml(employee)
        url = self.base_url + 'employees/'
        r = requests.post(url, timeout=self.timeout, data=xml, headers=self.headers, auth=(self.api_key, ''))
        r.raise_for_status()

        return {'url': r.headers['location'], 'id': r.headers['location'].replace(url, "")}

    def update_employee(self, id, employee):
        """
        API method for updating an existing employee from a dictionary.
        http://www.bamboohr.com/api/documentation/employees.php#updateEmployee

        @param id: String of containing the employee id you want to update.
        @param employee: Dictionary containing employee information.
        @return: Boolean of request success (Status Code == 200).
        """
        employee = utils.camelcase_keys(employee)
        xml = self._format_employee_xml(employee)
        url = self.base_url + 'employees/{0}'.format(id)
        r = requests.post(url, timeout=self.timeout, data=xml, headers=self.headers, auth=(self.api_key, ''))
        r.raise_for_status()

        return True

    def get_employee_directory(self):
        """
        API method for returning a globally shared company directory.
        http://www.bamboohr.com/api/documentation/employees.php#getEmployeeDirectory

        @return: A list of employee dictionaries which is a list of employees in the directory.
        """
        url = self.base_url + 'employees/directory'
        r = requests.get(url, timeout=self.timeout, headers=self.headers, auth=(self.api_key, ''))
        r.raise_for_status()

        data = r.json()
        employees = data['employees']
        if self.underscore_keys:
            employees = [utils.underscore_keys(employee) for employee in employees]

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

        field_list = [utils.underscore_to_camelcase(field) for field in field_list] if field_list else None

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

        if self.only_current == False:
            payload.update({
                'onlyCurrent': 'false'
            })

        url = self.base_url + "employees/{0}".format(employee_id)
        r = requests.get(url, timeout=self.timeout, headers=self.headers, params=payload, auth=(self.api_key, ''))
        r.raise_for_status()

        employee = r.json()

        if self.underscore_keys:
            employee = utils.underscore_keys(employee)

        return employee

    def get_all_employees(self, field_list=None, disabledUsers=False, reloadEmployees=False):
        """
        API method for returning a dictionary of employees.

        @param allUsers: Boolean flag that indicates if get all employees.
        @param field_list: List of fields to return with the employee dictionary.
        @param reloadEmployees: Boolean flag that indicates if get all employees again.
        @return: Dictionary of dictionarys containing employees information.
        """
        if reloadEmployees or not self.employees:
            self.employees = {}

            users = {}
            # get all employees (doesn't get whom don't have activity)
            for u in self.get_meta_users().values():
                users[str(u['employeeId'])] = True if u['status']=='enabled' else False
            # get all enabled employees (included whom don't have activity, but are enabled)
            for u in self.get_employee_directory():
                users[u['id']] = True

            # filter enabled/active employees
            if not disabledUsers:
                users = {k:v for k,v in users.items() if v}

            # get employees data according to field_list
            for i,uKey in enumerate(users.keys()):
                if uKey not in self.employees.keys():
                    self.employees[uKey] = self.get_employee(uKey, field_list=field_list)

        return self.employees

    def get_employee_photo(self, employee_id, photo_size='small'):
        """
        API method to get photo data for an employee

        @param employee_id: String of the employee id.
        @param photo_size: String of the size of photo to fetch. Default is 'small'.
        @return A tuple whose first element is the photo data and second element
        is the content type header.
        """
        url = self.base_url + "employees/{0}/photo".format(employee_id)
        if photo_size:
            url = url + "/{}".format(photo_size)
        r = requests.get(url, timeout=self.timeout, headers=self.headers, auth=(self.api_key, ''))
        r.raise_for_status()

        return r.content, r.headers.get('content-type', '')

    def get_employee_files(self, employee_id):
        """
        API method to get files data for an employee

        @param employee_id: String of the employee id.
        @return A dictionary with data about the files of the employee
        """

        url = self.base_url + "employees/{0}/files/view/".format(employee_id)
        r = requests.get(url, timeout=self.timeout, headers=self.headers, auth=(self.api_key, ''))
        r.raise_for_status()
        data = utils.transform_table_data(r.content)

        return data['employee']

    def upload_employee_file(self, employee_id, file_path, category_id, share, override_file_name=None):
        """
        API method to upload a file for an employee

        @param employee_id: String of the employee id.
        @param file_path: String of the path of the file to upload
        @param category_id: The category id to upload the file to
        @param share: Boolean indicating if the file is shared with employee
        @param override_file_name: String to name the file uploaded, overriding the local file name
        """

        file_name = override_file_name if override_file_name else basename(file_path)

        with open(file_path, "rb") as f:
            params = {"file": f,
                      "fileName": (None, file_name),
                      "category": (None, str(category_id)),
                      "share": (None, "yes" if share else "no")}

            url = self.base_url + "employees/{0}/files/".format(employee_id)
            r = requests.post(url, timeout=self.timeout, headers=self.headers, auth=(self.api_key, ''), files=params)
            r.raise_for_status()
        return True

    def add_row(self, table_name, employee_id, row):
        """
        API method for adding a row to a table
        http://www.bamboohr.com/api/documentation/tables.php

        @param table_name: string of table's name
        @param employee_id: string of employee id
        @param row: dictionary containing row information
        """
        row = utils.camelcase_keys(row)
        xml = self._format_row_xml(row)
        url = self.base_url + \
            "employees/{0}/tables/{1}/".format(employee_id, table_name)
        r = requests.post(url, timeout=self.timeout, data=xml, headers=self.headers, auth=(self.api_key, ''))
        r.raise_for_status()

        return True

    def update_row(self, table_name, employee_id, row_id, row):
        """
        API method for updating a row in a table
        http://www.bamboohr.com/api/documentation/tables.php

        @param table_name: string of table's name
        @param employee_id: string of employee id
        @param row_id: string of id of row in table to update
        @param row: dicionary containing row information
        """
        row = utils.camelcase_keys(row)
        xml = self._format_row_xml(row)
        url = self.base_url + \
            "employees/{0}/tables/{1}/{2}/".format(employee_id, table_name, row_id)
        r = requests.post(url, timeout=self.timeout, data=xml, headers=self.headers, auth=(self.api_key, ''))
        r.raise_for_status()

        return True

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
        url = self.base_url + "reports/{0}?format={1}&fd={2}&onlyCurrent={3}".format(report_id, report_format, filter_duplicates, self.only_current)
        r = requests.get(url, timeout=self.timeout, headers=self.headers, auth=(self.api_key, ''))
        r.raise_for_status()

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

    def request_custom_report(
            self, field_list, report_format='xls', title="My Custom Report",
            output_filename=None, last_changed=None):
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
        if report_format not in self.report_formats:
            raise UserWarning("You requested an invalid report type. Valid values are: {0}".format(','.join([k for k in self.report_formats])))

        get_fields = []
        field_list = [utils.underscore_to_camelcase(field) for field in field_list] if field_list else None
        if field_list:
            for f in field_list:
                if not f.startswith('custom') and not self.employee_fields.get(f):
                    raise UserWarning("You passed in an invalid field")
                else:
                    get_fields.append(f)
        else:
            for field in self.employee_fields:
                get_fields.append(field)

        xml = self._format_report_xml(
            get_fields, title=title, report_format=report_format,
            last_changed=last_changed)
        url = self.base_url + "reports/custom/?format={0}".format(report_format)
        r = requests.post(url, timeout=self.timeout, data=xml, headers=self.headers, auth=(self.api_key, ''))
        r.raise_for_status()

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

    def get_tabular_data(self, table_name, employee_id='all'):
        """
        API method to retrieve tabular data for an employee, or all employees if employee_id argument is 'all' (the default).
        See http://www.bamboohr.com/api/documentation/tables.php for a list of available tables.

        @return A dictionary with employee ID as key and a list of dictionaries, each dictionary showing
        the values of the table's fields for a particular date, which is stored by key 'date' in the dictionary.
        """
        url = self.base_url + 'employees/{}/tables/{}'.format(employee_id, table_name)
        r = requests.get(url, timeout=self.timeout, headers=self.headers, auth=(self.api_key, ''))
        r.raise_for_status()

        return utils.transform_tabular_data(r.content)

    def get_employee_changed_table(self, table_name='jobInfo', since=None):
        """
        API method to retrieve tabular data for changed employee.
        See http://www.bamboohr.com/api/documentation/tables.php for a list of available tables.

        @return A dictionary with employee ID as key and a list of dictionaries, each dictionary showing
        the values of the table's fields for a particular date, which is stored by key 'date' in the dictionary.
        """
        if not isinstance(since, datetime.datetime):
            raise ValueError("Error: since argument must be a datetime.datetime instance")

        url = 'employees/changed/tables/{}'.format(table_name)
        params = {'since': since.strftime('%Y-%m-%dT%H:%M:%SZ')}
        return self._query(url, params)

    def get_employee_changes(self, since=None, _type=None):
        """
        Returns a list of dictionaries, each with id, action, and lastChanged keys, representing
        the employee records that have changed since the datetime object passed in the since= argument.

        @return List of dictionaries, each with id, action, and lastChanged keys.
        """
        if not isinstance(since, datetime.datetime):
            raise ValueError("Error: since argument must be a datetime.datetime instance")

        url = self.base_url + 'employees/changed/'
        params = {'since': since.strftime('%Y-%m-%dT%H:%M:%SZ')}
        if _type:
            params.update({'type': _type})

        r = requests.get(url, timeout=self.timeout, params=params, headers=self.headers, auth=(self.api_key, ''))
        r.raise_for_status()

        return r.json()

    def get_whos_out(self, start_date=None, end_date=None):
        start_date = utils.resolve_date_argument(start_date)
        end_date = utils.resolve_date_argument(end_date)

        url = self.base_url + 'time_off/whos_out'
        params = {}
        if start_date:
            params['start'] = start_date
        if end_date:
            params['end'] = end_date
        r = requests.get(url, timeout=self.timeout, params=params, headers=self.headers, auth=(self.api_key, ''))
        r.raise_for_status()
        return r.json()
        # return utils.transform_whos_out(r.content)

    def get_time_off_requests(self, start_date=None, end_date=None, status=None, type=None, employee_id=None):
        start_date = utils.resolve_date_argument(start_date)
        end_date = utils.resolve_date_argument(end_date)

        params = {}
        # Must set dates or request errors 400 Bad Request
        params['start']= start_date if start_date else '0000-01-01'
        params['end']= end_date if end_date else '9999-01-01'
        if type:
            params['type'] = type
        if employee_id:
            params['employeeId'] = employee_id

        r = self._query('time_off/requests', params, raw=True)
        return r.json()

    def get_time_off_policies(self):
        """
        Api method for returning list of time off policies for a subdomain
        https://www.bamboohr.com/api/documentation/time_off.php#getTimeOffPolicies
        Success Response: 200
        @return: List containing time off policies
        """
        url = 'meta/time_off/policies'
        r = self._query(url, {})
        return r

    def get_time_off_types(self):
        """
        Api method for returning list of time off types for a subdomain
        https://www.bamboohr.com/api/documentation/time_off.php#getTimeOffTypes
        Success Response: 200
        @return: List containing time off types
        """
        url = 'meta/time_off/types'
        r = self._query(url, {})
        return r['timeOffTypes']

    def create_time_off_request(self, data, raw=False):
        """
        API method for creating a new time off request
        https://www.bamboohr.com/api/documentation/time_off.php#addRequest
        Success Response: 201
        @return: A dictionary containing the created time off request
        """
        data['status'] = 'requested'
        return self.update_time_off_request(data, raw)

    def update_time_off_request(self, data, raw=False):
        """
        API method for creating or updating a new time off request
        https://www.bamboohr.com/api/documentation/time_off.php#addRequest
        @param data = {
            'status': 'requested',
            'employee_id': '113',
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
        Success Response: 201
        @return: A dictionary containing the created/updated time off request
        """
        url = self.base_url + 'employees/{0}/time_off/request'.format(data.get('employee_id'))
        xml = self._format_time_off_xml(data)
        r = requests.put(url, timeout=self.timeout, headers=self.headers, auth=(self.api_key, ''), data=xml)
        r.raise_for_status()
        if raw:
            return r
        else:
            return r.json()

    def update_time_off_request_status(self, request_id, data, raw=False):
        """
        https://www.bamboohr.com/api/documentation/time_off.php#changeRequest
        Success Response: 200
        @param data = d = {
            'status': 'denied',
            'note': 'have fun!'
        }
        @return: Boolean of request success (Status Code == 200).
        """
        url = self.base_url + 'time_off/requests/{0}/status'.format(request_id)
        r = requests.put(url, timeout=self.timeout, headers=self.headers, auth=(self.api_key, ''), json=data)
        r.raise_for_status()
        return True

    def get_meta_fields(self):
        """
        API method for returning a list of fields info.
        https://www.bamboohr.com/api/documentation/metadata.php#getFields
        Success Response: 200
        The HTTP Content-type header will be set with the mime type for the response.

        @return: list containing fields information
        """
        url = self.base_url + "meta/fields/"
        r = requests.get(url, timeout=self.timeout, headers=self.headers, auth=(self.api_key, ''))
        r.raise_for_status()

        return r.json()

    def get_meta_tables(self):
        """
        API method for returning a list of tables info.
        https://www.bamboohr.com/api/documentation/metadata.php#getTables
        Success Response: 200
        The HTTP Content-type header will be set with the mime type for the response.

        @return: list containing tables information
        """

        url = self.base_url + "meta/tables/"
        r = requests.get(url, timeout=self.timeout, auth=(self.api_key, ''))
        r.raise_for_status()
        data = utils.transform_table_data(r.content)
        self.meta_tables = data['tables']['table']

        return self.meta_tables

    def get_meta_lists(self):
        """
        API method for returning a list with lists fields info.
        https://www.bamboohr.com/api/documentation/metadata.php#getLists
        Success Response: 200
        The HTTP Content-type header will be set with the mime type for the response.

        @return: list containing lists fields information
        """

        url = self.base_url + "meta/lists/"
        r = requests.get(url, timeout=self.timeout, headers=self.headers, auth=(self.api_key, ''))
        r.raise_for_status()

        return r.json()

    def get_meta_users(self):
        """
        API method for returning a dictionary of users info.
        https://www.bamboohr.com/api/documentation/metadata.php#getUsers
        Success Response: 200
        The HTTP Content-type header will be set with the mime type for the response.

        @return: dictionary containing users information
        """

        url = self.base_url + "meta/users/"
        r = requests.get(url, timeout=self.timeout, headers=self.headers, auth=(self.api_key, ''))
        r.raise_for_status()

        return r.json()

    def _query(self, url, params, raw=False):
        url = self.base_url + url
        r = requests.get(url, timeout=self.timeout, params=params, headers=self.headers, auth=(self.api_key, ''))
        r.raise_for_status()
        if raw:
            return r
        else:
            return r.json()
