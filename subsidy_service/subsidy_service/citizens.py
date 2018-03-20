"""
Business logic for working with citizens.
"""


from bunq.sdk.model.generated import endpoint

import json

import sys

import subsidy_service as service

# Globals
CONF = service.utils.get_config()
CLIENT = service.mongo.get_client(CONF)
DB = CLIENT.subsidy


# CRUD functionality
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


def read(id):
    """
    Get a citizen by ID

    :param id: the citizen's ID
    :return: dict
    """
    return service.mongo.get_by_id(id, DB.citizens)


def read_all():
    """
    Get all available citizens

    :return: dict
    """
    return service.mongo.get_collection(DB.citizens)


def update(id, citizen: dict):
    """
    Update a citizen's information.

    :param id: the citizen's id
    :param citizen: the fields to update. Nones will be ignored.
    :return: the updated citizen
    """
    document = service.utils.drop_nones(citizen)
    obj = service.mongo.update_by_id(id, document, DB.citizens)
    return obj


def replace(id, citizen: dict):
    """
    Replace a citizen in the database with the provided citizen, preserving ID.

    :param id: the citizen's id
    :param citizen: the new details
    :return: the new citizen's details
    """
    document = citizen
    document['id'] = str(id)
    obj = service.mongo.replace_by_id(id, document, DB.citizens)
    return obj


def delete(id):
    """
    Delete a citizen from the database.

    :param id: the id of the citizen to delete.
    :return: None
    """
    service.mongo.delete_by_id(id, DB.citizens)
    return None

