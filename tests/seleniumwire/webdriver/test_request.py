import uuid
from unittest import TestCase
from unittest.mock import Mock, patch

from seleniumwire.webdriver.request import InspectRequestsMixin, Request, Response


class Driver(InspectRequestsMixin):
    pass


class InspectRequestsMixinTest(TestCase):

    @patch('seleniumwire.webdriver.request.client')
    def test_request_property(self, mock_client):
        driver = Driver()
        driver.requests

        mock_client.capture_requests.assert_called_once_with()


class RequestTest(TestCase):

    def test_create_request(self):
        request_id = uuid.uuid4()
        data = self._request_data(request_id)

        request = Request(data)

        self.assertEqual(request.id, request_id)
        self.assertEqual(request.method, 'GET'),
        self.assertEqual(request.path, 'http://www.example.com/some/path/')
        self.assertEqual(len(request.headers), 3)
        self.assertEqual(request.headers['Host'], 'www.example.com')
        self.assertIsNone(request.body)
        self.assertIsNone(request.response)

    def test_request_repr(self):
        data = self._request_data(uuid.uuid4())

        request = Request(data)

        self.assertEqual(repr(request), 'Request({})'.format(data))

    def test_request_str(self):
        data = self._request_data(uuid.uuid4())

        request = Request(data)

        self.assertEqual(str(request), 'http://www.example.com/some/path/'.format(data))

    def test_create_response(self):
        data = self._response_data()

        response = Response(data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.reason, 'OK')
        self.assertEqual(len(response.headers), 2)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertIsNone(response.body)

    def test_response_repr(self):
        data = self._response_data()

        response = Response(data)

        self.assertEqual(repr(response), 'Response({})'.format(data))

    def test_response_str(self):
        data = self._response_data()

        response = Response(data)

        self.assertEqual(str(response), '200 OK'.format(data))

    def test_create_request_with_response(self):
        data = self._request_data(uuid.uuid4())
        data['response'] = self._response_data()

        request = Request(data)

        self.assertIsInstance(request.response, Response)

    def test_load_request_body(self):
        self.fail('Implement')

    def test_load_response_body(self):
        self.fail('Implement')

    def _request_data(self, request_id):
        data = {
            'id': request_id,
            'method': 'GET',
            'path': 'http://www.example.com/some/path/',
            'headers': {
                'Accept': '*/*',
                'Host': 'www.example.com',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0'
            },
            'body': None,
            'response': None
        }

        return data

    def _response_data(self):
        data = {
            'status_code': 200,
            'reason': 'OK',
            'headers': {
                'Content-Type': 'application/json',
                'Content-Length': 120
            },
            'body': None
        }

        return data
