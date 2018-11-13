# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.user import User  # noqa: E501
from swagger_server.test import BaseTestCase


class TestUsersController(BaseTestCase):
    """UsersController integration test stubs"""

    def test_users_get(self):
        """Test case for users_get

        Returns a list of users.
        """
        response = self.client.open(
            '/api/v1/users',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_users_post(self):
        """Test case for users_post

        Create a new user
        """
        body = User()
        response = self.client.open(
            '/api/v1/users',
            method='POST',
            data=json.dumps(body),
            content_type='application/nl.kpmg.v1.user+json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_users_username_delete(self):
        """Test case for users_username_delete

        Remove a user
        """
        response = self.client.open(
            '/api/v1/users/{username}'.format(username='username_example'),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_users_username_get(self):
        """Test case for users_username_get

        Returns a specific user
        """
        response = self.client.open(
            '/api/v1/users/{username}'.format(username='username_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_users_username_patch(self):
        """Test case for users_username_patch

        Edit a user's information
        """
        body = User()
        response = self.client.open(
            '/v1/users/{username}'.format(username='username_example'),
            method='PATCH',
            data=json.dumps(body),
            content_type='application/nl.kpmg.v1.user+json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_users_username_put(self):
        """Test case for users_username_put

        Re-upload user's information
        """
        body = User()
        response = self.client.open(
            '/api/v1/users/{username}'.format(username='username_example'),
            method='PUT',
            data=json.dumps(body),
            content_type='application/nl.kpmg.v1.user+json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
