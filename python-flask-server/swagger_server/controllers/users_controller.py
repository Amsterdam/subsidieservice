import connexion
import six

from swagger_server.models.user import User  # noqa: E501
from swagger_server import util


def users_get():  # noqa: E501
    """Returns a list of users.

     # noqa: E501


    :rtype: List[User]
    """
    return 'do some magic!'


def users_post(body):  # noqa: E501
    """Create a new user

     # noqa: E501

    :param body: user to add
    :type body: dict | bytes

    :rtype: User
    """
    if connexion.request.is_json:
        body = User.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def users_username_delete(username):  # noqa: E501
    """Remove a user

     # noqa: E501

    :param username: 
    :type username: str

    :rtype: None
    """
    return 'do some magic!'


def users_username_get(username):  # noqa: E501
    """Returns a specific user

     # noqa: E501

    :param username: 
    :type username: str

    :rtype: User
    """
    return 'do some magic!'


def users_username_patch(username, body):  # noqa: E501
    """Edit a user&#39;s information

     # noqa: E501

    :param username: 
    :type username: str
    :param body: user properties to be updated
    :type body: dict | bytes

    :rtype: User
    """
    if connexion.request.is_json:
        body = User.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def users_username_put(username, body):  # noqa: E501
    """Re-upload user&#39;s information

     # noqa: E501

    :param username: 
    :type username: str
    :param body: user details
    :type body: dict | bytes

    :rtype: User
    """
    if connexion.request.is_json:
        body = User.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
