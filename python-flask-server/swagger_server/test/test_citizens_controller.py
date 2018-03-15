# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.citizen import Citizen  # noqa: E501
from swagger_server.models.citizen_base import CitizenBase  # noqa: E501
from swagger_server.test import BaseTestCase


class TestCitizensController(BaseTestCase):
    """CitizensController integration test stubs"""

    def test_citizens_get(self):
        """Test case for citizens_get

        Returns a list of citizens.
        """
        response = self.client.open(
            '/v1/citizens',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_citizens_id_delete(self):
        """Test case for citizens_id_delete

        Remove a citizen
        """
        response = self.client.open(
            '/v1/citizens/{id}'.format(id=56),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_citizens_id_get(self):
        """Test case for citizens_id_get

        Returns a specific citizen
        """
        response = self.client.open(
            '/v1/citizens/{id}'.format(id=56),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_citizens_id_patch(self):
        """Test case for citizens_id_patch

        Edit a citizen's information
        """
        body = Citizen()
        response = self.client.open(
            '/v1/citizens/{id}'.format(id=56),
            method='PATCH',
            data=json.dumps(body),
            content_type='application/nl.kpmg.v1.citizen+json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_citizens_id_put(self):
        """Test case for citizens_id_put

        Re-upload a citizen's information
        """
        body = Citizen()
        response = self.client.open(
            '/v1/citizens/{id}'.format(id=56),
            method='PUT',
            data=json.dumps(body),
            content_type='application/nl.kpmg.v1.citizen+json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_citizens_post(self):
        """Test case for citizens_post

        Create a new citizen
        """
        body = Citizen()
        response = self.client.open(
            '/v1/citizens',
            method='POST',
            data=json.dumps(body),
            content_type='application/nl.kpmg.v1.citizen+json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
