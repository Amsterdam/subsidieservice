import unittest
from unittest import mock
from subsidy_service import subsidies, exceptions
import subsidy_service as service
from . import common

DUMMY_MASTER = {
    'name': 'Dummy Master',
    'bunq_id': 1234,
    'id': 'abcd',
    'iban':'NL66 1234',
    'description': 'bunq account',
}

DUMMY_CITIZEN = {
    'name': 'John Doe',
    'phone_number': '+3161234',
    'email': 'test@example.com',
    'id': '1234',
}

DUMMY_ACCOUNT = {
    "description": "Example Subsidy",
    "iban": "NL46BUNQ9900130413",
    "name": "Lovelace N.V.",
    "bunq_id": 1234,
    "balance": 100.0
}

DUMMY_SHARE = {'status': 'ACCEPTED'}

DUMMY_SUBSIDY = {
    "account": DUMMY_ACCOUNT,
    "amount": 100.0,
    "id": "1234",
    "master": DUMMY_MASTER,
    "name": "Example Subsidy",
    "recipient": DUMMY_CITIZEN,
    "status": "SHARE_CLOSED",
}


class TestCreate(unittest.TestCase):
    pass

@mock.patch('subsidy_service.subsidies.get_and_update',
            return_value=DUMMY_SUBSIDY)
class TestRead(unittest.TestCase):
    def setUp(self):
        service.bunq.get_payments = mock.MagicMock(return_value=[])

        self.original_dummy_sub = DUMMY_SUBSIDY.copy()
        self.original_dummy_share = DUMMY_SHARE.copy()
        self.original_dummy_acct = DUMMY_ACCOUNT.copy()

    def tearDown(self):
        super().tearDown()
        global DUMMY_SUBSIDY, DUMMY_SHARE, DUMMY_ACCOUNT
        DUMMY_SUBSIDY = self.original_dummy_sub.copy()
        DUMMY_SHARE = self.original_dummy_share.copy()
        DUMMY_ACCOUNT = self.original_dummy_acct.copy()

    def test_updated(self, get_update_mock: mock.Mock):
        subsidies.read(123)
        subsidies.get_and_update.assert_called()

    def test_got_payments(self, get_update_mock: mock.Mock):
        output = subsidies.read(123)
        self.assertIn('transactions', output['account'])


class TestReadAll(unittest.TestCase):
    pass

class TestUpdate(unittest.TestCase):
    def test_not_implemented(self):
        with self.assertRaises(exceptions.NotImplementedException):
            subsidies.update(123, {'name': 'Subsidy'})


class TestReplace(unittest.TestCase):
    def test_not_implemented(self):
        with self.assertRaises(exceptions.NotImplementedException):
            subsidies.replace(123, {'name': 'Subsidy'})


class TestDelete(unittest.TestCase):
    pass


class TestApprove(unittest.TestCase):
    def test_not_implemented(self):
        with self.assertRaises(exceptions.NotImplementedException):
            subsidies.approve(123)


@mock.patch('subsidy_service.mongo.update_by_id',
            new=common.dummy_func(return_arg=1))
@mock.patch('time.sleep', new=common.dummy_func())
class TestGetAndUpdate(unittest.TestCase):
    def setUp(self):
        super().setUp()
        service.mongo.get_by_id = mock.MagicMock(return_value=DUMMY_SUBSIDY)
        service.bunq.get_balance = mock.MagicMock(return_value=1234)
        service.bunq.read_account = mock.MagicMock(return_value=DUMMY_ACCOUNT)

        self.original_dummy_sub = DUMMY_SUBSIDY.copy()
        self.original_dummy_share = DUMMY_SHARE.copy()

    def tearDown(self):
        super().tearDown()
        global DUMMY_SUBSIDY, DUMMY_SHARE
        DUMMY_SUBSIDY = self.original_dummy_sub.copy()
        DUMMY_SHARE = self.original_dummy_share.copy()

    @mock.patch('subsidy_service.mongo.get_by_id', new=common.dummy_func())
    def test_subsidy_not_found(self):
        with self.assertRaises(exceptions.NotFoundException):
            subsidies.get_and_update(123)

    def test_master_balance(self):
        subsidies.get_and_update(123, master_balance=True)
        service.bunq.get_balance.assert_called()

    def test_status_pending_account(self):
        DUMMY_SUBSIDY['status'] = subsidies.STATUSCODE.PENDING_ACCOUNT
        output = subsidies.get_and_update(123)
        self.assertEqual(output['status'], subsidies.STATUSCODE.PENDING_ACCOUNT)

    def test_status_pending_accept_not_accepted(self):
        DUMMY_SUBSIDY['status'] = subsidies.STATUSCODE.PENDING_ACCEPT
        DUMMY_ACCOUNT['shares'] = []
        output = subsidies.get_and_update(123)
        self.assertEqual(output['status'], subsidies.STATUSCODE.PENDING_ACCEPT)

    def test_status_pending_accept_accepted(self):
        DUMMY_SUBSIDY['status'] = subsidies.STATUSCODE.PENDING_ACCEPT
        DUMMY_SHARE['status'] = 'ACCEPTED'
        DUMMY_ACCOUNT['shares'] = [DUMMY_SHARE]
        output = subsidies.get_and_update(123)
        self.assertEqual(output['status'], subsidies.STATUSCODE.OPEN)

    def test_status_open_cancelled(self):
        DUMMY_SUBSIDY['status'] = subsidies.STATUSCODE.PENDING_ACCEPT

        for status in ['CANCELLED', 'REVOKED', 'REJECTED']:
            with self.subTest(status=status):
                DUMMY_SHARE['status'] = status
                DUMMY_ACCOUNT['shares'] = [DUMMY_SHARE]
                output = subsidies.get_and_update(123)
                self.assertEqual(output['status'],
                                 subsidies.STATUSCODE.SHARE_CLOSED)

    def test_status_open(self):
        DUMMY_SUBSIDY['status'] = subsidies.STATUSCODE.PENDING_ACCEPT
        DUMMY_SHARE['status'] = 'ACCEPTED'
        DUMMY_ACCOUNT['shares'] = [DUMMY_SHARE]
        output = subsidies.get_and_update(123)
        self.assertEqual(output['status'], subsidies.STATUSCODE.OPEN)

    def test_status_closed(self):
        DUMMY_SUBSIDY['status'] = subsidies.STATUSCODE.CLOSED
        output = subsidies.get_and_update(123)
        self.assertEqual(output['status'], subsidies.STATUSCODE.CLOSED)






