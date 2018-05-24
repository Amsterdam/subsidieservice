import unittest
from subsidy_service import exceptions, config
from . import common

# config.Context.replace('subsidy_service/tests/subsidy_service_unittest.ini')


class TestExceptionHTTPEncode(unittest.TestCase):
    def test_decorator(self):
        func = common.dummy_func()
        wrapped = exceptions.exceptionHTTPencode(func)
        self.assertTrue(callable(wrapped))

    def test_404(self):
        func = common.dummy_func(raises=exceptions.NotFoundException)
        wrapped = exceptions.exceptionHTTPencode(func)
        output = wrapped()
        self.assertEqual(output.status_code, 404)

    def test_400(self):
        func = common.dummy_func(raises=exceptions.BadRequestException)
        wrapped = exceptions.exceptionHTTPencode(func)
        output = wrapped()
        self.assertEqual(output.status_code, 400)

    def test_403(self):
        func = common.dummy_func(raises=exceptions.ForbiddenException)
        wrapped = exceptions.exceptionHTTPencode(func)
        output = wrapped()
        self.assertEqual(output.status_code, 403)

    def test_401(self):
        func = common.dummy_func(raises=exceptions.UnauthorizedException)
        wrapped = exceptions.exceptionHTTPencode(func)
        output = wrapped()
        self.assertEqual(output.status_code, 401)
        self.assertIn('WWW-Authenticate', output.headers)

    def test_429(self):
        func = common.dummy_func(raises=exceptions.RateLimitException)
        wrapped = exceptions.exceptionHTTPencode(func)
        output = wrapped()
        self.assertEqual(output.status_code, 429)

    def test_501(self):
        func = common.dummy_func(raises=exceptions.NotImplementedException)
        wrapped = exceptions.exceptionHTTPencode(func)
        output = wrapped()
        self.assertEqual(output.status_code, 501)

    def test_409(self):
        func = common.dummy_func(raises=exceptions.AlreadyExistsException)
        wrapped = exceptions.exceptionHTTPencode(func)
        output = wrapped()
        self.assertEqual(output.status_code, 409)

    def test_500(self):
        func = common.dummy_func(raises=Exception)
        wrapped = exceptions.exceptionHTTPencode(func)
        output = wrapped()
        self.assertEqual(output.status_code, 500)

