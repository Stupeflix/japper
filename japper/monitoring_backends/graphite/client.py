from urlparse import urljoin

from japper.utils import HttpClient
from .exceptions import InvalidDataFormat


def average(values):
    return float(sum(values)) / len(values)


class GraphiteClient(HttpClient):

    def __init__(self, endpoint, *args, **kwargs):
        super(GraphiteClient, self).__init__(*args, **kwargs)
        self.endpoint = endpoint

    def get_metric(self, target, from_='-1minutes', aggregator=average):
        url = urljoin(self.endpoint, '/render')
        response = self.get(url, params={
            'target': target,
            'format': 'json',
            'from': from_,
        })
        data = response.json()

        # Check data format
        err_prefix = 'got invalid data for "%s": ' % target
        if not isinstance(data, list):
            raise InvalidDataFormat(err_prefix +
                    'expected a list but got a %s instead' % type(data))
        if len(data) != 1:
            raise InvalidDataFormat(err_prefix + 'multiple metrics returned')
        if not isinstance(data[0], dict):
            raise InvalidDataFormat(err_prefix + 'expected a dict '
                    'at item 0 but got a %s instead' % type(data[0]))

        # Extract values
        values = [e[0] for e in data[0]['datapoints']]

        # Aggregate values
        return aggregator(values)
