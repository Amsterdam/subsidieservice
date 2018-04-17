"""
Business logic for working with master accounts.
"""
import subsidy_service as service

# Globals
CONF = service.utils.get_config()
CLIENT = service.mongo.get_client(CONF)
DB = CLIENT.subsidy

# CRUD functionality
def create(master: dict):
    """
    Create a new master.

    :param master: The master to be added
    :type master: dict
    :return: dict: the created object
    """

    if 'iban' in master:
        mast = service.bunq.read_account_by_iban(master['iban'])
    elif 'description' in master:
        mast = service.bunq.create_account(description=master['description'])
    else:
        mast = service.bunq.create_account(description=master['description'])

    mast['bunq_id'] = mast.pop('id')
    mast = service.mongo.add_and_copy_id(mast, DB.masters)
    mast['transactions'] = service.bunq.get_payments(mast['bunq_id'])

    return mast


def read(id):
    """
    Get a master by ID

    :param id: the master's ID
    :return: dict
    """
    master = get_and_update_balance(id)
    master['transactions'] = service.bunq.get_payments(master['bunq_id'])
    return master


def read_all():
    """
    Get all available masters

    :return: dict
    """
    masters = service.mongo.get_collection(DB.masters)
    output = [get_and_update_balance(mast['id']) for mast in masters]
    return masters


def update(id, master: dict):
    """
    Update a master's information.

    :param id: the master's id
    :param master: the fields to update. Nones will be ignored.
    :return: the updated master
    """
    document = service.utils.drop_nones(master)
    obj = service.mongo.update_by_id(id, document, DB.masters)
    return obj


def replace(id, master: dict):
    """
    Replace a master in the database with the provided master, preserving ID.

    :param id: the master's id
    :param master: the new details
    :return: the new master's details
    """
    document = master
    document['id'] = str(id)
    obj = service.mongo.replace_by_id(id, document, DB.masters)
    return obj


def delete(id):
    """
    Delete a master from the database.

    :param id: the id of the master to delete.
    :return: None
    """
    # TODO: Do we want to close the acct in Bunq too?
    # service.bunq.close_account(id)
    service.mongo.delete_by_id(id, DB.masters)
    return None


# utils
def get_and_update_balance(id):
    """
    Get the master from the DB, update the balance from bunq, push the update
    to the DB, and return the master account.

    :param id:
    :return:
    """
    master = service.mongo.get_by_id(id, DB.masters)
    master['balance'] = service.bunq.get_balance(master['bunq_id'])
    master = service.mongo.update_by_id(master['id'], master, DB.masters)
    return master
