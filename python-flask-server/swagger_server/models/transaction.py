# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util


class Transaction(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    def __init__(self, counterparty_name: str=None, counterparty_iban: str=None, description: str=None, amount: float=None, timestamp: datetime=None):  # noqa: E501
        """Transaction - a model defined in Swagger

        :param counterparty_name: The counterparty_name of this Transaction.  # noqa: E501
        :type counterparty_name: str
        :param counterparty_iban: The counterparty_iban of this Transaction.  # noqa: E501
        :type counterparty_iban: str
        :param description: The description of this Transaction.  # noqa: E501
        :type description: str
        :param amount: The amount of this Transaction.  # noqa: E501
        :type amount: float
        :param timestamp: The timestamp of this Transaction.  # noqa: E501
        :type timestamp: datetime
        """
        self.swagger_types = {
            'counterparty_name': str,
            'counterparty_iban': str,
            'description': str,
            'amount': float,
            'timestamp': datetime
        }

        self.attribute_map = {
            'counterparty_name': 'counterparty_name',
            'counterparty_iban': 'counterparty_iban',
            'description': 'description',
            'amount': 'amount',
            'timestamp': 'timestamp'
        }

        self._counterparty_name = counterparty_name
        self._counterparty_iban = counterparty_iban
        self._description = description
        self._amount = amount
        self._timestamp = timestamp

    @classmethod
    def from_dict(cls, dikt) -> 'Transaction':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The transaction of this Transaction.  # noqa: E501
        :rtype: Transaction
        """
        return util.deserialize_model(dikt, cls)

    @property
    def counterparty_name(self) -> str:
        """Gets the counterparty_name of this Transaction.


        :return: The counterparty_name of this Transaction.
        :rtype: str
        """
        return self._counterparty_name

    @counterparty_name.setter
    def counterparty_name(self, counterparty_name: str):
        """Sets the counterparty_name of this Transaction.


        :param counterparty_name: The counterparty_name of this Transaction.
        :type counterparty_name: str
        """

        self._counterparty_name = counterparty_name

    @property
    def counterparty_iban(self) -> str:
        """Gets the counterparty_iban of this Transaction.


        :return: The counterparty_iban of this Transaction.
        :rtype: str
        """
        return self._counterparty_iban

    @counterparty_iban.setter
    def counterparty_iban(self, counterparty_iban: str):
        """Sets the counterparty_iban of this Transaction.


        :param counterparty_iban: The counterparty_iban of this Transaction.
        :type counterparty_iban: str
        """

        self._counterparty_iban = counterparty_iban

    @property
    def description(self) -> str:
        """Gets the description of this Transaction.


        :return: The description of this Transaction.
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description: str):
        """Sets the description of this Transaction.


        :param description: The description of this Transaction.
        :type description: str
        """

        self._description = description

    @property
    def amount(self) -> float:
        """Gets the amount of this Transaction.


        :return: The amount of this Transaction.
        :rtype: float
        """
        return self._amount

    @amount.setter
    def amount(self, amount: float):
        """Sets the amount of this Transaction.


        :param amount: The amount of this Transaction.
        :type amount: float
        """

        self._amount = amount

    @property
    def timestamp(self) -> datetime:
        """Gets the timestamp of this Transaction.


        :return: The timestamp of this Transaction.
        :rtype: datetime
        """
        return self._timestamp

    @timestamp.setter
    def timestamp(self, timestamp: datetime):
        """Sets the timestamp of this Transaction.


        :param timestamp: The timestamp of this Transaction.
        :type timestamp: datetime
        """

        self._timestamp = timestamp
