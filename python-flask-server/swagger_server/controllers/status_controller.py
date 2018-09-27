import connexion
import six

from swagger_server.models.endpoint_status import EndpointStatus  # noqa: E501
from swagger_server.models.service_status import ServiceStatus  # noqa: E501
from swagger_server import util


def status_endpoints_get():  # noqa: E501
    """Returns the status of the REST API endpoints.

    An entry is returned for each endpoint. This is a conventional endpoint for internal usage and it may be exposed to application clients. # noqa: E501


    :rtype: List[EndpointStatus]
    """
    return 'do some magic!'


def status_services_get():  # noqa: E501
    """Returns the status of the backend services (e.g. Mongo).

    An entry is returned for each service. This is a conventional endpoint for internal usage and it should not be exposed to application clients. # noqa: E501


    :rtype: List[ServiceStatus]
    """
    return 'do some magic!'
