"""
A collection of misc. utilities that are used in the main class.
"""

import datetime
import re
import xmltodict
import json

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


def make_field_xml(id, value=None, pre='', post=''):
    id = escape(str(id))
    if value:
        value = escape(str(value))
        tag = '<field id="{}">{}</field>'.format(id, value)
    else:
        tag = '<field id="{}" />'.format(id)
    return '{0}{1}{2}'.format(pre, tag, post)


def resolve_date_argument(arg):
    # basestring is undefined: We are running Python 3
    try:
        basestring
    except NameError:
        basestring = str

    if isinstance(arg, (datetime.datetime, datetime.date)):
        return arg.strftime('%Y-%m-%d')
    elif isinstance(arg, basestring) and _date_regex.match(arg):
        return arg
    elif arg is None:
        return None
    raise ValueError("Date argument {} must be either datetime, date, or string in form YYYY-MM-DD".format(arg))

def transform_tabular_data(xml_input):
    """
    Converts table data (xml) from BambooHR into a dictionary with employee
    id as key and a list of dictionaries.
    Each field is a dict with the id as the key and inner text as the value
    e.g.
        <table>
          <row id="321" employeeId="123">
            <field id="customFieldA">123 Value A</field>
            <field id="customFieldC"></field>
          </row>
          <row id="999" employeeId="321">
            <field id="customFieldB">321 Value B</field>
          </row>
        </table>
    becomes
        {'123': [{
                 'customFieldA': '123 Value A',
                 'customFieldB': '123 Value B',
                 'row_id': '321'}],
         '321': [{
                 'customFieldA': '321 Value A',
                 'row_id': '999'}]}
    """
    obj = _parse_xml(xml_input)
    rows = _extract(obj, 'table', 'row')
    by_employee_id = {}
    for row in rows:
        eid = row['@employeeId']
        field_list = row['field'] if type(row['field']) is list \
            else [row['field']]
        fields = dict([(f['@id'], f.get('#text', None)) for f in field_list])
        fields['row_id'] = row['@id']
        by_employee_id.setdefault(eid, []).append(fields)
    return by_employee_id

def transform_table_data(xml_input):
    """
    Converts table data (xml) from BambooHR into a dictionary or list
    Each field is a dict with the id as the key and inner text as the value
    e.g.
    <tables>
         <table alias="customTable1">
          <field id="5908" alias="custom1" type="date">Date</field>
          <field id="5909" alias="custom2" type="currency">Amount</field>
         </table>
         <table alias="customTable2">
          <field id="5900" alias="custom3" type="list">Type</field>
         </table>
    </tables>
    becomes
        {"tables":{"table":[{
            u'alias': u'customTable1',
            u'field': [
                {
                    u'alias': u'custom1',
                    u'id': u'5908',
                    u'text': u'Date',
                    u'type': u'date'
                },
                {
                    u'alias': u'custom2',
                    u'id': u'5909',
                    u'text': u'Amount',
                    u'type': u'currency'
                }]
            },{
            u'alias': u'customTable2',
            u'field': [
                {
                    u'alias': u'custom3',
                    u'id': u'5900',
                    u'text': u'Type',
                    u'type': u'list'
                }
            ]}
        ]}}
    """
    obj = _parse_xml(xml_input)
    d = json.loads(json.dumps(obj))
    d = change_keys(d)
    return d

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

def transform_time_off(xml_input):
    obj = _parse_xml(xml_input)
    rows = _extract(obj, 'requests', 'request')
    requests = []
    for row in rows:
        # Sample XML
        # <employee id="1">Jon Doe</employee>
        # <status lastChanged="2011-08-14" lastChangedByUserId="1">approved</status>
        # <start>2001-01-01</start>
        # <end>2001-01-06</end>
        # <created>2011-08-13</created>
        # <type id="1">Vacation</type>
        # <amount unit="days">5</amount>
        rq = {
            'employeeId': row['employee']['@id'],
            'employeeName': row['employee']['#text'],
            'status': row['status']['#text'],
            'type': row['type']['#text'],
            'amount': row['amount']['#text'],
            'unit': row['amount']['@unit'],
            'start': row['start'],
            'end': row['end']
        }
        requests.append(rq)
    return requests

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
    first = xml_obj.get(first_key, {}) or {}
    rows = first.get(second_key, []) or []
    return rows if isinstance(rows, list) else [rows]

def _parse_xml(input):
    return xmltodict.parse(input)

def change_keys(obj):
    """Replace keys of dictionaries recursively

    TODO: change convert() to recive a list of string to replace
    """
    def convert(k):
        return k.replace("@", "").replace("#", "")

    if isinstance(obj, dict):
        new = {}
        for k, v in obj.items():
            new[convert(k)] = change_keys(v)
    elif isinstance(obj, list):
        new = []
        for v in obj:
            new.append(change_keys(v))
    else:
        return obj
    return new

XML_ESCAPES = (
    ('<', '&lt;'),
    ('>', '&gt;'),
    ('&', '&amp;'),
    ("'", '&apos;'),
    ('"', '&quot;'),
)

def escape(to_escape):
    """Returns the given string with XML reserved characters encoded."""
    for char, repl in XML_ESCAPES:
        to_escape = to_escape.replace(char, repl)
    return to_escape
