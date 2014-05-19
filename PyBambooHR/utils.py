"""
A collection of misc. utilities that are used in the main class.
"""

import datetime
import re
import xmltodict

def camelcase_keys(data):
    """
    Converts all the keys in a dict to camelcase. It works recursively to convert any nested dicts as well.
    @param data: The dict to convert
    """
    return_dict = {}
    for key in data:
        if isinstance(data[key], dict):
            return_dict[underscore_to_camelcase(key)] = camelcase_keys(data[key])
        else:
            return_dict[underscore_to_camelcase(key)] = data[key]

    return return_dict

def camelcase_to_underscore(name):
    """
    Converts a string to underscore. (Typically from camelcase.)
    @param name: The string to convert.
    """
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)).lower()

def underscore_to_camelcase(name):
    """
    Converts a string to camelcase. (Typically from underscore.)
    @param name: The string to convert.
    """
    return re.sub(r'_([a-z])', lambda m: (m.group(1).upper()), name)

def underscore_keys(data):
    """
    Converts all the keys in a dict to camelcase. It works recursively to convert any nested dicts as well.
    @param data: The dict to convert
    """
    return_dict = {}
    for key in data:
        if isinstance(data[key], dict):
            return_dict[camelcase_to_underscore(key)] = underscore_keys(data[key])
        else:
            return_dict[camelcase_to_underscore(key)] = data[key]

    return return_dict

_date_regex = re.compile(r"^\d{4}-\d{2}-\d{2}")

def resolve_date_argument(arg):
    if isinstance(arg, (datetime.datetime, datetime.date)):
        return arg.strftime('%Y-%m-%d')
    elif isinstance(arg, basestring) and _date_regex.match(arg):
        return arg
    elif arg is None:
        return None
    raise ValueError("Date argument {} must be either datetime, date, or string in form YYYY-MM-DD".format(arg))

def transform_tabular_data(xml_input):
    obj = _parse_xml(xml_input)
    rows = _extract(obj, 'table', 'row')
    by_employee_id = {}
    for row in rows:
        eid = row['@employeeId']
        fields = dict([ (f['@id'], f['#text']) for f in row['field'] ])
        by_employee_id.setdefault(eid, []).append(fields)
    return by_employee_id

def transform_whos_out(xml_input):
    obj = _parse_xml(xml_input)
    rows = _extract(obj, 'calendar', 'item')
    events = []
    for row in rows:
        ev = {
            'type': row['@type'],
            'start': row['start'],
            'end': row['end']
        }
        if ev['type'] == 'timeOff':
            ev['employeeId'] = row['employee']['@id']
            ev['employeeName'] = row['employee']['#text']
        events.append(ev)
    return events

def transform_change_list(xml_input):
    obj = _parse_xml(xml_input)
    rows = _extract(obj, 'changeList', 'employee')
    events = []
    for row in rows:
        events.append({
            'id': row['@id'],
            'action': row['@action'],
            'lastChanged': datetime.datetime.strptime(row['@lastChanged'], '%Y-%m-%dT%H:%M:%S+00:00')
        })
    return events

def _extract(xml_obj, first_key, second_key):
    rows = xml_obj.get(first_key, {}).get(second_key, [])
    return rows if isinstance(rows, list) else [ rows ]

def _parse_xml(input):
    return xmltodict.parse(input)
