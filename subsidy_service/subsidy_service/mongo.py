"""
MongoDB operations on the database indicated by the config object
returned by subsidy_service.utils.get_config().
"""

import pymongo
import os

import bson

import subsidy_service as service

# Globals
CONF = service.utils.get_config()


# Database interactions
def _id_query(id):
    return {'_id':bson.ObjectId(str(id))}


def find(document, collection):
    return collection.find_one(document)


def get_client(conf=CONF):
    client = pymongo.MongoClient(host=conf['mongo']['host'],
                                 port=int(conf['mongo']['port']))
    return client


def get_collection(collection):
    docs = []
    for doc in collection.find():
        doc.pop('_id')
        docs.append(doc)

    return docs


def add_and_copy_id(document:dict, collection, id_field='id'):
    new_id = collection.insert_one(document).inserted_id

    new_record = collection.find_one(document)
    new_record['id'] = str(new_record['_id'])

    return update_by_id(new_id, new_record, collection)


def get_by_id(id, collection):
    try:
        doc = collection.find_one(_id_query(id))
    except bson.errors.InvalidId:
        doc = None

    if doc is not None:
        doc.pop('_id')

    return doc


def update_by_id(id, document, collection):
    collection.update_one(_id_query(id), {'$set': document})
    return get_by_id(id, collection)


def replace_by_id(id, document, collection):
    document['id'] = str(id)
    collection.replace_one(_id_query(id), document)
    return get_by_id(id, collection)


def delete_by_id(id, collection):
    collection.delete_one(_id_query(id))
    return None