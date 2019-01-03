import json
import csv
import click

#Invoke with:
#python convert_subsidies_transactions_json_to_csv.py --subsidies-transactions-json ~/Downloads/transacties_all.json --output-file ~/Downloads/data_total.csv
#TODO Merge with twin script.

@click.option('-s', '--subsidies-transactions-json', help='JSON file containing the subsidies as returned from a for cycle on GET /subsidies/{id} for all ids and formatted as a JSON array')
@click.option('-d', '--output-file', help='CSV output file')
@click.command()
def cli(subsidies_transactions_json, output_file):
    """
    Convert a JSON transactions response into CSV. This is what you get if you perform a GET /master-accounts/238h7c42c23f.
    """
    with open(subsidies_transactions_json) as trans:
        rows = []
        transactions = json.load(trans)
        for t in transactions:
            for p in t['account']['transactions']:
                if 'recipient' in t:
                    name = t['recipient']['name']
                    phone = t['recipient']['phone_number']
                else:
                    name = None
                    phone = None
                rows.append({
                    'subsidie_naam': t['account']['description'],
                    'subsidie_deelnemer': name,
                    'subsidie_balans': t['account']['balance'],
                    'subsidie_telefoon': phone,
                    'subsidie_rekening_nummer': t['account']['iban'],
                    'transactie_omschrijving': p['description'],
                    'transactie_tegenpartij': p['counterparty_name'],
                    'transactie_bedrag': p['amount'],
                    'transactie_datum': p['timestamp'],
                })
        with open(output_file, 'w') as d:
            w = csv.DictWriter(d, rows[0].keys())
            w.writeheader()
            w.writerows(rows)


if __name__ == '__main__':
    cli()
