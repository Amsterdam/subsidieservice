# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.subsidy import Subsidy  # noqa: E501
from swagger_server.models.subsidy_base import SubsidyBase  # noqa: E501
from swagger_server.models.user import User  # noqa: E501
from swagger_server.test import BaseTestCase


class TestSubsidiesController(BaseTestCase):
    """SubsidiesController integration test stubs"""

    def test_subsidies_get(self):
        """Test case for subsidies_get

        List all subsidies
        """
        query_string = [('status', 'status_example')]
        response = self.client.open(
            '/api/v1/subsidies',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_subsidies_id_actions_approve_post(self):
        """Test case for subsidies_id_actions_approve_post

        Approve a subsidy
        """
        body = User()
        response = self.client.open(
            '/api/v1/subsidies/{id}/actions/approve'.format(id='id_example'),
            method='POST',
            data=json.dumps(body),
            content_type='application/nl.kpmg.v1.user+json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_subsidies_id_delete(self):
        """Test case for subsidies_id_delete

        Close a subsidy
        """
        response = self.client.open(
            '/api/v1/subsidies/{id}'.format(id='id_example'),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_subsidies_id_get(self):
        """Test case for subsidies_id_get

        Returns a specific subsidy
        """
        response = self.client.open(
            '/api/v1/subsidies/{id}'.format(id='id_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_subsidies_id_patch(self):
        """Test case for subsidies_id_patch

        Edit a subsidy's information
        """
        body = SubsidyBase()
        response = self.client.open(
            '/api/v1/subsidies/{id}'.format(id='id_example'),
            method='PATCH',
            data=json.dumps(body),
            content_type='application/nl.kpmg.v1.subsidy+json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_subsidies_id_put(self):
        """Test case for subsidies_id_put

        Re-upload a subsidy's information
        """
        body = SubsidyBase()
        response = self.client.open(
            '/api/v1/subsidies/{id}'.format(id='id_example'),
            method='PUT',
            data=json.dumps(body),
            content_type='application/nl.kpmg.v1.subsidy+json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_subsidies_post(self):
        """Test case for subsidies_post

        Create a new subsidy
        """
        body = SubsidyBase()
        response = self.client.open(
            '/api/v1/subsidies',
            method='POST',
            data=json.dumps(body),
            content_type='application/nl.kpmg.v1.subsidy-base+json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_subsidies_payments_post(self):
        """Test case for subsidies_payments_post

        Perform a one-off payment transfering a desired amount to the subsidy from the associated master account.
        """
        body = Payment()
        response = self.client.open(
            '/api/v1/subsidies/payments',
            method='POST',
            data=json.dumps(body),
            content_type='application/nl.kpmg.v1.payment+json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

if __name__ == '__main__':
    import unittest
    unittest.main()
