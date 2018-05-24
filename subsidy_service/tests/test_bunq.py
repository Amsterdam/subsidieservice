import unittest
from subsidy_service import bunq, exceptions, config
from unittest import mock
from bunq.sdk.model.generated import endpoint, object_
from bunq.sdk import exception #as bunq_exception


# config.Context.replace('subsidy_service/tests/subsidy_service_unittest.ini')


class TestAliasFromErrorMessage(unittest.TestCase):
    def test_no_alias(self):
        input = 'This is not the message you are looking for'
        self.assertIsNone(bunq._get_alias_from_error_message(input))

    def test_alias(self):
        input = 'Account already has a Connect with user with alias "test"'
        self.assertEqual(bunq._get_alias_from_error_message(input), 'test')


class TestConvertException(unittest.TestCase):
    def test_not_found(self):
        input = exception.NotFoundException('', 123, '')
        self.assertIsInstance(bunq._convert_exception(input),
                              exceptions.NotFoundException)

    def test_bad_request(self):
        input = exception.BadRequestException('', 123, '')
        self.assertIsInstance(bunq._convert_exception(input),
                              exceptions.BadRequestException)

    def test_rate_limit(self):
        input = exception.TooManyRequestsException('', 123, '')
        self.assertIsInstance(bunq._convert_exception(input),
                              exceptions.RateLimitException)

    def test_other_exception(self):
        input = Exception()
        self.assertEqual(bunq._convert_exception(input), input)


