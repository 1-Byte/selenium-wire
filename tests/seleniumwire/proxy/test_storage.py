import glob
import os
import pickle
import shutil
from unittest import TestCase
from unittest.mock import Mock

from seleniumwire.proxy.storage import RequestStorage


class RequestStorageTest(TestCase):

    def setUp(self):
        self.base_dir = os.path.join(os.path.dirname(__file__), 'data')
        self.storage = RequestStorage(base_dir=self.base_dir)

    def test_initialise(self):
        storage_dir = glob.glob(os.path.join(self.base_dir, 'seleniumwire', 'storage-*'))

        self.assertEqual(len(storage_dir), 1)

    def test_save_request(self):
        mock_request = self._create_mock_request()

        request_id = self.storage.save_request(mock_request)

        request_file_path = self._get_full_path(request_id, 'request')

        with open(request_file_path[0], 'rb') as loaded:
            loaded_request = pickle.load(loaded)

        self.assertEqual(loaded_request['id'], request_id)
        self.assertEqual(loaded_request['path'], 'http://www.example.com/test/path/')
        self.assertEqual(loaded_request['method'], 'GET')
        self.assertEqual(loaded_request['headers'], {
            'Host': 'www.example.com',
            'Accept': '*/*'
        })
        self.assertIsNone(loaded_request['response'])

    def test_save_request_with_body(self):
        mock_request = self._create_mock_request()
        request_body = 'test request body'

        request_id = self.storage.save_request(mock_request, request_body)

        request_body_path = self._get_full_path(request_id, 'requestbody')

        with open(request_body_path[0], 'rb') as loaded:
            loaded_body = pickle.load(loaded)

        self.assertEqual(loaded_body, 'test request body')

    def test_save_response(self):
        mock_request = self._create_mock_request()
        request_id = self.storage.save_request(mock_request)
        mock_response = self._create_mock_resonse()

        self.storage.save_response(request_id, mock_response)

        response_file_path = self._get_full_path(request_id, 'response')

        with open(response_file_path[0], 'rb') as loaded:
            loaded_response = pickle.load(loaded)

        self.assertEqual(loaded_response['status_code'], 200)
        self.assertEqual(loaded_response['reason'], 'OK')
        self.assertEqual(loaded_response['headers'], {
            'Content-Type': 'application/json',
            'Content-Length': 500
        })

    def test_save_response_with_body(self):
        mock_request = self._create_mock_request()
        request_id = self.storage.save_request(mock_request)
        mock_response = self._create_mock_resonse()
        response_body = 'some response body'

        self.storage.save_response(request_id, mock_response, response_body)

        response_body_path = self._get_full_path(request_id, 'responsebody')

        with open(response_body_path[0], 'rb') as loaded:
            loaded_body = pickle.load(loaded)

        self.assertEqual(loaded_body, 'some response body')

    def _get_full_path(self, request_id, filename):
        return glob.glob(os.path.join(self.base_dir, 'seleniumwire', 'storage-*',
                                      'request-{}'.format(request_id), filename))

    def _create_mock_request(self):
        mock_request = Mock()
        mock_request.path = 'http://www.example.com/test/path/'
        mock_request.command = 'GET'
        mock_request.headers = {
            'Host': 'www.example.com',
            'Accept': '*/*'
        }
        return mock_request

    def _create_mock_resonse(self):
        mock_response = Mock()
        mock_response.status = 200
        mock_response.reason = 'OK'
        mock_response.headers = {
            'Content-Type': 'application/json',
            'Content-Length': 500
        }
        return mock_response

    def tearDown(self):
        shutil.rmtree(os.path.join(self.base_dir), ignore_errors=True)
