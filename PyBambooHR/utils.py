"""
A collection of misc. utilities that are used in the main class.
"""

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


