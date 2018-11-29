"""
Business logic for working with master accounts.
"""
import subsidy_service as service
import time

# Globals
CTX = service.config.Context

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
    master = service.utils.drop_nones(master.copy())

    if 'initiative' in master:
        existing = service.mongo.find({'name': master['initiative']}, CTX.db.initiatives)
        if existing is None:
            existing = service.mongo.find({'id': master['initiative']}, CTX.db.initiatives)
            if existing is None:
                raise service.exceptions.NotFoundException('Initiative not found; use an existing one or omit for default')

    if 'iban' in master:
        existing = service.mongo.find({'iban': master['iban']}, CTX.db.masters)

        if existing:
            msg = 'A Master-account with that iban already exists. '
            if 'id' in existing:
                id = existing['id']
                msg += f'The id is "{id}".'

            raise service.exceptions.AlreadyExistsException(msg)

        else:
            mast = service.bunq.read_account_by_iban(master['iban'])

    elif 'description' in master:
        mast = service.bunq.create_account(description=master['description'])
    else:
        mast = service.bunq.create_account()

    mast['bunq_id'] = mast.pop('id')
    mast = service.mongo.add_and_copy_id(mast, CTX.db.masters)
    mast['transactions'] = get_payments_if_available(mast['bunq_id'])

    return mast


def read(id):
    """
    Get a master by ID

    :param id: the master's ID
    :return: dict
    """
    # # Bunq get & update
    # master = get_and_update_balance(id)
    # master['transactions'] = get_payments_if_available(master['bunq_id'])
    master = service.mongo.get_by_id(id, CTX.db.masters)
    if master is None:
        raise service.exceptions.NotFoundException(
            f'Master Account with id {id} not found'
        )

    return master


def read_all(initiative: str=None):
    """
    Get all available masters

    :param id: the initiative to filter on
    :return: dict
    """
    masters = service.mongo.get_collection(CTX.db.masters)
    # output = []
    # for mast in masters:
    #     output.append(get_and_update_balance(mast['id']))
    #     time.sleep(1)
    if not masters:
        return []
    
    if initiative is None:
        # no initiative specified - return all initiatives
        filtered_masters = masters
    else:
        existing = service.mongo.find({'name': initiative}, CTX.db.initiatives)
        if existing is None:
            # initiative does not exist - return all initiatives
            filtered_masters = masters
        else:
            # initiative exists: we want to return only the masters:
            # - belonging to it explicitly thus those which show the requested initiative 
            # - not belonging to any initiative if this existing initiative is the default
            for master in masters:
                # master account has some initiative value explicitly set...
                if 'initiative' in master:
                    # but if it is not the requested one, we drop the value
                    if master['initiative'] is not initiative:
                        masters.remove(master)
                # if the master does not have an initiative name at all and the
                #requested initiative is not a default then we drop it too
                else:
                    if not existing['default']:
                        masters.remove(master)
            filtered_masters = masters
    for master in filtered_masters:
        if 'transactions' in master:
            master.pop('transactions')
    return filtered_masters

def update(id, master: dict):
    """
    Update a master's information.

    :param id: the master's id
    :param master: the fields to update. Nones will be ignored.
    :return: the updated master
    """
    raise service.exceptions.NotImplementedException('Not yet implemented')
    # document = service.utils.drop_nones(master)
    # obj = service.mongo.update_by_id(id, document, CTX.db.masters)
    # return obj


def replace(id, master: dict):
    """
    Replace a master in the database with the provided master, preserving ID.

    :param id: the master's id
    :param master: the new details
    :return: the new master's details
    """
    raise service.exceptions.NotImplementedException('Not yet implemented')
    # document = master
    # document['id'] = str(id)
    # obj = service.mongo.replace_by_id(id, document, CTX.db.masters)
    # return obj


def delete(id):
    """
    Delete a master from the database.

    :param id: the id of the master to delete.
    :return: None
    """
    # TODO: Do we want to close the acct in Bunq too?
    document = service.mongo.get_by_id(id, CTX.db.masters)
    if document is None:
        raise service.exceptions.NotFoundException('Master account not found')
    # service.bunq.close_account(id)
    service.mongo.delete_by_id(id, CTX.db.masters)
    return None


# utils
def get_and_update_balance(id):
    """
    Get the master from the db, update the balance from bunq, push the update
    to the db, and return the master account.

    If the master account can't be found (no access at bank level), None is
    returned and the db is not updated.

    :param id:
    :return:
    """
    master = service.mongo.get_by_id(id, CTX.db.masters)
    if master is None:
        raise service.exceptions.NotFoundException('Master-Account not found')

    try:
        master['balance'] = service.bunq.get_balance(master['bunq_id'])
        master = service.mongo.update_by_id(master['id'], master,
                                            CTX.db.masters)

    except service.exceptions.NotFoundException:
        master['balance'] = None

    return master


def get_payments_if_available(bunq_id):
    try:
        return service.bunq.get_payments(bunq_id)
    except service.exceptions.NotFoundException:
        return None

