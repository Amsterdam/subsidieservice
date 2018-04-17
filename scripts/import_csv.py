import pandas as pd
import click
from pprint import pprint

import warnings
warnings.filterwarnings('ignore', message='\[bunq SDK')

import subsidy_service as service


def process_row(row: pd.Series, master_id: str):
    phnum = service.utils.format_phone_number(row['Mobiel nummer'])

    citizen = {
        'name': row['Voornaam'] + ' ' + row['Achternaam'],
        'email': row['Email'],
        'phone_number': phnum
    }

    # citizen = service.citizens.create(citizen)

    subsidy = {
        'name': row['Subsidienaam'],
        'recipient': citizen,
        'comment': row['Referentie veld'],
        'start_date': row['Begindatum'],
        'end_date': row['Einddatum'],
        'amount': float(row['Bedrag']),
        'master': {'id': master_id},
    }

    # subsidy = service.subsidies.create(subsidy)
    # citizen = service.citizens.read(citizen['id'])
    # citizen.pop('subsidies')

    return {'citizen': citizen, 'subsidy': subsidy}


@click.command()
@click.argument('filename')
@click.argument('master_id')
def process_csv(filename):
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
    print(recipients_df)


    for idx, row in recipients_df.iterrows():
        output = process_row(row)
        print('Created:')
        pprint(output)
        print()


if __name__ == '__main__':
    process_csv()
