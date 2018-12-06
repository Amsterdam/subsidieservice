import connexion
import six

from swagger_server.models.user import User  # noqa: E501
from swagger_server import util

import subsidy_service as service

@service.exceptions.exceptionHTTPencode
def login_post(body):  # noqa: E501
    """Login a user; this a virtual endpoint to just confirm the user exists. Also important to see whether a user is an admin or not.

     # noqa: E501

    :param body: The user to login
    :type body: dict | bytes

    :rtype: User
    """
    if connexion.request.is_json:
        body = User.from_dict(connexion.request.get_json())  # noqa: E501
    user = body.to_dict()
    if 'username' not in user or 'password' not in user:
        raise service.exceptions.BadRequestException('Please provide both username and password to login')
    if service.users.authenticate(user['username'], user['password']):
        response = service.users.get(user['username'])
        return User.from_dict(response)
    else:
        raise service.exceptions.ForbiddenException("Username/password incorrect")
