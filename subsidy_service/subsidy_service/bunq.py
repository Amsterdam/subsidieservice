import subsidy_service as service
import os
import re

from bunq.sdk.context import ApiContext, BunqContext
from bunq.sdk.model.generated import endpoint, object_
from bunq.sdk import exception

# Globals
CONF = service.utils.get_config()

try:
    CTX = ApiContext.restore(CONF.get('bunq', 'conf_path'))
    print('Bunq config loaded from', CONF.get('bunq', 'conf_path'))
except FileNotFoundError:
    basepath = os.getcwd()
    path = os.path.join(basepath, CONF.get('bunq', 'conf_path'))
    CTX = ApiContext.restore(path)
    print('Bunq config loaded from', path)

BunqContext.load_api_context(CTX)

USER_CTX = BunqContext._user_context

if USER_CTX.is_both_user_type_set() or USER_CTX.is_only_user_company_set():
    user_obj = USER_CTX.user_company
else:
    user_obj = USER_CTX.user_person


USER_ID = int(user_obj.id_)
USER_NAME = user_obj.name
CURRENCY = 'EUR'


# Actions
def create_account(description: str='Subsidie Gemeente Amsterdam'):
    request_map = {
        endpoint.MonetaryAccountBank.FIELD_DESCRIPTION: description,
        endpoint.MonetaryAccountBank.FIELD_CURRENCY: CURRENCY,
    }

    response = endpoint.MonetaryAccountBank.create(currency=CURRENCY,
                                                   description=description)

    acct_id = response.value
    return read_account(acct_id)


def read_account(id: int):
    response = endpoint.MonetaryAccountBank.get(int(id))
    acct = response.value
    return account_summary(acct)


def read_account_by_iban(iban: str, include_closed=False):
    accts = list_accounts(include_closed)
    output = None
    for acct in accts:
        if acct['iban'] == iban:
            output = acct
    return output


def get_payments(id: int):
    payments = _list_all_pages(endpoint.Payment, {}, id)
    return [payment_summary(pmt) for pmt in payments]


def list_accounts(include_closed=False):
    accts = _list_all_pages(endpoint.MonetaryAccountBank, {})

    output = [account_summary(acct) for acct in accts
              if (acct.status != 'CANCELLED') or include_closed]

    return output


def create_share(acct_id: int, recip_phnum: str):
    counterparty = object_.Pointer(
        'PHONE_NUMBER',
        recip_phnum
    )

    share_detail = object_.ShareDetail(
                payment=object_.ShareDetailPayment(
                    make_payments=True,
                    view_balance=True,
                    view_old_events=False,
                    view_new_events=True
                )
            )

    try:
        response = endpoint.ShareInviteBankInquiry.create(
            counter_user_alias=counterparty,
            share_detail=share_detail,
            status='PENDING',
            monetary_account_id=acct_id,
        )

    except exception.BadRequestException as e:
        # Share already exists, return it
        existing_alias = _get_alias_from_error_message(e.message)
        current_shares = list_shares(acct_id)
        matching_share = [s for s in current_shares
                          if s['counterparty'] == existing_alias][0]

        return matching_share

    share_id = response.value

    response = endpoint.ShareInviteBankInquiry.get(share_id, acct_id)
    share = response.value

    return share_summary(share)


def revoke_share(acct_id: int, share_id: int):
    share_dict = read_share(acct_id, share_id)
    status = share_dict['status']

    new_status = status
    if status in ['CANCELLED', 'REVOKED']:
        return share_dict
    elif status == 'PENDING':
        new_status = 'REVOKED'
    elif status == 'ACCEPTED':
        new_status = 'CANCELLED'

    response = endpoint.ShareInviteBankInquiry.update(
        share_id,
        acct_id,
        status=new_status
    )

    share = endpoint.ShareInviteBankInquiry.get(response.value, acct_id).value

    return share_summary(share)


def make_payment_to_iban(acct_id, to_iban, to_name, amount,
                 description='Subsidy Service payment'):
    counterparty = object_.Pointer(type_='IBAN', value=to_iban, name=to_name)
    amt = object_.Amount(value=str(amount), currency=CURRENCY)

    response = endpoint.Payment.create(
        amt,
        counterparty,
        description,
        monetary_account_id=acct_id,
    )

    pmt = endpoint.Payment.get(response.value, acct_id).value

    return payment_summary(pmt)


