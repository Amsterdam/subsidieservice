import connexion
import six

from swagger_server.models.citizen import Citizen  # noqa: E501
from swagger_server.models.citizen_base import CitizenBase  # noqa: E501
from swagger_server import util

import subsidy_service as service

def citizens_get():  # noqa: E501
    """Returns a list of citizens.

     # noqa: E501


    :rtype: List[CitizenBase]
    """
    return 'do some magic!'


def citizens_id_delete(id):  # noqa: E501
    """Remove a citizen

     # noqa: E501

    :param id: 
    :type id: int

    :rtype: None
    """
    return 'do some magic!'


def citizens_id_get(id):  # noqa: E501
    """Returns a specific citizen

     # noqa: E501

    :param id: 
    :type id: int

    :rtype: Citizen
    """
    return 'do some magic!'


def citizens_id_patch(id, body):  # noqa: E501
    """Edit a citizen&#39;s information

     # noqa: E501

    :param id: 
    :type id: int
    :param body: citizen properties to be updated
    :type body: dict | bytes

    :rtype: Citizen
    """
    if connexion.request.is_json:
        body = Citizen.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def citizens_id_put(id, body):  # noqa: E501
    """Re-upload a citizen&#39;s information

     # noqa: E501

    :param id: 
    :type id: int
    :param body: citizen details
    :type body: dict | bytes

    :rtype: Citizen
    """
    if connexion.request.is_json:
        body = Citizen.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def citizens_post(body):  # noqa: E501
    """Create a new citizen

     # noqa: E501

    :param body: citizen to add
    :type body: dict | bytes

    :rtype: Citizen
    """
    if connexion.request.is_json:
        body = Citizen.from_dict(connexion.request.get_json())  # noqa: E501

    obj = service.citizens.add(body.to_dict())

    return obj
