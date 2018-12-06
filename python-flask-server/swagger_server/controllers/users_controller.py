import connexion
import six

from swagger_server.models.user import User  # noqa: E501
from swagger_server import util

import subsidy_service as service

@service.exceptions.exceptionHTTPencode
@service.auth.authenticate(as_admin=True)
def users_get():  # noqa: E501
    """List all API users created by the administrator. One of the users is flagged as the administrator; that is the very first user created and may not be deleted.

     # noqa: E501


    :rtype: List[User]
    """
    response = service.users.read_all()
    output = [User().from_dict(doc) for doc in response]
    return output

@service.exceptions.exceptionHTTPencode
@service.auth.authenticate(as_admin=True)
def users_id_delete(id):  # noqa: E501
    """Delete a user. The administrator user may not be deleted.

     # noqa: E501

    :param id: 
    :type id: str

    :rtype: None
    """
    service.users.delete(id)
    return None

@service.exceptions.exceptionHTTPencode
@service.auth.authenticate(as_admin=True)
def users_id_patch(id, body):  # noqa: E501
    """Edit a user&#39;s information; at the moment of writing, its pass.

     # noqa: E501

    :param id: 
    :type id: str
    :param body: user properties to be updated; at the moment of writing, its pass.
    :type body: dict | bytes

    :rtype: User
    """
    if connexion.request.is_json:
        body = User.from_dict(connexion.request.get_json())  # noqa: E501
    response = service.users.update(id, body.to_dict())
    return User.from_dict(response) 

@service.exceptions.exceptionHTTPencode
@service.auth.authenticate(as_admin=True)
def users_post(body):  # noqa: E501
    """Create a new user.

     # noqa: E501

    :param body: The user to create
    :type body: dict | bytes

    :rtype: User
    """
    if connexion.request.is_json:
        body = User.from_dict(connexion.request.get_json())  # noqa: E501
    response = service.users.create(body.to_dict())
    return User.from_dict(response)