def make_payment_to_acct_id(from_acct_id, to_acct_id, amount,
                            description='Subsidy service internal payment'):

    to_acct = read_account(to_acct_id)

    pmt = make_payment_to_iban(
        from_acct_id,
        to_acct['iban'],
        to_acct['name'],
        amount,
        description,
    )

    return pmt


def close_account(id):
    acct = read_account(id)

    revoke_all_shares(id)

    response = endpoint.MonetaryAccountBank.update(
        id,
        status='CANCELLED',
        sub_status='REDEMPTION_VOLUNTARY',
        reason='OTHER',
        reason_description='Closed via Subsidy Service'
    )

    return acct


def revoke_all_shares(acct_id: int):
    share_ids = [s['id'] for s in list_shares(acct_id)]
    return [revoke_share(acct_id, share_id) for share_id in share_ids]


def list_shares(acct_id: int):
    response = endpoint.ShareInviteBankInquiry.list(monetary_account_id=acct_id)
    shares = [share_summary(share) for share in response.value]

    return shares


def read_share(acct_id: int, share_id: int):
    response = endpoint.ShareInviteBankInquiry.get(share_id, acct_id)
    return share_summary(response.value)


def get_balance(acct_id: int):
    acct = read_account(acct_id)
    return float(acct['balance'])


# Object abstractions
def account_summary(acct: endpoint.MonetaryAccountBank, full: bool=False):
    iban = ''
    name = ''
    for al in acct.alias:
        if al.type_ == 'IBAN':
            iban = al.value
            name = al.name

    acct_dict = {
        'type': 'bunq',
        'id': acct.id_,
        'description': acct.description,
        'balance': acct.balance.value,
        'iban': iban,
        'name': name,
        # 'user_id': USER_ID,
        # 'user_name': USER_NAME
    }

    if full:
        acct_dict['shares'] = list_shares(acct.id_)

    return acct_dict


def share_summary(share: endpoint.ShareInviteBankInquiry):
    share_dict = {
        'type': 'bunq_connect',
        'id': share.id_,
        'status': share.status,
        'start_date': share.start_date,
        'counterparty': share.counter_user_alias.display_name,
        'acct_id': share.monetary_account_id,
    }

    return share_dict


def payment_summary(payment: endpoint.Payment):
    pmt_dict = {
        'id': payment.id_,
        'amount': float(payment.amount.value),
        'description': payment.description,
        'counterparty_name': payment.counterparty_alias.pointer.name,
        'counterparty_iban': payment.counterparty_alias.pointer.value,
        'timestamp': payment.created
    }

    return pmt_dict


# Util functions
def _get_alias_from_error_message(msg):
    template = r'already has a Connect with user with alias "(.+)"'
    alias = re.search(template, msg)

    try:
        return alias.group(1)
    except AttributeError:
        return None


def _list_all_pages(endpoint_obj, list_params, *args, **kwargs):
    """
    The list method on endpoint objects may return paginated results. This
    function iterates through the pages and returns all results appended into
    one list. The params dict that can optionally be provided to the .list
    method must be provided explicitly (it may be empty, however). Other
    arguments to .list are provided through *args and **kwargs.

    The list method of the endpoint object is called like
        endpoint_obj.list(
            *args,
            params=list_params,
            **kwargs
        )

    The number of items per page can be set by settings list_params['count'].
    It may be maximally 200, which is also the default value inserted if
    the key 'count' is not present in de list_params dict.

    :param endpoint_obj: an endpoint object supporting the .list method
    :param list_params: the params dict to pass to .list
    :param args: any other args for .list
    :param kwargs: any other kwargs for .list
    :return: list
    """

    params = list_params.copy()

    # set default pagination count if not provided
    if 'count' not in params:
        params['count'] = '200'
    else:
        params['count'] = str(params['count'])

    # get first response
    response = endpoint_obj.list(*args, params=params, **kwargs)
    output = list(response.value)

    # keep getting pages while they are available
    while response.pagination.has_previous_page():
        response = endpoint_obj.list(
            *args,
            params=response.pagination.url_params_previous_page,
            **kwargs)

        output += list(response.value)

    return output

# new_acct = create_account('SS Test')
# pmt = make_payment_to_acct_id(6146, new_acct['id'], 100.00)
# pmt = make_payment_to_acct_id(new_acct['id'], 6146, 100.00)
# new_acct = close_account(new_acct['id'])
#
# print(list_accounts())
# print(list_shares(6146))
# print(create_share(6146, '+31648136656'))

