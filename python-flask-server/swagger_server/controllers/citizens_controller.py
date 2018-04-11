import connexion
import six

from swagger_server.models.citizen import Citizen  # noqa: E501
from swagger_server.models.citizen_base import CitizenBase  # noqa: E501
from swagger_server import util

import subsidy_service as service


@service.auth.authenticate
def citizens_get():  # noqa: E501
    """Returns a list of citizens.

     # noqa: E501


    :rtype: List[CitizenBase]
    """
    response = service.citizens.read_all()
    output = [CitizenBase().from_dict(doc) for doc in response]
    return output


@service.auth.authenticate
def citizens_id_delete(id):  # noqa: E501
    """Remove a citizen

     # noqa: E501

    :param id: 
    :type id: str

    :rtype: None
    """
    service.citizens.delete(id)
    return None


@service.auth.authenticate
def citizens_id_get(id):  # noqa: E501
    """Returns a specific citizen

     # noqa: E501

    :param id: 
    :type id: str

    :rtype: Citizen
    """
    response = service.citizens.read(id)
    return Citizen.from_dict(response)


@service.auth.authenticate
def citizens_id_patch(id, body):  # noqa: E501
    """Edit a citizen&#39;s information

     # noqa: E501

    :param id: 
    :type id: str
    :param body: citizen properties to be updated
    :type body: dict | bytes

    :rtype: Citizen
    """
    if connexion.request.is_json:
        body = Citizen.from_dict(connexion.request.get_json())  # noqa: E501

    response = service.citizens.update(id, body.to_dict())
    return Citizen.from_dict(response)


@service.auth.authenticate
def citizens_id_put(id, body):  # noqa: E501
    """Re-upload a citizen&#39;s information

     # noqa: E501

    :param id: 
    :type id: str
    :param body: citizen details
    :type body: dict | bytes

    :rtype: Citizen
    """
    if connexion.request.is_json:
        body = Citizen.from_dict(connexion.request.get_json())  # noqa: E501

    response = service.citizens.replace(id, body.to_dict())
    return Citizen.from_dict(response)


@service.auth.authenticate
def citizens_post(body):  # noqa: E501
    """Create a new citizen

     # noqa: E501

    :param body: citizen to add
    :type body: dict | bytes

    :rtype: Citizen
    """
    if connexion.request.is_json:
        body = Citizen.from_dict(connexion.request.get_json())  # noqa: E501

    response = service.citizens.create(body.to_dict())
    return Citizen.from_dict(response)
