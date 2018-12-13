import connexion
import six

from swagger_server.models.citizen import Citizen  # noqa: E501
from swagger_server.models.citizen_base import CitizenBase  # noqa: E501
from swagger_server import util

import subsidy_service as service


@service.exceptions.exceptionHTTPencode
@service.auth.authenticate()
def citizens_get():  # noqa: E501
    """List all citizens.

    Lists all known information about every citizen in the database. # noqa: E501


    :rtype: List[CitizenBase]
    """
    response = service.citizens.read_all()
    output = [CitizenBase().from_dict(doc) for doc in response]
    return output


@service.exceptions.exceptionHTTPencode
@service.auth.authenticate()
def citizens_id_delete(id):  # noqa: E501
    """Remove a citizen

    Remove a citizen form the subsidy service database. The citizen should not have any active subsidies. If there are any active subsidies, this call will respond with 400 and
the citizen will not be deleted. # noqa: E501

    :param id: 
    :type id: str

    :rtype: None
    """
    service.citizens.delete(id)
    return None


@service.exceptions.exceptionHTTPencode
@service.auth.authenticate()
def citizens_id_get(id):  # noqa: E501
    """Returns a specific citizen

    Get the information for a single citizen Currently no additional information is available compared to the list view. # noqa: E501

    :param id: 
    :type id: str

    :rtype: Citizen
    """
    response = service.citizens.read(id)
    return Citizen.from_dict(response)


@service.exceptions.exceptionHTTPencode
@service.auth.authenticate()
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


@service.exceptions.exceptionHTTPencode
@service.auth.authenticate()
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


@service.exceptions.exceptionHTTPencode
@service.auth.authenticate()
def citizens_post(body):  # noqa: E501
    """Create a new citizen

    A new citizen will be created in the database and assigned a unique id. The &#x60;name&#x60; and &#x60;phone_number&#x60; are required to make use of the subsidy service. The &#x60;phone_number&#x60; must be unique per citizen. # noqa: E501

    :param body: citizen to add
    :type body: dict | bytes

    :rtype: Citizen
    """
    if connexion.request.is_json:
        body = Citizen.from_dict(connexion.request.get_json())  # noqa: E501

    response = service.citizens.create(body.to_dict())
    return Citizen.from_dict(response)
