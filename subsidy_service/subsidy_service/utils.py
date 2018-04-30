import os
import configparser
import subsidy_service as service
import datetime
import re


def get_config(filename='subsidy_service.ini', configdir=None):
    """
    Looks for a config file in several directories and loads it.

    Optional: specify the full path to the config directory to skip the default
    locations.

    The paths searched are, in order:
    - /etc/subsidy_service/config
    - subsidy_service/ (the directory where this file is)

    The default config file is located at
    subsidy_service/subsidy_service_defaults.ini.

    :param fname: the config file name, default: subsidy_service.ini
    :return: the config object
    """

    if configdir:
        paths = [configdir]
    else:
        paths =[]

    paths += [
        '/etc/subsidy_service/config',
    ]

    # default file in this directory
    pkg_dir = service.__path__[0]
    default = os.path.join(pkg_dir, 'subsidy_service_defaults.ini')

    config = configparser.ConfigParser()

    # reverse paths since first path = lowest priority
    config.read(default)
    config.read([os.path.join(p, filename) for p in reversed(paths)])

    return config


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