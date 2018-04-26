import subsidy_service as service
import time
import collections

# Globals
CONF = service.utils.get_config()
CLIENT = service.mongo.get_client(CONF)
DB = CLIENT.subsidy

STATUS_OPTIONS = [
    # 'PENDING_APPROVAL',  # Not yet implemented
    # 'PENDING_START',  # Not yet implemented
    'PENDING_ACCOUNT',
    'PENDING_ACCEPT',
    'OPEN',
    'SHARE_CLOSED',
    'CLOSED',
]

STATUSCODE = collections.namedtuple(
    'subsidy_statuscode', STATUS_OPTIONS
)(*STATUS_OPTIONS)
# Usage:
#    >>> STATUSCODE.PENDING_ACCOUNT == 'PENDING_ACCOUNT'
#    True


# CRUD functionality
def create(subsidy: dict):
    """
    Create a new subsidy for a citizen. If the citizen is not yet in the
    database, they are added. A new bank account is created, the amount of the
    subsidy is transferred from the master to the subsidy account, and a
    connect invite is sent to the recipient.

    :param subsidy: Subsidy to create
    :return: The created subsidy
    """
    recip = service.utils.drop_nones(subsidy['recipient'])

    # check required DB objects
    master = service.utils.drop_nones(subsidy['master'])
    master = service.mongo.find(master, DB.masters)

    if master is None:
        raise service.exceptions.NotFoundException('Master account not found')

    if 'id' not in recip and 'phone_number' not in recip:
        raise service.exceptions.BadRequestException(
            'Please include recipient citizen\'s "id" or "phone_number"'
            + 'for unique identification.'
        )

    if 'id' in recip:
        recip = service.mongo.get_by_id(recip['id'], DB.citizens)
    else:
        recip = service.mongo.find({'phone_number': recip['phone_number']},
                                   DB.citizens)

    if recip is None:
        raise service.exceptions.NotFoundException(
            'Recipient citizen not found'
        )

    # recip = recip_full.copy()
    # recip.pop('subsidies')
    subsidy['recipient'] = recip
    if 'name' not in subsidy:
        subsidy['name'] = 'Subsidie Gemeente Amsterdam'

    # TODO: Move to actions/approve
    new_acct = service.bunq.create_account(description=subsidy['name'])
    new_acct['bunq_id'] = new_acct.pop('id')

    try:
        pmt = service.bunq.make_payment_to_iban(
            master['bunq_id'],
            new_acct['iban'],
            new_acct['name'],
            subsidy['amount'],
        )
    except Exception as e:
        # rollback
        time.sleep(1)
        service.bunq.close_account(new_acct['bunq_id'])
        raise e

    new_acct['balance'] = - float(pmt['amount'])
    master['balance'] = float(master['balance']) - float(pmt['amount'])

    try:
        time.sleep(1)
        new_share = service.bunq.create_share(new_acct['bunq_id'],
                                              recip['phone_number'])
        subsidy['status'] = STATUSCODE.PENDING_ACCEPT
    except:
        # couldn't create share
        subsidy['status'] = STATUSCODE.PENDING_ACCOUNT

    new_acct['transactions'] = service.bunq.get_payments(new_acct['bunq_id'])

    subsidy['account'] = new_acct
    subsidy['master'] = master

    # # REMOVED
    # # add subsidy to recipient's subsidies
    # if not recip_full['subsidies']:
    #     recip_full['subsidies'] = [subsidy]
    # else:
    #     recip_full['subsidies'].append(subsidy)
    #
    # service.mongo.update_by_id(recip_full['id'], recip_full, DB.citizens)

    output = service.mongo.add_and_copy_id(subsidy, DB.subsidies)

    return service.utils.drop_nones(output)


def read(id):
    """
    Get a subsidy by ID

    :param id: the subsidy's ID
    :return: dict
    """
    subsidy = get_and_update(id, master_balance=True)
    subsidy['account']['transactions'] = \
        service.bunq.get_payments(subsidy['account']['bunq_id'])
    return subsidy


def read_all(status: str=None):
    """
    Get all available subsidies. If a status is provided, return only
    those subsidies with the matching status.

    :return: list[dict]
    """

    if status and status not in STATUS_OPTIONS:
        raise service.exceptions.BadRequestException(
            'Status should be one of: {}.'.format(', '.join(STATUS_OPTIONS))
        )

    subsidies = service.mongo.get_collection(DB.subsidies)
    output = []
    if not subsidies:
        return output

    check_statuses = []
    if not status:
        check_statuses = [
            STATUSCODE.PENDING_ACCOUNT,
            STATUSCODE.PENDING_ACCEPT,
            STATUSCODE.OPEN,
            STATUSCODE.SHARE_CLOSED,
        ]

    elif status == STATUSCODE.PENDING_ACCOUNT:
        check_statuses = [STATUSCODE.PENDING_ACCOUNT]

    elif status == STATUSCODE.PENDING_ACCEPT:
        check_statuses = [
            STATUSCODE.PENDING_ACCOUNT,
            STATUSCODE.PENDING_ACCEPT
        ]

    elif status == STATUSCODE.OPEN:
        check_statuses = [STATUSCODE.PENDING_ACCEPT, STATUSCODE.OPEN]

    elif status == STATUSCODE.SHARE_CLOSED:
        check_statuses = [
            STATUSCODE.PENDING_ACCEPT,
            STATUSCODE.OPEN,
            STATUSCODE.SHARE_CLOSED
        ]

    elif status == STATUSCODE.CLOSED:
        check_statuses = [STATUSCODE.CLOSED]

    for sub in subsidies:
        if sub['status'] in check_statuses:
            sub_updated = get_and_update(sub['id'])
            if (sub_updated['status'] == status) or (not status):
                output.append(sub_updated)
            time.sleep(1)

    return output


