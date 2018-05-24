import unittest
from unittest import mock
from subsidy_service import citizens, exceptions, config
from . import common

# config.Context.replace('subsidy_service/tests/subsidy_service_unittest.ini')


class TestCreate(unittest.TestCase):
    def test_no_phone_number(self):
        input = {'name': 'John'}
        with self.assertRaises(exceptions.BadRequestException):
            citizens.create(input)

    def test_phone_number_none(self):
        input = {'name': 'John', 'phone_number': None}
        with self.assertRaises(exceptions.BadRequestException):
            citizens.create(input)

    def test_bad_phone_number(self):
        input = {'name': 'John', 'phone_number': 'not a number'}
        with self.assertRaises(exceptions.BadRequestException):
            citizens.create(input)

    @mock.patch('subsidy_service.mongo.find',
                return_value={'name': 'John', 'phone_number': '+31612345678'})
    def test_citizen_exists(self, find_mock: mock.Mock):
        input = find_mock.return_value
        with self.assertRaises(exceptions.AlreadyExistsException):
            citizens.create(input)

    @mock.patch('subsidy_service.mongo.find', return_value=None)
    @mock.patch('subsidy_service.mongo.add_and_copy_id',
                new=common.dummy_func(return_arg=0))
    def test_good_creation(self, find_mock: mock.Mock):
        input = {'name': 'John', 'phone_number': '+31612345678'}
        output = citizens.create(input)
        self.assertDictEqual(output, input)

    @mock.patch('subsidy_service.mongo.find', return_value=None)
    @mock.patch('subsidy_service.mongo.add_and_copy_id',
                new=common.dummy_func(return_arg=0))
    def test_phone_number_gets_formatted(self, find_mock: mock.Mock):
        input = {'name': 'John', 'phone_number': '06 123-45678'}
        expected = {'name': 'John', 'phone_number': '+31612345678'}
        output = citizens.create(input)
        self.assertDictEqual(output, expected)


class TestRead(unittest.TestCase):
    @mock.patch('subsidy_service.mongo.get_by_id', return_value=None)
    def test_not_found(self, get_mock: mock.Mock):
        with self.assertRaises(exceptions.NotFoundException):
            citizens.read('123')

    @mock.patch('subsidy_service.mongo.get_by_id',
                return_value={'name': 'John'})
    def test_found(self, get_mock: mock.Mock):
        self.assertEqual(citizens.read('123'), get_mock.return_value)


class TestReadAll(unittest.TestCase):
    @mock.patch('subsidy_service.mongo.get_collection', return_value=[])
    def test_not_found(self, get_mock: mock.Mock):
        self.assertListEqual(citizens.read_all(), [])

    @mock.patch('subsidy_service.mongo.get_collection',
                return_value=[{'name': 'John'}, {'name': 'Maarten'}])
    def test_found(self, get_mock: mock.Mock):
        self.assertListEqual(citizens.read_all(), get_mock.return_value)


class TestDelete(unittest.TestCase):
    @mock.patch('subsidy_service.mongo.delete_by_id', autospec=True)
    @mock.patch('subsidy_service.mongo.get_by_id', return_value=None)
    def test_not_found(self, get_mock: mock.Mock, delete_mock: mock.Mock):
        with self.assertRaises(exceptions.NotFoundException):
            citizens.delete(123)
        delete_mock.assert_not_called()

    @mock.patch('subsidy_service.mongo.delete_by_id', autospec=True)
    @mock.patch('subsidy_service.mongo.get_by_id',
                return_value={'name': 'john'})
    def test_found(self, get_mock: mock.Mock, delete_mock: mock.Mock):
        self.assertIsNone(citizens.delete(123))
        delete_mock.assert_called()


class TestUpdate(unittest.TestCase):
    def test_not_implemented(self):
        with self.assertRaises(exceptions.NotImplementedException):
            citizens.update(123, {'name': 'john'})


class TestReplace(unittest.TestCase):
    def test_not_implemented(self):
        with self.assertRaises(exceptions.NotImplementedException):
            citizens.replace(123, {'name': 'john'})
