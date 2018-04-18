import connexion
import six

from swagger_server.models.master_account import MasterAccount  # noqa: E501
from swagger_server.models.master_account_base import MasterAccountBase  # noqa: E501
from swagger_server import util

import subsidy_service as service

@service.auth.authenticate
def master_accounts_get():  # noqa: E501
    """Returns a list of master-accounts.

     # noqa: E501


    :rtype: List[MasterAccountBase]
    """
    response = service.masters.read_all()
    output = [MasterAccountBase().from_dict(doc) for doc in response]
    return output


@service.auth.authenticate
def master_accounts_id_delete(id):  # noqa: E501
    """Remove a master-account

     # noqa: E501

    :param id: 
    :type id: str

    :rtype: None
    """
    service.masters.delete(id)
    return None


@service.auth.authenticate
def master_accounts_id_get(id):  # noqa: E501
    """Returns a specific master-account

     # noqa: E501

    :param id: 
    :type id: str

    :rtype: MasterAccount
    """
    response = service.masters.read(id)
    return MasterAccount.from_dict(response)


@service.auth.authenticate
def master_accounts_id_patch(id, body):  # noqa: E501
    """Edit a master-account&#39;s information

     # noqa: E501

    :param id: 
    :type id: str
    :param body: master-account properties to be updated
    :type body: dict | bytes

    :rtype: MasterAccount
    """
    if connexion.request.is_json:
        body = MasterAccount.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
    # response = service.masters.update(id, body.to_dict())
    # return MasterAccount.from_dict(response)



@service.auth.authenticate
def master_accounts_id_put(id, body):  # noqa: E501
    """Re-upload a master-account&#39;s information

     # noqa: E501

    :param id: 
    :type id: str
    :param body: master-account details
    :type body: dict | bytes

    :rtype: MasterAccount
    """
    if connexion.request.is_json:
        body = MasterAccount.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
    # response = service.masters.replace(id, body.to_dict())
    # return MasterAccount.from_dict(response)


@service.auth.authenticate
def master_accounts_post(body):  # noqa: E501
    """Create a new master-account

     # noqa: E501

    :param body: master-account to add
    :type body: dict | bytes

    :rtype: MasterAccount
    """
    if connexion.request.is_json:
        body = MasterAccountBase.from_dict(connexion.request.get_json())  # noqa: E501

    response = service.masters.create(body.to_dict())
    return MasterAccount.from_dict(response)
