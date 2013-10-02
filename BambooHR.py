import requests

class BambooHR(object):
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
        r = requests.get(url, headers=self.headers, auth=('29d50a2f95a4c697c6812599c33b293520a3bd24', ''))
        print r.json()


    def get_employee(self):
        raise NotImplemented("Returning data about a user is not implemented yet.")
