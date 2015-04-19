# PyBambooHR

[![Build Status](https://secure.travis-ci.org/smeggingsmegger/PyBambooHR.png)](https://travis-ci.org/smeggingsmegger/PyBambooHR)&nbsp;&nbsp;&nbsp;![Download Stats](https://pypip.in/download/PyBambooHR/badge.svg)

This is an unofficial Python API for Bamboo HR. So far it is focusing on managing employee information but you can pretty much do anything you want with a little python.

The library makes use of the [requests](http://docs.python-requests.org/en/latest/) library for Python and [HTTPretty](https://github.com/gabrielfalcao/HTTPretty) for testing. A huge thank you to both of those excellent projects.

Using this library is very simple:

```python
from PyBambooHR import PyBambooHR

bamboo = PyBambooHR(subdomain='yoursub', api_key='yourapikeyhere')

employees = bamboo.get_employee_directory()
```

(Note that you have to enable sharing employee directory to use that method.)

This will give you a list of employees with properties on each including their ID.


```python
from PyBambooHR import PyBambooHR

bamboo = PyBambooHR(subdomain='yoursub', api_key='yourapikeyhere')

# Jim's employee ID is 123 and we are not specifying fields so this will get all of them.
jim = bamboo.get_employee(123)

# Pam's employee ID is 222 and we are specifying fields so this will get only the ones we request.
pam = bamboo.get_employee(222, ['city', 'workPhone', 'workEmail'])

```

Adding an employee

```python
from PyBambooHR import PyBambooHR

bamboo = PyBambooHR(subdomain='yoursub', api_key='yourapikeyhere')

# The firstName and lastName keys are required...
employee = {'firstName': 'Test', 'lastName': 'Person'}

result = bamboo.add_employee(employee)

The result dict will contain id and location. "id" is the numerical BambooHR employee ID. Location is a link to that employee.

```

Updating an employee

```python
from PyBambooHR import PyBambooHR

bamboo = PyBambooHR(subdomain='yoursub', api_key='yourapikeyhere')

# His name was test person...
employee = {'firstName': 'Another', 'lastName': 'Namenow'}

# Use the ID and then the dict with the new information
result = bamboo.update_employee(333, employee)

result will be True or False depending on if it succeeded.

```

Requesting a Report

```python
from PyBambooHR import PyBambooHR

bamboo = PyBambooHR(subdomain='yoursub', api_key='yourapikeyhere')

# Use the ID to request json information
result = bamboo.request_company_report(1, format='json', filter_duplicates=True)

# Now do stuff with your results (Will vary by report.)
for employee in result['employees']:
    print(employee)

# Use the ID and save a pdf:
result = bamboo.request_company_report(1, format='pdf', output_file='/tmp/report.pdf', filter_duplicates=True)

```
