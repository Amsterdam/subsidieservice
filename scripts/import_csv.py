import pandas as pd
import click
from pprint import pprint

import warnings
warnings.filterwarnings('ignore', message='\[bunq SDK')

import subsidy_service as service
import traceback
import time

from swagger_server.models.citizen_base import CitizenBase
from swagger_server.models.subsidy_base import SubsidyBase


def process_row(row: pd.Series, master_id: str):
    phnum = service.utils.format_phone_number(row['Mobiel nummer'])

    citizen = {
        'name': row['Voornaam'] + ' ' + row['Achternaam'],
        'email': row['Email'],
        'phone_number': phnum
    }

    try:
        CitizenBase.from_dict(citizen)
    except:
        raise service.exceptions.BadRequestException('Invalid Citizen input')

    citizen = service.citizens.create(citizen)

    subsidy = {
        'name': row['Subsidienaam'],
        'recipient': citizen,
        'comment': row['Referentie veld'],
        'start_date': row['Begindatum'],
        'end_date': row['Einddatum'],
        'amount': float(row['Bedrag']),
        'master': {'id': master_id},
    }

    try:
        SubsidyBase.from_dict(subsidy)
    except:
        service.citizens.delete(citizen['id'])
        raise service.exceptions.BadRequestException('Invalid Subsidy input')

    try:
        subsidy = service.subsidies.create(subsidy)
    except Exception as e:
        service.citizens.delete(citizen['id'])
        raise e

    return {'citizen': citizen, 'subsidy': subsidy}


@click.command()
@click.argument('filename')
@click.argument('master_id')
def process_csv(filename, master_id):
    """
    Process subsidy recipients csv. Citizens and corresponding subsidies are
    added to the database, and subsidies are granted immediately upon
    processing. The created subsidies will have the master account indicated
    by master id (which must already exist in the database).

    See docs/InputREMCSVformat.docx for input csv specification.
    """
    # spec: pandas read_csv kwargs
    csv_spec = {
        'sep': ';',
        'header': 0,
        'skipinitialspace': True,
        'decimal': ',',
        'escapechar': '\\',
        'doublequote': False,
        'quotechar': '"'
    }

    recipients_df = pd.read_csv(filename, **csv_spec)
    # print(recipients_df)

    for idx, row in recipients_df.iterrows():
        try:
            output = process_row(row, master_id)
            print('Created:')
            pprint(output)
            time.sleep(1)  # rate limit
        except service.exceptions.BaseSubsidyServiceException as e:
            print('ERROR: Could not create subsidy for')
            print(row)
            print('REASON:', e.message)
            print()
        except Exception as e:
            traceback.print_exc()


def main():
    process_csv()


if __name__ == '__main__':
    main()
