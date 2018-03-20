from bunq.sdk import client, context
from bunq.sdk.context import ApiContext
from bunq.sdk.model.generated import endpoint


import subsidy_service as service
import os

# Globals
CONF = service.utils.get_config()
try:
    CTX = ApiContext.restore(CONF.get('bunq', 'conf_path'))
except FileNotFoundError:
    basepath = os.getcwd()
    path = os.path.join(basepath, CONF.get('bunq', 'conf_path'))
    CTX = ApiContext.restore(path)

USER = endpoint.User.list(CTX).value[0]

if USER.UserCompany:
    USER_ID = USER.UserCompany.id_
    USER_NAME = USER.UserCompany.name
elif USER.UserPerson:
    USER.UserPerson
    USER_ID = USER.UserPerson.id_
    USER_NAME = USER.UserPerson.name
else: # USER.UserLight
    USER_ID = USER.UserLight.id_
    USER_NAME = USER.UserLight.name

CURRENCY = 'EUR'

# USER_ID = endpoint.User.get()

# Actions
def create_account(ctx: ApiContext, description='Subsidie Gemeente Amsterdam'):
    request_map = {
        endpoint.MonetaryAccountBank.FIELD_DESCRIPTION: description,
        endpoint.MonetaryAccountBank.FIELD_CURRENCY: CURRENCY,
    }

    response = endpoint.MonetaryAccountBank.create(CTX, request_map)
    acct = response['Response'][0]['Id']

    output = {
        'type': 'bunq',
        'bank_id': acct['id'],
        'description': acct['description']
    }

    return output


def read_account(id: int):
    response = endpoint.MonetaryAccountBank.get(CTX, USER_ID, int(id))
    acct = response.value
    return account_summary(acct)


def list_accounts():
    response = endpoint.MonetaryAccountBank.list(CTX, USER_ID)

    accts = response.value

    output = [account_summary(acct) for acct in accts]

    return output


def account_summary(acct: endpoint.MonetaryAccountBank):
    acct_dict = {
        'type': 'bunq',
        'id': acct.id_,
        'description': acct.description,
        'balance': acct.balance.value,
        # 'user_id': USER_ID,
        # 'user_name': USER_NAME
    }

    return acct_dict