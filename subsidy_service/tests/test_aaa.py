"""File will be run first when collecting tests. Changes the Context to
the Test Context and asserts that this has been done."""
import unittest
from subsidy_service import config

config.Context.replace('subsidy_service/tests/subsidy_service_unittest.ini')

if 'subsidy_service_unittest.ini' not in config.Context._last_read:
    raise RuntimeError('Testing Context not loaded, aborting')

class TestContextActive(unittest.TestCase):
    def test_context_active(self):
        self.assertIn('subsidy_service_unittest.ini', config.Context._last_read)
