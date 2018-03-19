import pymongo

from bunq.sdk.model.generated import endpoint

import json

import sys

import subsidy_service as service

CONF = service.utils.get_config()

CLIENT = service.mongo.get_client(CONF)
DB = CLIENT.subsidy


def create(citizen: dict):
    """
    Create a new citizen.

    :param citizen: The citizen to be added
    :type citizen: dict
    :return: True if the operation was successful, else False
    """

    obj = service.mongo.add_and_copy_id(citizen, DB.citizens)

    # # --- Martijn's Demo
    # _USER_ITEM_ID = 5897
    # _MONETARY_ACCOUNT_ITEM_ID = 6146 #data['accountid']
    #
    # api_context = service.bunq.get_context('/usr/src/config/bunq.conf')
    #
    # monetary_account = endpoint.MonetaryAccountBank.get(
    #     api_context,
    #     _USER_ITEM_ID,
    #     _MONETARY_ACCOUNT_ITEM_ID
    # ).value
    #
    # iban_number = 'N/A'
    #
    # account_details = json.loads(monetary_account.to_json())
    #
    # print("Received account details: {}".format(account_details))
    #
    # for account in account_details['alias']:
    #     if (str(account['type']).lower() == 'iban'):
    #         iban_number = account['value']
    #
    # print("Extracted IBAN number: {}".format(iban_number))
    #
    # new_record['iban'] = iban_number

    # ---

    return obj


def read(id=None):
    if id is not None:
        obj = service.mongo.get_by_id(id, DB.citizens)
    else:
        obj = service.mongo.get_collection(DB.citizens)
    return obj


def update(id, citizen: dict):
    document = service.utils.drop_nones(citizen)
    obj = service.mongo.update_by_id(id, document, DB.citizens)
    return obj


def replace(id, citizen: dict):
    document = citizen
    document['id'] = str(id)
    obj = service.mongo.replace_by_id(id, document, DB.citizens)
    return obj


def delete(id):
    service.mongo.delete_by_id(id, DB.citizens)
    return None
