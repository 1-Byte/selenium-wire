import socket
import ssl
from unittest import TestCase
import urllib.request

from seleniumwire.proxy.client import AdminClient


class AdminClientTest(TestCase):

    def setUp(self):
        self.client = AdminClient()
        host, port = self.client.create_proxy()
        self._configure_proxy(host, port)

    def tearDown(self):
        self.client.destroy_proxy()

    def test_create_proxy(self):
        html = self._make_request('http://python.org')

        self.assertIn(b'Welcome to Python.org', html)

    def test_destroy_proxy(self):
        self.client.destroy_proxy()

        with self.assertRaises(socket.timeout):
            self._make_request('http://python.org')

    def test_get_requests_single(self):
        self._make_request('http://python.org')

        requests = self.client.get_requests()

        self.assertEqual(len(requests), 1)
        request = requests[0]
        self.assertEqual(request['method'], 'GET')
        self.assertEqual(request['path'], 'http://python.org')
        self.assertEqual(request['headers']['Accept-Encoding'], 'identity')
        self.assertEqual(request['response']['status_code'], 301)
        self.assertEqual(request['response']['headers']['Content-Type'], 'text/html')

    def test_get_requests_multiple(self):
        self._make_request('http://python.org')
        self._make_request('http://www.wikipedia.org')

        requests = self.client.get_requests()

        self.assertEqual(len(requests), 2)

    def test_get_requests_https(self):
        self._make_request('https://www.wikipedia.org')

        requests = self.client.get_requests()

        self.assertEqual(len(requests), 1)
        request = requests[0]
        self.assertEqual(request['method'], 'GET')
        self.assertEqual(request['path'], 'https://www.wikipedia.org')
        self.assertEqual(request['headers']['Accept-Encoding'], 'identity')
        self.assertEqual(request['response']['status_code'], 200)
        self.assertEqual(request['response']['headers']['Content-Type'], 'text/html')

    def test_get_last_request(self):
        self._make_request('https://python.org')
        self._make_request('https://www.wikipedia.org')

        last_request = self.client.get_last_request()

        self.assertEqual(last_request['path'], 'https://www.wikipedia.org')

    def test_clear_requests(self):
        self._make_request('https://python.org')
        self._make_request('https://www.wikipedia.org')

        self.client.clear_requests()

        self.assertEqual(self.client.get_requests(), [])

    def test_get_request_body(self):
        self._make_request('https://www.wikipedia.org')
        last_request = self.client.get_last_request()

        body = self.client.get_request_body(last_request['id'])

        self.assertIsInstance(body, bytes)
        self.assertIn(b'html', body)

    def test_get_request_body_empty(self):
        self._make_request('https://www.wikipedia.org')
        last_request = self.client.get_last_request()

        body = self.client.get_request_body(last_request['id'])

        self.assertIsNone(body)

    def test_get_response_body(self):
        self._make_request('https://www.wikipedia.org')
        last_request = self.client.get_last_request()

        body = self.client.get_response_body(last_request['id'])

        self.assertIsInstance(body, bytes)
        self.assertIn(b'html', body)

    def test_get_response_body_binary(self):
        self._make_request('https://www.python.org/static/img/python-logo@2x.png')
        last_request = self.client.get_last_request()

        body = self.client.get_response_body(last_request['id'])

        self.assertIsInstance(body, bytes)

    def test_get_response_body_empty(self):
        self._make_request('http://www.python.org')  # Redirects to https with empty body
        redirect_request = self.client.get_requests()[0]

        body = self.client.get_response_body(redirect_request['id'])

        self.assertIsNone(body)

    def _configure_proxy(self, host, port):
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        https_handler = urllib.request.HTTPSHandler(context=context)
        proxy_handler = urllib.request.ProxyHandler({
            'http': 'http://{}:{}'.format(host, port),
            'https': 'http://{}:{}'.format(host, port),
        })
        opener = urllib.request.build_opener(https_handler, proxy_handler)
        urllib.request.install_opener(opener)

    def _make_request(self, url):
        with urllib.request.urlopen(url, timeout=1) as response:
            html = response.read()

        return html
