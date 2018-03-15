import connexion
import six

from swagger_server.models.master_account import MasterAccount  # noqa: E501
from swagger_server import util


def master_accounts_get():  # noqa: E501
    """Returns a list of master-accounts.

     # noqa: E501


    :rtype: List[MasterAccount]
    """
    return 'do some magic!'


def master_accounts_id_delete(id):  # noqa: E501
    """Remove a master-account

     # noqa: E501

    :param id: 
    :type id: int

    :rtype: None
    """
    return 'do some magic!'


def master_accounts_id_get(id):  # noqa: E501
    """Returns a specific master-account

     # noqa: E501

    :param id: 
    :type id: int

    :rtype: MasterAccount
    """
    return 'do some magic!'


def master_accounts_id_patch(id, body):  # noqa: E501
    """Edit a master-account&#39;s information

     # noqa: E501

    :param id: 
    :type id: int
    :param body: master-account properties to be updated
    :type body: dict | bytes

    :rtype: MasterAccount
    """
    if connexion.request.is_json:
        body = MasterAccount.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def master_accounts_id_put(id, body):  # noqa: E501
    """Re-upload a master-account&#39;s information

     # noqa: E501

    :param id: 
    :type id: int
    :param body: master-account details
    :type body: dict | bytes

    :rtype: MasterAccount
    """
    if connexion.request.is_json:
        body = MasterAccount.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def master_accounts_post(body):  # noqa: E501
    """Create a new master-account

     # noqa: E501

    :param body: master-account to add
    :type body: dict | bytes

    :rtype: MasterAccount
    """
    if connexion.request.is_json:
        body = MasterAccount.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
