"""
Business logic for working with master accounts.
"""
import subsidy_service as service
import time

# Globals
CONF = service.utils.get_config()
CLIENT = service.mongo.get_client(CONF)
DB = CLIENT.subsidy


# CRUD functionality
def create(master: dict):
    """
    Create a new master. If an iban of an existing account is specified, this
    account is used. Otherwise, a new account will be created and assigned to
    this master.

    :param master: The master to be added
    :type master: dict
    :return: dict: the created object
    """
    if 'iban' in master:
        existing = service.mongo.find({'iban':master['iban']}, DB.masters)

        if existing is not None:
            existing['transactions'] = \
                get_payments_if_available(existing['bunq_id'])
            return existing
        else:
            mast = service.bunq.read_account_by_iban(master['iban'])

    elif 'description' in master:
        mast = service.bunq.create_account(description=master['description'])
    else:
        mast = service.bunq.create_account()

    mast['bunq_id'] = mast.pop('id')
    mast = service.mongo.add_and_copy_id(mast, DB.masters)
    mast['transactions'] = get_payments_if_available(mast['bunq_id'])

    return mast


def read(id):
    """
    Get a master by ID

    :param id: the master's ID
    :return: dict
    """
    master = get_and_update_balance(id)
    master['transactions'] = get_payments_if_available(master['bunq_id'])
    return master


def read_all():
    """
    Get all available masters

    :return: dict
    """
    masters = service.mongo.get_collection(DB.masters)
    output = []
    for mast in masters:
        output.append(get_and_update_balance(mast['id']))
        time.sleep(1)
    return masters


def update(id, master: dict):
    """
    Update a master's information.

    :param id: the master's id
    :param master: the fields to update. Nones will be ignored.
    :return: the updated master
    """
    raise service.exceptions.NotImplementedException('Not yet implemented')
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
    raise service.exceptions.NotImplementedException('Not yet implemented')
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

    If the master account can't be found (no access at bank level), None is
    returned and the db is not updated.

    :param id:
    :return:
    """
    master = service.mongo.get_by_id(id, DB.masters)
    try:
        master['balance'] = service.bunq.get_balance(master['bunq_id'])
        master = service.mongo.update_by_id(master['id'], master, DB.masters)

    except service.exceptions.NotFoundException:
        master['balance'] = None

    return master


def get_payments_if_available(bunq_id):
    try:
        return service.bunq.get_payments(bunq_id)
    except service.exceptions.NotFoundException:
        return None

