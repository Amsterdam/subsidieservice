# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.subsidy import Subsidy  # noqa: E501
from swagger_server.models.user import User  # noqa: E501
from swagger_server.test import BaseTestCase


class TestActionsController(BaseTestCase):
    """ActionsController integration test stubs"""

    def test_subsidies_id_actions_approve_post(self):
        """Test case for subsidies_id_actions_approve_post

        Approve a subsidy
        """
        body = User()
        response = self.client.open(
            '/v1/subsidies/{id}/actions/approve'.format(id='id_example'),
            method='POST',
            data=json.dumps(body),
            content_type='application/nl.kpmg.v1.user+json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
