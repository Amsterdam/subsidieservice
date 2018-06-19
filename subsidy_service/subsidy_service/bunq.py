import subsidy_service as service
import os
import re
import time

from bunq.sdk.context import ApiContext, BunqContext
from bunq.sdk.model.generated import endpoint, object_
from bunq.sdk import exception

# Globals
CURRENCY = 'EUR'
CTX = service.config.Context

# Direct Interaction with Bunq
# Actions
def create_account(description: str='Subsidie Gemeente Amsterdam'):
    response = endpoint.MonetaryAccountBank.create(currency=CURRENCY,
                                                   description=description)
    acct_id = response.value
    return read_account(acct_id)


def read_account(id: int, full=False):
    try:
        response = endpoint.MonetaryAccountBank.get(int(id))
        acct = response.value
        return account_summary(acct, full)
    except Exception as e:
        raise _convert_exception(e)


def close_account(id):
    acct = read_account(id)
    time.sleep(1.5)
    revoke_all_shares(id)

    response = endpoint.MonetaryAccountBank.update(
        id,
        status='CANCELLED',
        sub_status='REDEMPTION_VOLUNTARY',
        reason='OTHER',
        reason_description='Closed via Subsidy Service'
    )

    return acct


def read_share(acct_id: int, share_id: int):
    try:
        response = endpoint.ShareInviteBankInquiry.get(share_id, acct_id)
        return share_summary(response.value)

    except exception.ApiException as e:
        raise _convert_exception(e)


def list_shares(acct_id: int):
    try:
        response = \
            endpoint.ShareInviteBankInquiry.list(monetary_account_id=acct_id)
    except Exception as e:
        raise _convert_exception(e)

    shares = [share_summary(share) for share in list(response.value)]
    return shares


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
        # Share with counterparty already may already exist -> return it
        existing_alias = _get_alias_from_error_message(e.message)
        matching_shares = []
        if existing_alias:
            current_shares = list_shares(acct_id)
            matching_shares = [s for s in current_shares
                               if s['counterparty'] == existing_alias]

        if len(matching_shares) == 1:
            return matching_shares[0]
        else:
            raise _convert_exception(e)

    except Exception as e:
        raise _convert_exception(e)

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

    try:
        response = endpoint.ShareInviteBankInquiry.update(
            share_id,
            acct_id,
            status=new_status
        )

    except Exception as e:
        raise _convert_exception(e)

    share = endpoint.ShareInviteBankInquiry.get(response.value, acct_id).value

    return share_summary(share)


def make_payment_to_iban(acct_id, to_iban, to_name, amount,
                         description='Subsidy Service payment'):
    counterparty = object_.Pointer(type_='IBAN', value=to_iban, name=to_name)
    amt = object_.Amount(value=str(amount), currency=CURRENCY)

    try:
        response = endpoint.Payment.create(
            amt,
            counterparty,
            description,
            monetary_account_id=acct_id,
        )

    except Exception as e:
        raise _convert_exception(e)

    pmt = endpoint.Payment.get(response.value, acct_id).value

    return payment_summary(pmt)


def get_payments(acct_id: int):
    try:
        payments = _list_all_pages(endpoint.Payment, {}, acct_id)
    except Exception as e:
        raise _convert_exception(e)
    return [payment_summary(pmt) for pmt in payments]


def list_accounts(include_closed=False):
    accts = _list_all_pages(endpoint.MonetaryAccountBank, {})

    output = [account_summary(acct) for acct in accts
              if (acct.status != 'CANCELLED') or include_closed]

    return output


# helper functions (no direct calls to Bunq)
def get_balance(acct_id: int):
    acct = read_account(acct_id)
    if acct is None:
        return None
    return float(acct['balance'])


def revoke_all_shares(acct_id: int):
    share_ids = [s['id'] for s in list_shares(acct_id)]
    output = []
    for share_id in share_ids:
        output.append(revoke_share(acct_id, share_id))
        time.sleep(1.5)
    return output


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


def read_account_by_iban(iban: str, include_closed=False, full=False):
    accts = list_accounts(include_closed)
    output = None
    for acct in accts:
        if acct['iban'] == iban:
            if full:
                output = read_account(acct['id'], full=full)
            else:
                output = acct

    if output is None:
        raise service.exceptions.NotFoundException('Account not found')

    return output


# Object abstractions
def account_summary(acct: endpoint.MonetaryAccountBank, full: bool=False):
    if not isinstance(acct, endpoint.MonetaryAccountBank):
        return None
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
        'status': acct.status
    }

    if full:
        acct_dict['shares'] = list_shares(acct.id_)

    return acct_dict


def share_summary(share: endpoint.ShareInviteBankInquiry):
    if not isinstance(share, endpoint.ShareInviteBankInquiry):
        return None
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
    if not isinstance(payment, endpoint.Payment):
        return None
    pmt_dict = {
        'id': payment.id_,
        'amount': float(payment.amount.value),
        'description': payment.description,
        'name': payment.alias.pointer.name,
        'iban': payment.alias.pointer.name,
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


def _convert_exception(e: Exception):
    """
    Convert bunq exceptions to service.exceptions exceptions.

    :param e:
    :return:
    """

    if isinstance(e, exception.NotFoundException):
        if 'Connect with id' in e.message:
            return service.exceptions.NotFoundException('Share not found')

        elif 'account for id' in e.message:
            return service.exceptions.NotFoundException('Account not found')

        else:
            return service.exceptions.NotFoundException('Not found')

    elif isinstance(e, exception.BadRequestException):
        if 'Iban pointer' in e.message:
            return service.exceptions.BadRequestException('Iban invalid')

        elif 'amount of a payment' in e.message:
            msg = 'Payment amount invalid'
            return service.exceptions.BadRequestException(msg)

        elif 'No user found' in e.message:
            msg = 'No bank account found for user'
            return service.exceptions.NotFoundException(msg)
        elif 'doesn\'t have enough money' in e.message:
            return service.exceptions.BadRequestException('Insufficient funds')

        else:
            return service.exceptions.BadRequestException('Invalid request')
    elif isinstance(e, exception.TooManyRequestsException):
        return service.exceptions.RateLimitException(
            'Too many request to bank API'
        )

    else:
        return e


def _list_all_pages(endpoint_obj, list_params: dict, *args, **kwargs):
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
        time.sleep(1.5)
        try:
            response = endpoint_obj.list(
                *args,
                params=response.pagination.url_params_previous_page,
                **kwargs)

            output += list(response.value)
        except:
            pass

    return output


# new_acct = create_account('SS Test')
# pmt = make_payment_to_acct_id(6146, new_acct['id'], 100.00)
# pmt = make_payment_to_acct_id(new_acct['id'], 6146, 100.00)
# new_acct = close_account(new_acct['id'])
#
# print(list_accounts())
# print(list_shares(6146))
# print(create_share(6146, '+31648136656'))