def update(id, subsidy: dict):
    """
    Update a subsidy's information.

    :param id: the subsidy's id
    :param subsidy: the fields to update. Nones will be ignored.
    :return: the updated subsidy
    """
    raise service.exceptions.NotImplementedException('Not yet implemented')
    # document = service.utils.drop_nones(subsidy)
    # obj = service.mongo.update_by_id(id, document, DB.subsidies)
    # return obj


def replace(id, subsidy: dict):
    """
    Replace a subsidy in the database with the provided subsidy, preserving ID.

    :param id: the subsidy's id
    :param subsidy: the new details
    :return: the new subsidy's details
    """
    raise service.exceptions.NotImplementedException('Not yet implemented')
    # document = subsidy
    # document['id'] = str(id)
    # obj = service.mongo.replace_by_id(id, document, DB.subsidies)
    # return obj


def delete(id):
    """
    Remove a subsidy, revoking any related shares and closing related account.

    :param id: the id of the subsidy to delete.
    :return: None
    """
    subsidy = service.mongo.get_by_id(id, DB.subsidies)

    if subsidy is None:
        raise service.exceptions.NotFoundException('Subsidy not found')
    elif 'status' in subsidy:
        if subsidy['status'] == 'CLOSED':
            return None

    elif subsidy['status'] == STATUSCODE.CLOSED:
        raise service.exceptions.BadRequestException('Subsidy already closed')

    balance = float(service.bunq.get_balance(subsidy['account']['bunq_id']))

    if balance > 0:
        pmt = service.bunq.make_payment_to_acct_id(
            subsidy['account']['bunq_id'],
            subsidy['master']['bunq_id'],
            balance
        )
    time.sleep(1)
    service.bunq.close_account(subsidy['account']['bunq_id'])
    subsidy['status'] = STATUSCODE.CLOSED
    subsidy['account']['balance'] = 0.
    subsidy['master']['balance'] = None
    subsidy = service.mongo.update_by_id(id, subsidy, DB.subsidies)

    return None


def approve(id):
    """
    Approve a subsidy.

    :param id: int
    :return:
    """
    raise service.exceptions.NotImplementedException(
        'Subsidy approval not yet implemented'
    )

# # utilities
# def update_accounts():
#     accts = service.bunq.list_accounts(include_closed=True)
#     for acct in accts:
#         acct_db = acct.copy()
#         acct_db['bunq_id'] = acct_db.pop('id')
#         service.mongo.upsert(acct_db, DB.accounts, ['iban'])
#
#     accts_db = service.mongo.get_collection(DB.accounts)
#
#     return accts_db


# utils
def get_and_update(id, master_balance=False):
    """
    Get the subsidy from the DB, update the balance from bunq, update the status
    as appropriate, push the updates to the server, and return the subsidy.

    If the account is not accessible, a balance of None is reported and the DB
    is not updated.

    :param id:
    :param master_balance: Get the most recent balance of the master (else
        do not return the balance of the master).
    :return:
    """
    # TODO: Do we even want to store balances?
    sub = service.mongo.get_by_id(id, DB.subsidies)

    if sub is None:
        raise service.exceptions.NotFoundException('Subsidy not found')

    # temporarily removed for performance
    # sub['account']['balance'] = \
    #     service.bunq.get_balance(sub['account']['bunq_id'])
    # time.sleep(1)

    # only need shares for PENDING_ACCEPT and OPEN subsidies
    full_read = (sub['status'] in [STATUSCODE.PENDING_ACCEPT, STATUSCODE.OPEN])
    acct = {}
    if sub['status'] != STATUSCODE.CLOSED:
        acct = service.bunq.read_account(sub['account']['bunq_id'], full_read)
        sub['account']['balance'] = acct['balance']

    if master_balance:
        sub['master']['balance'] = \
            service.bunq.get_balance(sub['master']['bunq_id'])
    else:
        sub['master']['balance'] = None

    if sub['status'] == STATUSCODE.PENDING_ACCOUNT:
        # TODO: Should we trigger this action at this point? Or in a script?
        # try:
        #     service.bunq.create_share(sub['account']['bunq_id'],
        #                               sub['recipient']['phone_number'])
        #     sub['status'] = 'PENDING_ACCEPT'
        # except service.exceptions.NotFoundException:
        #     pass
        pass

    elif sub['status'] in [STATUSCODE.PENDING_ACCEPT, STATUSCODE.OPEN]:
        if 'shares' in acct:
            if len(acct['shares']) > 0:
                share_status = acct['shares'][0]['status']

                if share_status == 'ACCEPTED':
                    sub['status'] = STATUSCODE.OPEN
                elif share_status in ['CANCELLED', 'REVOKED', 'REJECTED']:
                    sub['status'] = STATUSCODE.SHARE_CLOSED

    sub = service.mongo.update_by_id(sub['id'], sub, DB.subsidies)

    return sub

