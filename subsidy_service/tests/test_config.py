from subsidy_service import config
import unittest
from unittest import mock
from . import common
import collections

DUMMY_CLIENT = collections.namedtuple('client',['subsidy'])('test_db')


@mock.patch('pymongo.MongoClient', new=common.dummy_func(DUMMY_CLIENT))
@mock.patch('bunq.sdk.context.ApiContext.restore', new=common.dummy_func(None))
class TestContext(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        config.Context.replace(
            'subsidy_service/tests/subsidy_service_unittest.ini'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        config.Context.replace(
            'subsidy_service/tests/subsidy_service_unittest.ini'
        )

    def test_singleton(self):
        a = config.Context()
        b = config.Context

        self.assertTrue(a is b)
