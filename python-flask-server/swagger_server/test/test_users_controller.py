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

        List all API users created by the administrator. One of the users is flagged as the administrator; that is the very first user created and may not be deleted.
        """
        response = self.client.open(
            '/api/v1/users',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_users_id_delete(self):
        """Test case for users_id_delete

        Delete a user. The administrator user may not be deleted.
        """
        response = self.client.open(
            '/api/v1/users/{id}'.format(id='id_example'),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_users_id_patch(self):
        """Test case for users_id_patch

        Edit a user's information; at the moment of writing, its pass.
        """
        body = User()
        response = self.client.open(
            '/api/v1/users/{id}'.format(id='id_example'),
            method='PATCH',
            data=json.dumps(body),
            content_type='application/nl.kpmg.v1.user+json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_users_post(self):
        """Test case for users_post

        Create a new user.
        """
        body = User()
        response = self.client.open(
            '/api/v1/users',
            method='POST',
            data=json.dumps(body),
            content_type='application/nl.kpmg.v1.user+json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
