from seleniumwire.proxy import client


class InspectRequestsMixin:
    """Mixin class that provides functions to capture and inspect browser requests."""

    @property
    def requests(self):
        # Want to be able to support:
        #
        # webdriver.requests -> []  (list of all requests)
        # webdriver.requests['/path/of/some/request'] -> []  (list of all requests that match)
        # del webdriver.requests (clears the requests from the proxy)
        return client.requests()

    @requests.deleter
    def requests(self):
        pass

    @property
    def last_request(self):
        pass

    def requests_for(self, path):
        pass

    @property
    def header_overrides(self):
        # Support del firefox.header_overrides to clear all overrides?
        pass

    @header_overrides.setter
    def header_overrides(self, headers):
        pass

    @header_overrides.deleter
    def header_overrides(self):
        pass

    def _create_proxy(self):
        return client.create_proxy()

    def _destroy_proxy(self):
        client.destroy_proxy()


class Request:
    """An HTTP request made by the browser to the server."""

    def __init__(self, data):
        """Initialise a new Request object with a dictionary of data, which takes
        the format:

        data = {
            'id': 'request id',
            'method': 'GET',
            'path': 'http://www.example.com/some/path',
            'headers': {
                'Accept': '*/*',
                'Host': 'www.example.com'
            }
            'response': {
                'status_code': 200,
                'reason': 'OK',
                'headers': {
                    'Content-Type': 'text/plain',
                    'Content-Length': 15012
                }
            }
        }

        Note that the value of the 'response' key may be None where no response
        is associated with a given request.

        Args:
            data: The dictionary of data.
        """
        self._data = data
        self.method = data['method']
        self.path = data['path']
        self.headers = data['headers']
        if data['response'] is not None:
            self.response = Response(self._data['id'], data['response'])
        else:
            self.response = None

    @property
    def body(self):
        """Lazily retrieve the request body when it is asked for.

        Returns: The response bytes.
        """

    def __repr__(self):
        return 'Request({})'.format(self._data)

    def __str__(self):
        return self.path


class Response:
    """An HTTP response returned from the server to the browser."""

    def __init__(self, request_id, data):
        """Initialise a new Response object with a request id and a dictionary
        of data, which takes the format:

        data = {
            'status_code': 200,
            'reason': 'OK',
            'headers': {
                'Content-Type': 'text/plain',
                'Content-Length': 15012
            }
        }

        Args:
            request_id: The request id.
            data: The dictionary of data.
        """
        self._request_id = request_id
        self._data = data
        self.status_code = data['status_code']
        self.reason = data['reason']
        self.headers = data['headers']

    @property
    def body(self):
        """Lazily retrieve the response body when it is asked for.

        Returns: The response bytes.
        """

    def __repr__(self):
        return 'Response({}, {})'.format(self._request_id, self._data)

    def __str__(self):
        return '{} {}'.format(self.status_code, self.reason)
