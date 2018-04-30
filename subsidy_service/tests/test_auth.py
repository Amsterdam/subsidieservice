import unittest
from unittest import mock
import collections
from subsidy_service import auth, exceptions


AUTH_HEADER = collections.namedtuple('header', ['username', 'password'])
REQUEST = collections.namedtuple('request', ['authorization'])
CRYPT_CTX = auth.CRYPT_CTX


class TestVerifyUser(unittest.TestCase):
    @mock.patch('subsidy_service.mongo.find', autospec=True, return_value=None)
    def test_db_lookup(self, find_mock: mock.Mock):
        auth.verify_user('usr', 'pwd')
        find_mock.assert_called_once()

    @mock.patch('subsidy_service.mongo.find', autospec=True, return_value=None)
    def test_user_not_found(self, find_mock: mock.Mock):
        self.assertFalse(auth.verify_user('usr', 'pwd'))

    @mock.patch('subsidy_service.mongo.find', autospec=True,
                return_value={'username': 'usr', 'password': 'pwd'})
    @mock.patch('subsidy_service.auth.verify_password', return_value=False)
    def test_wrong_password(self, find_mock: mock.Mock, verify_mock: mock.Mock):
        self.assertFalse(auth.verify_user('usr', 'wrong_pwd'))

    @mock.patch('subsidy_service.mongo.find', autospec=True,
                return_value={'username': 'usr', 'password': 'pwd'})
    @mock.patch('subsidy_service.auth.verify_password', return_value=True)
    def test_wrong_password(self, find_mock: mock.Mock, verify_mock: mock.Mock):
        self.assertTrue(auth.verify_user('usr', 'wrong_pwd'))


class TestValidatePassword(unittest.TestCase):
    def test_anything(self):
        self.assertTrue(auth.validate_password('literally anything'))


class TestAuthenticate(unittest.TestCase):
    def test_decorator(self):
        input = lambda x: x
        output = auth.authenticate(input)
        self.assertTrue(callable(output))

    def test_no_request(self):
        input = lambda x: x
        output = auth.authenticate(input)
        with self.assertRaises(exceptions.UnauthorizedException):
            output(123)

    @mock.patch('connexion.request', new=REQUEST(authorization=None))
    def test_no_auth_header(self):
        input = lambda x: x
        output = auth.authenticate(input)
        with self.assertRaises(exceptions.UnauthorizedException):
            output(123)

    @mock.patch('connexion.request',
                new=REQUEST(authorization=AUTH_HEADER('usr', 'pwd')))
    @mock.patch('subsidy_service.auth.verify_user', new=lambda *args: False)
    def test_not_verified(self):
        input = lambda x: x
        output = auth.authenticate(input)
        with self.assertRaises(exceptions.ForbiddenException):
            output(123)

    @mock.patch('connexion.request',
                new=REQUEST(authorization=AUTH_HEADER('usr', 'pwd')))
    @mock.patch('subsidy_service.auth.verify_user', new=lambda *args: True)
    def test_verified(self):
        input = lambda x: x
        output = auth.authenticate(input)
        self.assertEqual(output(123), input(123))


class TestVerifyPassword(unittest.TestCase):
    def test_good(self):
        hashed = CRYPT_CTX.hash('pwd')
        self.assertTrue(auth.verify_password('pwd', hashed))

    def test_bad(self):
        hashed = CRYPT_CTX.hash('pwd')
        self.assertFalse(auth.verify_password('wrong', hashed))


