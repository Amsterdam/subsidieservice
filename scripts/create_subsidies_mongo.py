import pandas as pd
import subsidy_service as service
import json

# TODO Merge the citizen and subsidy code flow, possibly externalize with add_bulk_citizens.py

#Example schema:
#Voornaam;Achternaam;Email;telefoonnummer;Connect rekening
#Arnulfo ;Mercati ;arnulfo.mercati@bunq.nl;+31642557177;NL06BUNQ9900092430

# This is to be run from the live container instance:
# - Drop the csv to be imported in the mounted share, /data/csv (see compose)
# - Get a python console on the docker
# - > from scripts import create_subsidies_mongo
# - > create_subsidies_mongo.start("/data/csv/manual_batch.csv", "ds76ffds67f6sdf6ds7", "500") #that is the id of the master rekening
# - try to get the citizens or subsidies and see the new entries
# - if you check back in the sandbox, or in the real life app, no new transactions are triggered of course
# - status is of course persistent because this is a real insert

# To test the flow:
# -Set up two tinkers, one for the master account one for the test user(s)
# -Create a subsidy instance for the user, and accept it on the mobile - this is basically the demo you see in the README
# -Stop all and delete the mongo data folder, but do not delete the tinkers
# -Restart all, put the subsided users in the csv and execute this
# -This now means adding citizens and subsidies already known to the sandbox - it is just like they were added with the mobile

CTX = service.config.Context

def row_to_citizen(row: pd.Series):
    citizen = {
        'email': row['Email'],
        'name': "%s %s" % (row['Voornaam'], row['Achternaam']),
        'phone_number': row['telefoonnummer'],
        'iban': row['Connect rekening']
    }

    return citizen

def row_to_subsidy(row: pd.Series, master_id, amount, rekening_to_id):
    subsidy = {
        'name': "MaaS pilot subsidie instantie van %s %s" % (row['Voornaam'], row['Achternaam']),
        'master_id': master_id,
        'citizen_iban': row['Connect rekening'],
        'citizen_name': "%s %s" % (row['Voornaam'], row['Achternaam']),
        'citizen_phone': row['telefoonnummer'],
        'recipient_id': rekening_to_id[row['Connect rekening']],
        'amount': amount,
        'comment': "Added manually from create_subsidies_mongo.py"
    }

    return subsidy


def subsidy_list(df: pd.DataFrame, master_id, amount, rekening_to_id):
    subsidies = []
    for i in range(len(df)):
        row = df.iloc[i]
        cit = row_to_subsidy(row, master_id, amount, rekening_to_id)
        subsidies.append(cit)
    return subsidies

def citizen_list(df: pd.DataFrame):
    citizens = []
    for i in range(len(df)):
        row = df.iloc[i]
        cit = row_to_citizen(row)
        citizens.append(cit)
    return citizens


def bulk_add_subsidies(input, master_id, amount, rekening_to_id):
    df = pd.read_csv(input, sep=';', dtype=str)
    citizens = citizen_list(df)
    subsidies = subsidy_list(df, master_id, amount, rekening_to_id)
    for sub in subsidies:
        entry = {
            "name": sub['name'],
            "account": {"iban": sub['citizen_iban']}
            "master": {"id": sub['master_id']},
            "recipient": {"id": sub['recipient_id'], "name": sub['citizen_name'], "phone_number": sub['citizen_phone']},
            "amount": sub['amount'],
            "comment": sub['comment'],
            "status": "OPEN"
        }
        output = service.mongo.add_and_copy_id(entry, CTX.db.subsidies)
        print("Added subsidy entry for %s" % sub['name'])

def bulk_add_citizens(input):
    df = pd.read_csv(input, sep=';', dtype=str)
    citizens = citizen_list(df)
    rekening_to_id = {}
    for cit in citizens:
        iban = cit['iban']
        cit.pop('iban')
        entry = cit
        output = service.mongo.add_and_copy_id(entry, CTX.db.citizens)
        print("Added citizen %s" % cit['name'])
        rekening_to_id.update({iban:output['id']})
    return rekening_to_id

def start(input, master_id, amount):
    rekening_to_id = bulk_add_citizens(input)
    bulk_add_subsidies(input, master_id, amount, rekening_to_id)
