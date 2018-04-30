from subsidy_service import utils, exceptions
import unittest


class TestDropNones(unittest.TestCase):
    def test_nones(self):
        input = {'a': 1, 'b': None}
        expected = {'a': 1}
        output = utils.drop_nones(input)
        self.assertDictEqual(output, expected)

    def test_empty_strings(self):
        input = {'a': '', 'b': None}
        expected = {'a': ''}
        output = utils.drop_nones(input)
        self.assertDictEqual(output, expected)

    def test_empty_lists(self):
        input = {'a': [], 'b': None}
        expected = {'a': []}
        output = utils.drop_nones(input)
        self.assertDictEqual(output, expected)

    def test_no_nones(self):
        input = {'a': 1, 'b': 'b'}
        expected = {'a': 1, 'b': 'b'}
        output = utils.drop_nones(input)
        self.assertDictEqual(output, expected)


class TestFormatPhoneNumber(unittest.TestCase):
    def test_already_formatted(self):
        input = '+31612345678'
        expected = '+31612345678'
        output = utils.format_phone_number(input)
        self.assertEqual(output, expected)

    def test_foreign(self):
        input = '+42612345678'
        expected = '+42612345678'
        output = utils.format_phone_number(input)
        self.assertEqual(output, expected)

    def test_spaces(self):
        input = '+31 6 12 34 56 78'
        expected = '+31612345678'
        output = utils.format_phone_number(input)
        self.assertEqual(output, expected)

    def test_plus(self):
        input = '31612345678'
        expected = '+31612345678'
        output = utils.format_phone_number(input)
        self.assertEqual(output, expected)

    def test_0_to_plus31(self):
        input = '0612345678'
        expected = '+31612345678'
        output = utils.format_phone_number(input)
        self.assertEqual(output, expected)

    def test_dashes(self):
        input = '+31-6-123-45678'
        expected = '+31612345678'
        output = utils.format_phone_number(input)
        self.assertEqual(output, expected)

    def test_bad_input(self):
        inputs = [
            'this is not a phone number',
            '1.2.3.4.5',
            '+316-123-456c',
            ''
        ]

        for i, inp in enumerate(inputs):
            with self.subTest(i=i):
                with self.assertRaises(exceptions.BadRequestException):
                    output = utils.format_phone_number(inp)