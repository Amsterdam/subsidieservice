import connexion
import six

from swagger_server.models.master_account import MasterAccount  # noqa: E501
from swagger_server.models.master_account_base import MasterAccountBase  # noqa: E501
from swagger_server import util

import subsidy_service as service


@service.exceptions.exceptionHTTPencode
@service.auth.authenticate()
def master_accounts_get(initiative=None):  # noqa: E501
    """List all master-accounts.

    Returns an overview list of master-accounts. These do not contain the transactions, to get transactions these please see &#x60;GET /master-accounts/{id}&#x60;. The &#x60;last_updated&#x60; property reflects the last time this entry was refreshed in the database, this is updated automatically. # noqa: E501


    :rtype: List[MasterAccountBase]
    """
    response = service.masters.read_all(initiative)
    output = [MasterAccountBase().from_dict(doc) for doc in response]
    return output


@service.exceptions.exceptionHTTPencode
@service.auth.authenticate()
def master_accounts_id_delete(id):  # noqa: E501
    """Remove a master-account

    Delete a master-account from the database. Note that this does **NOT** delete the account on the bank&#39;s end, it only removes it from the subsidy service system. The master account does not need to have zero balance. If the account itself is to be deleted, please also do this using the banking interface directly. # noqa: E501

    :param id: 
    :type id: str

    :rtype: None
    """
    service.masters.delete(id)
    return None


@service.exceptions.exceptionHTTPencode
@service.auth.authenticate()
def master_accounts_id_get(id):  # noqa: E501
    """Get the details of a specific master-account

    The detailed view of a master-account includes the list of transactions to and from that master-account. The &#x60;id&#x60; should correspond to one of the &#x60;id&#x60;s listed by &#x60;GET /master-accounts&#x60; or the call will return a 404. # noqa: E501

    :param id: 
    :type id: str

    :rtype: MasterAccount
    """
    response = service.masters.read(id)
    return MasterAccount.from_dict(response)


@service.exceptions.exceptionHTTPencode
@service.auth.authenticate()
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
    raise service.exceptions.NotImplementedException('Not yet implemented')
    # response = service.masters.update(id, body.to_dict())
    # return MasterAccount.from_dict(response)


@service.exceptions.exceptionHTTPencode
@service.auth.authenticate()
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
    raise service.exceptions.NotImplementedException('Not yet implemented')
    # response = service.masters.replace(id, body.to_dict())
    # return MasterAccount.from_dict(response)


@service.exceptions.exceptionHTTPencode
@service.auth.authenticate()
def master_accounts_post(body):  # noqa: E501
    """Create a new master-account

    A new master-account will be created in the system and assigned a unique id. If &#x60;iban&#x60; is provided, an account with that IBAN is assumed to exist in the linked bank profile, and this one will be added to the database for caching. If no &#x60;iban&#x60; is provided, a new bank account will be opened under the name of the linked account. The details of the new or existing account are returned. # noqa: E501

    :param body: master-account to add
    :type body: dict | bytes

    :rtype: MasterAccount
    """
    if connexion.request.is_json:
        body = MasterAccountBase.from_dict(connexion.request.get_json())  # noqa: E501

    response = service.masters.create(body.to_dict())
    return MasterAccount.from_dict(response)
