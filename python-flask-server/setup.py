# coding: utf-8

import sys
from setuptools import setup, find_packages

NAME = "swagger_server"
VERSION = "1.0.0"

# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = ["connexion"]

setup(
    name=NAME,
    version=VERSION,
    description="Subsidy Service API",
    author_email="",
    url="",
    keywords=["Swagger", "Subsidy Service API"],
    install_requires=REQUIRES,
    packages=find_packages(),
    package_data={'': ['swagger/swagger.yaml']},
    include_package_data=True,
    entry_points={
        'console_scripts': ['swagger_server=swagger_server.__main__:main']},
    long_description="""\
    Manage and allocate subsidies for real-time expense management.   Throughout this documentation, *bank profile* will refer to a collection of bank accounts owned by the same entity, while *bank account* will refer to one specific account (i.e. having a single IBAN). Access to a bank profile from the subsidy service must be arranged with the service administrator. Similarly, a *subsidy* will refer to a specific allocation of funds into one account accessible by one citizen. A group of subsidies that are all for the same purpose should come from the same dedicated master-account.   Currently, profiles at the following banks are supported:   * Bunq    The bank information returned by &#x60;GET&#x60; calls is cached in the database. It is held as up to date as possible, but due to the caching it is not absolutely real-time. The information is updated as quickly as allowed by the bank APIs.   We are using the &#x60;deprecated&#x60; tag to mark endpoints that are planned but not yet implemented, these will return a 501. 
    """
)

