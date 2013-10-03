PyBambooHR
========

This is an unofficial Python API for Bamboo HR. So far it is focusing on managing employee information but the plans are to have 100% API coverage eventually.

The library makes use of the requests library for Python and HTTPretty for testing. A huge thank you to both of those excellent projects.

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
