# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.initiative import Initiative  # noqa: E501
from swagger_server.test import BaseTestCase


class TestInitiativesController(BaseTestCase):
    """InitiativesController integration test stubs"""

    def test_initiatives_delete(self):
        """Test case for initiatives_delete

        Delete an initiative.
        """
        response = self.client.open(
            '/api/v1/initiatives'.format(id='id_example'),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_initiatives_get(self):
        """Test case for initiatives_get

        List all smart subsidy initiatives
        """
        response = self.client.open(
            '/api/v1/initiatives',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_initiatives_post(self):
        """Test case for initiatives_post

        Create a new initiative; names must be unique.
        """
        body = Initiative()
        response = self.client.open(
            '/api/v1/initiatives',
            method='POST',
            data=json.dumps(body),
            content_type='application/nl.kpmg.v1.initiative+json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
