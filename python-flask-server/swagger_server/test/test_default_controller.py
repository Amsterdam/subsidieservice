# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.user import User  # noqa: E501
from swagger_server.test import BaseTestCase


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def test_login_post(self):
        """Test case for login_post

        Login a user; this a virtual endpoint to just confirm the user exists. Also important to see whether a user is an admin or not.
        """
        body = User()
        response = self.client.open(
            '/api/v2/login',
            method='POST',
            data=json.dumps(body),
            content_type='application/nl.kpmg.v2.user+json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
