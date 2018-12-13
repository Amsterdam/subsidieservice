import connexion
import six

from swagger_server.models.initiative import Initiative  # noqa: E501
from swagger_server import util

import subsidy_service as service

@service.exceptions.exceptionHTTPencode
@service.auth.authenticate()
def initiatives_delete(init_id):  # noqa: E501
    """Delete an initiative.

    Delete an initiative - this just removes the instance, no associated data e.g. master accounts are modified. Attention: when no initiative argument is provided to the endpoints, all entities of unknown or missing initiative (that is, the initiative field is null or it has an unkown value), are returned, so all data will always be accessible. But it is highly suggested to always keep consistency by not removing initiatives, and to always keep a default one. # noqa: E501

    :param id: 
    :type id: str

    :rtype: None
    """
    raise service.exceptions.NotImplementedException('Not yet implemented')

@service.exceptions.exceptionHTTPencode
@service.auth.authenticate()
def initiatives_get():  # noqa: E501
    """List all smart subsidy initiatives

    A subsidy initiative, like MaaS for example. One and exactly one of the instances is flagged as default: domain entities not carrying an initiative field of their own will be assumed to be under the default one; this is very important to maintain backwards compatibility. # noqa: E501


    :rtype: List[Initiative]
    """
    response = service.initiatives.read_all()
    output = [Initiative().from_dict(doc) for doc in response]
    return output

@service.exceptions.exceptionHTTPencode
@service.auth.authenticate()
def initiatives_post(body):  # noqa: E501
    """Create a new initiative; names must be unique.

     # noqa: E501

    :param body: The initiative to create
    :type body: dict | bytes

    :rtype: Initiative
    """
    if connexion.request.is_json:
        body = Initiative.from_dict(connexion.request.get_json())  # noqa: E501

    response = service.initiatives.create(body.to_dict())
    return Initiative.from_dict(response)
