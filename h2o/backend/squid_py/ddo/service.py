"""
    Service Class
    To handle service items in a DDO record
"""

import json
import re


class Service:
    """
    Service class to create validate service in a DDO
    """

    def __init__(self, service_id, endpoint, service_type, values):
        self._id = service_id
        self._endpoint = endpoint
        self._type = service_type

        # assign the _values property to empty until they are used
        self._values = {}
        reserved_names = {'id', 'serviceEndpoint', 'type'}
        if values:
            for name, value in values.items():
                if name not in reserved_names:
                    self._values[name] = value

    def get_id(self):
        """Return the service id"""
        return self._id

    def assign_did(self, did):
        """ Assign a new DID/Id to the service"""
        if re.match('^#.*', self._id):
            self._id = did + self._id

    def get_type(self):
        """get the service type"""
        return self._type

    def get_endpoint(self):
        """get the service endpoint"""
        return self._endpoint

    def get_values(self):
        """get any service value s"""
        return self._values

    def update_value(self, name, value):
        if name not in {'id', 'serviceEndpoint', 'type'}:
            self._values[name] = value

    def as_text(self, is_pretty=False):
        """return the service as a JSON string"""
        values = {
            'id': self._id,
            'type': self._type,
            'serviceEndpoint': self._endpoint
        }
        if self._values:
            # add extra service values to the dictonairy
            for name, value in self._values.items():
                values[name] = value

        if is_pretty:
            return json.dumps(values, indent=4, separators=(',', ': '))

        return json.dumps(values)

    def as_dictionary(self):
        """return the service as a python dictionary"""
        values = {
            'id': self._id,
            'type': self._type,
            'serviceEndpoint': self._endpoint
        }
        if self._values:
            # add extra service values to the dictonairy
            for name, value in self._values.items():
                if isinstance(value, object) and hasattr(value, 'as_dictionary'):
                    value = value.as_dictionary()
                elif isinstance(value, list):
                    value = [v.as_dictionary() if hasattr(v, 'as_dictionary') else v for v in value]

                values[name] = value
        return values

    def is_valid(self):
        """return True if the sevice is valid"""
        return self._endpoint is not None and self._type is not None
