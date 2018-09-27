# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.endpoint_status import EndpointStatus  # noqa: E501
from swagger_server.models.service_status import ServiceStatus  # noqa: E501
from swagger_server.test import BaseTestCase


class TestStatusController(BaseTestCase):
    """StatusController integration test stubs"""

    def test_status_endpoints_get(self):
        """Test case for status_endpoints_get

        Returns the status of the REST API endpoints.
        """
        response = self.client.open(
            '/v1/status/endpoints',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_status_services_get(self):
        """Test case for status_services_get

        Returns the status of the backend services (e.g. Mongo).
        """
        response = self.client.open(
            '/v1/status/services',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
