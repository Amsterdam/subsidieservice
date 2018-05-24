import unittest
from unittest import mock
from subsidy_service import users, exceptions, auth, config
from . import common


# config.Context.replace('subsidy_service/tests/subsidy_service_unittest.ini')


USR = 'usr'
PWD = 'PWD'
PWD_HASHED = auth.hash_password(PWD)
DUMMY_USER = {'id': '123',
              'username': USR,
              'password': PWD_HASHED}

@mock.patch('subsidy_service.mongo.add_and_copy_id',
            return_value=DUMMY_USER.copy())
class TestAdd(unittest.TestCase):
    @mock.patch('subsidy_service.mongo.find',
                new=common.dummy_func(return_value=DUMMY_USER.copy()))
    def test_already_exists(self, add_mock: mock.Mock):
        with self.assertRaises(exceptions.AlreadyExistsException):
            users.add(USR, 'any_pwd')
        add_mock.assert_not_called()

    @mock.patch('subsidy_service.mongo.find', new=common.dummy_func())
    @mock.patch('subsidy_service.auth.validate_password',
                new=common.dummy_func(False))
    def test_bad_password(self, add_mock: mock.Mock):
        with self.assertRaises(exceptions.BadRequestException):
            users.add(USR, 'bad_pwd')
        add_mock.assert_not_called()

    @mock.patch('subsidy_service.mongo.find', new=common.dummy_func())
    @mock.patch('subsidy_service.auth.validate_password',
                new=common.dummy_func(True))
    def test_good(self, add_mock: mock.Mock):
        output = users.add(USR, PWD)
        add_mock.assert_called()
        new_pwd_input = add_mock.call_args[0][0]['password']
        self.assertNotEqual(new_pwd_input, PWD)
        self.assertNotIn('password', output)


class TestAuthenticate(unittest.TestCase):
    @mock.patch('subsidy_service.mongo.find', new=common.dummy_func())
    def test_not_found(self):
        self.assertFalse(users.authenticate('usr', 'pwd'))

    @mock.patch('subsidy_service.mongo.find',
                new=common.dummy_func(return_value=DUMMY_USER.copy()))
    def test_wrong_pwd(self):
        self.assertFalse(users.authenticate('usr', 'wrong_pwd'))

    @mock.patch('subsidy_service.mongo.find',
                new=common.dummy_func(return_value=DUMMY_USER.copy()))
    def test_right_pwd(self):
        self.assertTrue(users.authenticate('usr', PWD))


@mock.patch('subsidy_service.mongo.update_by_id')
class TestUpdatePassword(unittest.TestCase):
    @mock.patch('subsidy_service.mongo.find', new=common.dummy_func())
    def test_not_found(self, update_mock: mock.Mock):
        with self.assertRaises(exceptions.NotFoundException):
            users.update_password(USR, 'pwd', 'new_pwd')

    @mock.patch('subsidy_service.mongo.find',
                new=common.dummy_func(DUMMY_USER.copy()))
    @mock.patch('subsidy_service.auth.validate_password',
                new=common.dummy_func(True))
    def test_wrong_password(self, update_mock: mock.Mock):
        with self.assertRaises(exceptions.ForbiddenException):
            users.update_password(USR, 'wrong_pwd', 'new_pwd')
        update_mock.assert_not_called()

    @mock.patch('subsidy_service.mongo.find',
                new=common.dummy_func(DUMMY_USER.copy()))
    @mock.patch('subsidy_service.auth.validate_password',
                new=common.dummy_func(False))
    def test_bad_new_password(self, update_mock: mock.Mock):
        with self.assertRaises(exceptions.BadRequestException):
            users.update_password(USR, 'wrong_pwd', 'new_pwd')
        update_mock.assert_not_called()

    @mock.patch('subsidy_service.mongo.find',
                new=common.dummy_func(DUMMY_USER.copy()))
    @mock.patch('subsidy_service.auth.validate_password',
                new=common.dummy_func(True))
    def test_good_hashed(self, update_mock: mock.Mock):
        users.update_password(USR, PWD, 'new_pwd')
        update_mock.assert_called()
        new_pwd_input = update_mock.call_args[0][1]['password']
        self.assertNotEqual(new_pwd_input, 'new_pwd')


@mock.patch('subsidy_service.mongo.find',
            new=common.dummy_func(return_value=DUMMY_USER.copy()))
@mock.patch('subsidy_service.mongo.delete_by_id')
class TestDelete(unittest.TestCase):
    def test_wrong_password(self, delete_mock: mock.Mock):
        with self.assertRaises(exceptions.ForbiddenException):
            users.delete(USR, 'wrong_pwd')
        delete_mock.assert_not_called()

    def test_right_password(self, delete_mock: mock.Mock):
        self.assertIsNone(users.delete(USR, PWD))
        delete_mock.assert_called()
