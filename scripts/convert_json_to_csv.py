import json
import csv
import click

#Invoke with:
#python convert_json_to_csv.py --subsidies-json ~/Downloads/subsi.json --transactions-json ~/Downloads/trans.json --output-file ~/Downloads/data.csv

@click.option('-s', '--subsidies-json', help='JSON file containing the subsidies as returned from GET /subsidies')
@click.option('-t', '--transactions-json', help='JSON file containing the subsidies as returned from GET /master-accounts/{id}')
@click.option('-d', '--output-file', help='CSV output file')
@click.command()
def cli(subsidies_json, transactions_json, output_file):
    """
    Convert a JSON transactions response into CSV. This is what you get if you perform a GET /master-accounts/238h7c42c23f.
    """
    with open(subsidies_json) as subs:
        subsidies = json.load(subs)
        deelnemers = {}
        for s in subsidies:
            if 'account' in s and 'recipient' in s:
                deelnemers.update({
                    s['account']['iban']: {
                        'naam': s['recipient']['name'],
                        'telefoon': s['recipient']['phone_number']
                    }
                })
        with open(transactions_json) as trans:
            transactions = json.load(trans)
            master_account = transactions['name']
            rows = []
            for t in transactions['transactions']:
                iban = t['counterparty_iban']
                if iban in deelnemers:
                    naam = deelnemers[iban]['naam']
                    telefoon = deelnemers[iban]['telefoon']
                else:
                    naam = None
                    telefoon = None
                rows.append({
                    'master_account': master_account,
                    'subsidie_naam': naam,
                    'subsidie_telefoon': telefoon,
                    'subsidie_rekening_nummer': iban,
                    'bedrag': t['amount'],
                    'omschrijving': t['description'],
                    'datum': t['timestamp']
                })
            with open(output_file, 'w') as d:
                w = csv.DictWriter(d, rows[0].keys())
                w.writeheader()
                w.writerows(rows)


if __name__ == '__main__':
    cli()
