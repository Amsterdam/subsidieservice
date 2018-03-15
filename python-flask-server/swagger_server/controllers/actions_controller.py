import connexion
import six

from swagger_server.models.subsidy import Subsidy  # noqa: E501
from swagger_server.models.user import User  # noqa: E501
from swagger_server import util


def subsidies_id_actions_approve_post(id, body):  # noqa: E501
    """Approve a subsidy

     # noqa: E501

    :param id: 
    :type id: int
    :param body: user approving subsidy
    :type body: dict | bytes

    :rtype: Subsidy
    """
    if connexion.request.is_json:
        body = User.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
