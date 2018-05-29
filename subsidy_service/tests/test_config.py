from subsidy_service.config import Context, _get_mongo_uri
import unittest
from unittest import mock
from . import common
import collections
import os

DUMMY_CLIENT = collections.namedtuple('client', ['subsidy'])('test_db')
DUMMY_CONFIG = {
    'mongo': {
        'host': 'hst1',
        'port': '1231',
        'user': 'usr1',
        'password': 'pwd1'
    }
}

DUMMY_ENVIRON = {'MONGO_HOST': 'hst2', 'MONGO_PORT': '1232',
                 'MONGO_USER': 'usr2', 'MONGO_PASSWORD': 'pwd2'}


@mock.patch('pymongo.MongoClient', new=common.dummy_func(DUMMY_CLIENT))
@mock.patch('bunq.sdk.context.ApiContext.restore', new=common.dummy_func(None))
@mock.patch('bunq.sdk.context.BunqContext.load_api_context',
            new=common.dummy_func(None))
class TestContext(unittest.TestCase):

    @classmethod
    def setUp(cls):
        super().setUpClass()
        Context.replace(
            'subsidy_service/tests/subsidy_service_unittest.ini'
        )

    @classmethod
    def tearDown(cls):
        super().tearDownClass()
        Context.replace(
            'subsidy_service/tests/subsidy_service_unittest.ini'
        )

    def test_singleton(self):
        a = Context()
        b = Context

        self.assertIs(a, b)

    def test_nonexistent_file(self):
        Context.read('not/a/real/path.txt')
        self.assertNotIn('not/a/real', Context._last_read)

    def test_mongo_client_loaded(self):
        Context._reload_mongo_client()
        self.assertEqual(Context.mongo_client, DUMMY_CLIENT)

    def test_replace(self):
        Context.replace('not/a/path.txt')
        self.assertIsNone(Context.mongo_client)
        self.assertIsNone(Context.bunq_ctx)
        self.assertIsNone(Context._last_read)


class TestGetMongoURI(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.old_dummy_config = DUMMY_CONFIG.copy()
        self.old_dummy_environ = DUMMY_ENVIRON.copy()

        for k, v in DUMMY_ENVIRON.items():
            os.environ[k] = v

    def tearDown(self):
        global DUMMY_CONFIG, DUMMY_ENVIRON
        super().tearDown()
        DUMMY_CONFIG = self.old_dummy_config
        DUMMY_ENVIRON = self.old_dummy_environ

        for k, v in DUMMY_ENVIRON.items():
            try:
                os.environ.pop(k)
            except KeyError:
                pass

    def test_config_priority(self):
        uri, port = _get_mongo_uri(DUMMY_CONFIG)
        self.assertEqual('mongodb://usr1:pwd1@hst1', uri)
        self.assertEqual(1231, port)

    def test_environ(self):
        uri, port = _get_mongo_uri({})
        self.assertEqual('mongodb://usr2:pwd2@hst2', uri)
        self.assertEqual(1232, port)

    def test_no_user(self):
        os.environ.pop('MONGO_USER')
        uri, port = _get_mongo_uri({})
        self.assertEqual('mongodb://hst2', uri)
        self.assertEqual(1232, port)

    def test_no_password(self):
        os.environ.pop('MONGO_PASSWORD')
        uri, port = _get_mongo_uri({})
        self.assertEqual('mongodb://usr2@hst2', uri)
        self.assertEqual(1232, port)

    def test_no_host(self):
        os.environ.pop('MONGO_HOST')
        uri, port = _get_mongo_uri({})
        self.assertIsNone(uri)
        self.assertIsNone(port)

    def test_no_port(self):
        os.environ.pop('MONGO_PORT')
        uri, port = _get_mongo_uri({})
        self.assertEqual('mongodb://usr2:pwd2@hst2', uri)
        self.assertIsNone(port)

    def test_environ_fallback(self):
        DUMMY_CONFIG['mongo'].pop('user')
        uri, port = _get_mongo_uri(DUMMY_CONFIG)
        self.assertEqual('mongodb://usr2:pwd1@hst1', uri)
        self.assertEqual(1231, port)

