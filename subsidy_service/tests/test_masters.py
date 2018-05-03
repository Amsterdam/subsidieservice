import unittest
from unittest import mock
import subsidy_service as service
from subsidy_service import masters, exceptions, config
from . import common

# config.Context.replace('subsidy_service/tests/subsidy_service_unittest.ini')


DUMMY_MASTER = {
    'name': 'Dummy Master',
    'bunq_id': 1234,
    'id': 'abcd',
    'iban':'NL66 1234'
}


@mock.patch('subsidy_service.mongo.update_by_id',
            new=common.dummy_func(return_arg=1))
class TestGetAndUpdateBalance(unittest.TestCase):
    @mock.patch('subsidy_service.mongo.get_by_id', return_value=None)
    def test_not_found(self, get_mock: mock.Mock):
        with self.assertRaises(exceptions.NotFoundException):
            masters.get_and_update_balance(123)

    @mock.patch('subsidy_service.bunq.get_balance',
                new=common.dummy_func(raises=exceptions.NotFoundException))
    def test_balance_not_found(self):
        master = DUMMY_MASTER.copy()
        master_with_balance = DUMMY_MASTER.copy()
        master_with_balance['balance'] = None
        service.mongo.get_by_id = mock.MagicMock(return_value=master)
        expected = master_with_balance

        self.assertDictEqual(masters.get_and_update_balance(123), expected)

    @mock.patch('subsidy_service.bunq.get_balance', return_value=1000.00)
    def test_balance_found(self, get_balance_mock: mock.Mock):
        master = DUMMY_MASTER.copy()
        master_with_balance = DUMMY_MASTER.copy()
        master_with_balance['balance'] = get_balance_mock.return_value
        service.mongo.get_by_id = mock.MagicMock(return_value=master)
        expected = master_with_balance

        self.assertDictEqual(masters.get_and_update_balance(123), expected)


class TestGetPaymentsIfAvailable(unittest.TestCase):
    @mock.patch('subsidy_service.bunq.get_payments',
                new=common.dummy_func(raises=exceptions.NotFoundException))
    def test_not_found_exception_caught(self):
        self.assertIsNone(masters.get_payments_if_available(123))


@mock.patch('subsidy_service.mongo.add_and_copy_id',
            new=common.dummy_func(return_arg=0))
@mock.patch('subsidy_service.bunq.read_account_by_iban',
            new=common.dummy_func(return_value=DUMMY_MASTER.copy()))
@mock.patch('subsidy_service.masters.get_payments_if_available',
            new=common.dummy_func(return_value=[{'to': 'john'}]))
@mock.patch('subsidy_service.bunq.create_account',
            return_value=DUMMY_MASTER.copy())  # different pointer
class TestCreate(unittest.TestCase):
    @mock.patch('subsidy_service.mongo.find', return_value=DUMMY_MASTER.copy())
    def test_already_exists(self, find_mock: mock.Mock, create_mock: mock.Mock):
        with self.assertRaises(exceptions.AlreadyExistsException):
            masters.create(DUMMY_MASTER.copy())
        create_mock.assert_not_called()

    @mock.patch('subsidy_service.mongo.find', new=common.dummy_func())
    def test_known_iban(self, create_mock: mock.Mock):
        input = DUMMY_MASTER.copy()
        output = masters.create(input)
        create_mock.assert_not_called()
        self.assertIn('transactions', output)

    @mock.patch('subsidy_service.mongo.find', new=common.dummy_func())
    def test_no_iban(self, create_mock: mock.Mock):
        input = DUMMY_MASTER.copy()
        input.pop('iban')
        output = masters.create(input)
        create_mock.assert_called()
        self.assertEqual(DUMMY_MASTER['iban'], output['iban'])
        self.assertIn('transactions', output)


@mock.patch('subsidy_service.masters.get_payments_if_available',
            new=common.dummy_func(return_value=[{'to': 'john'}]))
@mock.patch('subsidy_service.masters.get_and_update_balance',
            new=common.dummy_func(return_value=DUMMY_MASTER.copy()))
class TestRead(unittest.TestCase):
    def test_transactions_included(self):
        self.assertIn('transactions', masters.read(123))


@mock.patch('time.sleep', new=common.dummy_func())
@mock.patch('subsidy_service.masters.get_and_update_balance',
            new=common.dummy_func(return_value=DUMMY_MASTER.copy()))
class TestReadAll(unittest.TestCase):
    @mock.patch('subsidy_service.mongo.get_collection', return_value=[])
    def test_not_found(self, get_mock: mock.Mock):
        output = masters.read_all()
        self.assertIsNotNone(output)
        self.assertListEqual(output, [])

    @mock.patch('subsidy_service.mongo.get_collection',
                return_value=[DUMMY_MASTER.copy(), DUMMY_MASTER.copy()])
    def test_found(self, get_mock: mock.Mock):
        output = masters.read_all()
        self.assertEqual(len(output), len(get_mock.return_value))
        for acct in output:
            self.assertNotIn('transactions', acct)


@mock.patch('time.sleep', new=common.dummy_func())
class TestDelete(unittest.TestCase):
    @mock.patch('subsidy_service.mongo.delete_by_id', autospec=True)
    @mock.patch('subsidy_service.mongo.get_by_id', return_value=None)
    def test_not_found(self, get_mock: mock.Mock, delete_mock: mock.Mock):
        with self.assertRaises(exceptions.NotFoundException):
            masters.delete(123)
        delete_mock.assert_not_called()

    @mock.patch('subsidy_service.mongo.delete_by_id', autospec=True)
    @mock.patch('subsidy_service.mongo.get_by_id',
                return_value=DUMMY_MASTER.copy())
    def test_found(self, get_mock: mock.Mock, delete_mock: mock.Mock):
        self.assertIsNone(masters.delete(123))
        delete_mock.assert_called()


@mock.patch('time.sleep', new=common.dummy_func())
class TestUpdate(unittest.TestCase):
    def test_not_implemented(self):
        with self.assertRaises(exceptions.NotImplementedException):
            masters.update(123, DUMMY_MASTER.copy())


@mock.patch('time.sleep', new=common.dummy_func())
class TestReplace(unittest.TestCase):
    def test_not_implemented(self):
        with self.assertRaises(exceptions.NotImplementedException):
            masters.replace(123, DUMMY_MASTER.copy())
