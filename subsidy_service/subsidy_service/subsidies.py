import subsidy_service as service
import time
import datetime
import collections
from dateutil.parser import parse

# Globals
CTX = service.config.Context


STATUS_OPTIONS = [
    # 'PENDING_APPROVAL',  # Not yet implemented
    # 'PENDING_START',  # Not yet implemented
    'PENDING_ACCOUNT',
    'PENDING_ACCEPT',
    'OPEN',
    'SHARE_CLOSED',
    'CLOSED',
    'UNKNOWN',
    'ALL'  # for filtering
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

    # check required CTX.db objects
    master = service.utils.drop_nones(subsidy['master'])
    master = service.mongo.find(master, CTX.db.masters)

    if master is None:
        raise service.exceptions.NotFoundException('Master account not found')

    if 'id' not in recip and 'phone_number' not in recip:
        raise service.exceptions.BadRequestException(
            'Please include recipient citizen\'s "id" or "phone_number"'
            + 'for unique identification.'
        )

    if 'id' in recip:
        recip = service.mongo.get_by_id(recip['id'], CTX.db.citizens)
    else:
        recip = service.mongo.find({'phone_number': recip['phone_number']},
                                   CTX.db.citizens)

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

    output = service.mongo.add_and_copy_id(subsidy, CTX.db.subsidies)

    return service.utils.drop_nones(output)


def read(id):
    """
    Get a subsidy by ID

    :param id: the subsidy's ID
    :return: dict
    """
    # # Bunq get & update
    # subsidy = get_and_update(id, master_balance=True)
    # subsidy['account']['transactions'] = \
    #     service.bunq.get_payments(subsidy['account']['bunq_id'])

    subsidy = service.mongo.get_by_id(id, CTX.db.subsidies)
    if subsidy is None:
        raise service.exceptions.NotFoundException(
            f'Subsidy with id {id} not found'
        )

    return subsidy

def read_all(status: str=None, drop_transactions: bool=True):
    """
    Get all available subsidies. If a status is provided, return only
    those subsidies with the matching status.

    :return: list[dict]
    """

    if status and status not in STATUS_OPTIONS:
        raise service.exceptions.BadRequestException(
            'Status should be one of: {}.'
            .format(', '.join(STATUS_OPTIONS))
        )

    subsidies = service.mongo.get_collection(CTX.db.subsidies)
    output = []
    if not subsidies:
        return output

    if drop_transactions:
        for subsidy in subsidies:
            if 'transactions' in subsidy:
                subsidy.pop('transactions')

    # # Bunq Get & Update
    # check_statuses = []
    # if not status:
    #     check_statuses = [
    #         STATUSCODE.PENDING_ACCOUNT,
    #         STATUSCODE.PENDING_ACCEPT,
    #         STATUSCODE.OPEN,
    #         STATUSCODE.SHARE_CLOSED,
    #     ]
    #
    # elif status == STATUSCODE.PENDING_ACCOUNT:
    #     check_statuses = [STATUSCODE.PENDING_ACCOUNT]
    #
    # elif status == STATUSCODE.PENDING_ACCEPT:
    #     check_statuses = [
    #         STATUSCODE.PENDING_ACCOUNT,
    #         STATUSCODE.PENDING_ACCEPT
    #     ]
    #
    # elif status == STATUSCODE.OPEN:
    #     check_statuses = [STATUSCODE.PENDING_ACCEPT, STATUSCODE.OPEN]
    #
    # elif status == STATUSCODE.SHARE_CLOSED:
    #     check_statuses = [
    #         STATUSCODE.PENDING_ACCEPT,
    #         STATUSCODE.OPEN,
    #         STATUSCODE.SHARE_CLOSED
    #     ]
    #
    # elif status == STATUSCODE.CLOSED:
    #     check_statuses = [STATUSCODE.CLOSED]
    #
    # for sub in subsidies:
    #     if sub['status'] in check_statuses:
    #         sub_updated = get_and_update(sub['id'])
    #         if (sub_updated['status'] == status) or (not status):
    #             output.append(sub_updated)
    #         time.sleep(1)

    if status is None:
        targets = [
            STATUSCODE.PENDING_ACCEPT,
            STATUSCODE.PENDING_ACCOUNT,
            STATUSCODE.OPEN,
            STATUSCODE.SHARE_CLOSED,
        ]
    elif status == 'ALL':
        targets = STATUS_OPTIONS
    elif status in STATUS_OPTIONS:
        targets = [status]
    else:
        raise service.exceptions.BadRequestException(
            'Status should be one of: {}.'
            .format(', '.join(STATUS_OPTIONS))
        )

    for sub in subsidies:
        if sub['status'] in targets:
            output.append(sub)

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
    # obj = service.mongo.update_by_id(id, document, CTX.db.subsidies)
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
    # obj = service.mongo.replace_by_id(id, document, CTX.db.subsidies)
    # return obj


def delete(id):
    """
    Remove a subsidy, revoking any related shares and closing related account.

    :param id: the id of the subsidy to delete.
    :return: None
    """
    subsidy = service.mongo.get_by_id(id, CTX.db.subsidies)

    if subsidy is None:
        raise service.exceptions.NotFoundException('Subsidy not found')
    elif 'status' in subsidy:
        if subsidy['status'] == 'CLOSED':
            return None

    elif subsidy['status'] == STATUSCODE.CLOSED:
        raise service.exceptions.BadRequestException('Subsidy already closed')

    balance = float(service.bunq.get_balance(subsidy['account']['bunq_id']))

    # TODO Put in a function
    if balance > 0:
        pmt = service.bunq.make_payment_to_acct_id(
            subsidy['account']['bunq_id'],
            subsidy['master']['bunq_id'],
            balance,
            'Closing subsidy account'
        )

    time.sleep(1)
    payments = service.masters.get_payments_if_available(
        subsidy['account']['bunq_id']
    )


    time.sleep(1)
    try:
        service.bunq.close_account(subsidy['account']['bunq_id'])
    except service.exceptions.BadRequestException:
        # Don't crash if account was closed externally
        acct = service.bunq.read_account(subsidy['account']['bunq_id'])
        if acct['status'] != 'CANCELLED':
            raise

    subsidy['status'] = STATUSCODE.CLOSED
    subsidy['account']['balance'] = 0.
    subsidy['account']['transactions'] = payments
    subsidy['master']['balance'] = None
    subsidy['last_updated'] = service.utils.now()
    subsidy = service.mongo.update_by_id(id, subsidy, CTX.db.subsidies)

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
#         service.mongo.upsert(acct_db, CTX.db.accounts, ['iban'])
#
#     accts_db = service.mongo.get_collection(CTX.db.accounts)
#
#     return accts_db

def send_payment(payment: dict):
    """
    Send a one-off payment to a subsidy account. While the request allows for
    specifying arbitrary from's and to's, the from account must be one owned by
    the application of course, otherwise it will not work; more specifically, a
    master account. We do not want it to limit it to the master account of the
    subsidy itself because we could think of accessory accounts for this kind of
    operations Futhermore, an app-level check on the amount is performed
    here too, even if this is validated at request level already.

    :return: None
    """
    amount = payment['amount']
    if amount > 500:
        raise service.exceptions.BadRequestException('Payment amount not supported: %s' % amount)

    # check required CTX.db objects                                                                                       
    master = service.utils.drop_nones(payment['_from'])
    master = service.mongo.find(master, CTX.db.masters)
    if master is None:
        raise service.exceptions.NotFoundException(
            f'Master with id {master[id]} not found'
        )
    subsidy = service.utils.drop_nones(payment['to'])
    subsidy = service.mongo.find(subsidy, CTX.db.subsidies)
    if subsidy is None:
        raise service.exceptions.NotFoundException(
            f'Subsidy with id {subsidy[id]} not found'
        )

    name = payment['name']
    comment = payment['comment']

    #TODO Put in a function
    try:
        pmt = service.bunq.make_payment_to_acct_id(
            master['bunq_id'],
            subsidy['account']['bunq_id'],
            amount,
            'Payment: %s; comment: %s' % (name, comment)
        )
    except Exception as e:
        raise type(e)(e.message + ' Payment could not be sent - is the balance on the master sufficient?')

    # updating the master entry:
    # - new balance: current balance + transferred amount
    # - update transactions (not necessary per se since the background update daemon does that)
    # - update timestamp
    # updating the subsidy entry: current amount + transferred amount

    #TODO Create functions

    time.sleep(1)
    payments = service.masters.get_payments_if_available(
        master['bunq_id']
    )

    id = master['id']
    master['transactions'] = payments
    master['balance'] = float(master['balance']) - amount
    master['last_updated'] = service.utils.now()
    
    master = service.mongo.update_by_id(id, master, CTX.db.masters)

    # updating the subsidy entry: same
    time.sleep(1)
    payments =  service.bunq.get_payments(subsidy['account']['bunq_id'])
    
    id = subsidy['id']
    subsidy['account']['transactions'] = payments
    subsidy['account']['balance'] = float(subsidy['account']['balance']) + amount
    subsidy['last_updated'] = service.utils.now()
    subsidy['amount'] = float(subsidy['amount']) + amount

    subsidy = service.mongo.update_by_id(id, subsidy, CTX.db.subsidies)

    return None

def read_all_transactions(start_date: datetime=None, end_date: datetime=None):
    """
    Return a CSV containing all of the transactions, optionally date-filtered.
    At this point we do expect the arguments are both datetimes or nones. We do
    everything in memory for the time being.

    :param start_date: the starting date to filter on
    :param end_date: the ending date to filter on
    """
    all_subsidies = read_all(drop_transactions = False)
    rows = []
    for subsidy in all_subsidies:
        if 'account' in subsidy and 'transactions' in subsidy['account']:
            transactions = subsidy['account']['transactions']
            for t in transactions:
                if (start_date is None and end_date is None) or (parse(t['timestamp']) >= start_date and parse(t['timestamp']) <= end_date):
                    if 'recipient' in subsidy:
                        name = subsidy['recipient']['name']
                        phone = subsidy['recipient']['phone_number']
                    else:
                        name = None
                        phone = None
                    rows.append({
                        'subsidie_naam': subsidy['account']['description'],
                        'subsidie_deelnemer': name,
                        'subsidie_balans': subsidy['account']['balance'],
                        'subsidie_telefoon': phone,
                        'subsidie_rekening_nummer': subsidy['account']['iban'],
                        'transactie_omschrijving': t['description'],
                        'transactie_tegenpartij': t['counterparty_name'],
                        'transactie_tegenpartij_iban': t['counterparty_iban'],
                        'transactie_bedrag': t['amount'],
                        'transactie_datum': t['timestamp'],
                    })
    if (start_date is None and end_date is None):
        suffix = "full_dump"
    else:
        suffix = "from_%s_to_%s" % (str(start_date), str(end_date))
    filename = "transaction_%s.csv" % suffix
    if rows == []:
        return ([], filename, ["NO TRANSACTIONS FOUND FOR GIVEN TIME PERIOD"])
    else:
        return (rows, filename, rows[0].keys())

# utils
def get_and_update(id, master_balance=False):
    """
    Get the subsidy from the CTX.db, update the balance from bunq, update the status
    as appropriate, push the updates to the server, and return the subsidy.

    If the account is not accessible, a balance of None is reported and the CTX.db
    is not updated.

    :param id:
    :param master_balance: Get the most recent balance of the master (else
        do not return the balance of the master).
    :return:
    """
    # TODO: Do we even want to store balances?
    sub = service.mongo.get_by_id(id, CTX.db.subsidies)

    if sub is None:
        raise service.exceptions.NotFoundException('Subsidy not found')

    # # temporarily removed for performance
    # sub['account']['balance'] = \
    #     service.bunq.get_balance(sub['account']['bunq_id'])
    # time.sleep(1)

    # only need shares for PENDING_ACCEPT and OPEN subsidies
    get_share_statuscodes = [STATUSCODE.PENDING_ACCEPT, STATUSCODE.OPEN]
    full_read = (sub['status'] in get_share_statuscodes)
    acct = {}
    if sub['status'] != STATUSCODE.CLOSED:
        try:
            acct = service.bunq.read_account(sub['account']['bunq_id'],
                                             full_read)
            sub['account']['balance'] = acct['balance']
        except service.exceptions.NotFoundException:
            sub['account']['balance'] = None

    if master_balance:
        try:
            sub['master']['balance'] = \
                service.bunq.get_balance(sub['master']['bunq_id'])
        except service.exceptions.NotFoundException:
            sub['master']['balance'] = None
    else:
        sub['master']['balance'] = None

    if sub['status'] in get_share_statuscodes:
        if 'shares' in acct:
            if len(acct['shares']) > 0:
                share_status = acct['shares'][0]['status']

                if share_status == 'ACCEPTED':
                    sub['status'] = STATUSCODE.OPEN
                elif share_status in ['CANCELLED', 'REVOKED', 'REJECTED']:
                    sub['status'] = STATUSCODE.SHARE_CLOSED

    sub = service.mongo.update_by_id(sub['id'], sub, CTX.db.subsidies)

    return sub
