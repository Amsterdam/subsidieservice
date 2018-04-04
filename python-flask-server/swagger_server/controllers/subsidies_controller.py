import connexion
import six

from swagger_server.models.subsidy import Subsidy  # noqa: E501
from swagger_server.models.subsidy_base import SubsidyBase  # noqa: E501
from swagger_server.models.user import User  # noqa: E501
from swagger_server import util

import subsidy_service as service


def subsidies_get():  # noqa: E501
    """Returns a list of subsidies.

     # noqa: E501


    :rtype: List[SubsidyBase]
    """
    response = service.subsidies.read_all()
    output = [SubsidyBase().from_dict(doc) for doc in response]
    return output


def subsidies_id_actions_approve_post(id, body):  # noqa: E501
    """Approve a subsidy

     # noqa: E501

    :param id: 
    :type id: str
    :param body: user approving subsidy
    :type body: dict | bytes

    :rtype: Subsidy
    """
    if connexion.request.is_json:
        body = User.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def subsidies_id_delete(id):  # noqa: E501
    """Remove a subsidy

     # noqa: E501

    :param id: 
    :type id: str

    :rtype: None
    """
    return 'do some magic!'


def subsidies_id_get(id):  # noqa: E501
    """Returns a specific subsidy

     # noqa: E501

    :param id: 
    :type id: str

    :rtype: Subsidy
    """
    response = service.subsidies.read(id)
    return Subsidy.from_dict(response)


def subsidies_id_patch(id, body):  # noqa: E501
    """Edit a subsidy&#39;s information

     # noqa: E501

    :param id: 
    :type id: str
    :param body: subsidy properties to be updated
    :type body: dict | bytes

    :rtype: Subsidy
    """
    if connexion.request.is_json:
        body = SubsidyBase.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def subsidies_id_put(id, body):  # noqa: E501
    """Re-upload a subsidy&#39;s information

     # noqa: E501

    :param id: 
    :type id: str
    :param body: subsidy details
    :type body: dict | bytes

    :rtype: Subsidy
    """
    if connexion.request.is_json:
        body = SubsidyBase.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def subsidies_post(body):  # noqa: E501
    """Create a new subsidy

     # noqa: E501

    :param body: subsidy to add
    :type body: dict | bytes

    :rtype: Subsidy
    """
    if connexion.request.is_json:
        body = SubsidyBase.from_dict(connexion.request.get_json())  # noqa: E501

    response = service.subsidies.create(body.to_dict())
    return Subsidy.from_dict(response)
