import os
import configparser
import subsidy_service as service
import datetime
import pymongo
import re

def drop_nones(dct: dict):
    """
    Drop all key-value pairs from a dict where the value is None.

    :param d: dict
    :return: the dict with no None values
    """
    return {k: v for k, v in dct.items() if v is not None}


def now():
    """
    Get the current datetime (YYYY-MM-DD HH:MM:SS)
    :return: str
    """
    return datetime.datetime.now().strftime('%Y-%M-%d %H:%m:%S')


def today():
    """
    Get the current date (YYYY-MM-DD)
    :return: str
    """
    return datetime.datetime.today().strftime('%Y-%M-%d')


def format_phone_number(phone_number: str):
    """
    Format phone numbers to the format +31123456789.

    Replaces leading 0 with +31 (assumed NL). Prepends + if it is not present.
    Eliminates any whitespace.

    :param phone_number: str: the phone number to format.
    :return: str
    """

    phnum = str(phone_number)

    rx = r'\+?[0-9\-\ ]+\Z'

    if not re.match(rx, phnum):
        raise service.exceptions.BadRequestException('Invaild phone number')

    phnum = phnum.replace('-', '')
    phnum = ''.join(phnum.split())  # Drop whitespace

    if phnum[0] == '0':
        phnum = '+31' + phnum[1:]

    if phnum[0] != '+':
        phnum = '+' + phnum

    return phnum
