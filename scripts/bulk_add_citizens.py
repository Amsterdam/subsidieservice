import requests
import pandas as pd
import click
import time
import tqdm

SUBSIDY_SERVICE_URL = 'https://subsidieservice.amsterdam.nl/v1'


def row_to_citizen(row: pd.Series):
    citizen = {
        'name': row['Voornaam'] + ' ' + row['Achternaam'],
        'phone_number': str(row['Mobiel nummer']),
        'email': row['Email'],
    }

    return citizen


def citizen_list(df: pd.DataFrame):
    citizens = []

    for i in range(len(df)):
        row = df.iloc[i]
        cit = row_to_citizen(row)
        citizens.append(cit)

    return citizens


@click.option('-u', '--username', help='Username for subsidy service')
@click.option('-p', '--password', prompt=True, hide_input=True,
              help='Subsidy service password')
@click.option('-i', '--input', type=click.Path(exists=True, dir_okay=False),
              help='Input csv')
@click.command()
def cli(username, password, input):
    """
    Bulk add citizens from a CSV to the subsidy service.
    """
    df = pd.read_csv(input, sep=';')
    citizens = citizen_list(df)

    for cit in tqdm.tqdm(citizens):
        r = requests.post(
            SUBSIDY_SERVICE_URL+'/citizens',
            json=cit,
            auth=(username, password,),
        )

        time.sleep(1)


if __name__ == '__main__':
    cli()
