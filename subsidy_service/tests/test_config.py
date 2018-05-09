from subsidy_service.config import Context
import unittest
from unittest import mock
from . import common
import collections

DUMMY_CLIENT = collections.namedtuple('client', ['subsidy'])('test_db')


@mock.patch('pymongo.MongoClient', new=common.dummy_func(DUMMY_CLIENT))
@mock.patch('bunq.sdk.context.ApiContext.restore', new=common.dummy_func(None))
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




