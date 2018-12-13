"""
MongoDB operations on the database indicated by the config object
returned by subsidy_service.utils.get_config().
"""

import pymongo
import bson

import subsidy_service as service


# Database interactions
def find(document, collection):
    doc = collection.find_one(document)
    doc = _drop_id(doc)
    return doc

def get_collection(collection):
    docs = []
    for doc in collection.find():
        docs.append(_drop_id(doc))

    return docs

def add_and_copy_id(document: dict, collection, id_field='id'):
    new_id = collection.insert_one(document).inserted_id

    new_record = collection.find_one(document)
    new_record['id'] = str(new_record['_id'])

    return update_by_id(new_id, new_record, collection)


def get_by_id(id, collection):
    try:
        doc = collection.find_one(_id_query(id))
    except bson.errors.InvalidId:
        doc = None

    doc = _drop_id(doc)

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


def upsert(document, collection, const_fields):
    """
    Update the document with fields matching document[constant_fields].
    Add and copy id if it is not yet in the collection.

    :param document:
    :param collection:
    :param const_fields: iterable. the fields of document that should not have
        changed
    :return: dict. The updated document
    """
    query = {f: document[f] for f in const_fields}
    result = find(document, collection)
    if result is None:
        output = add_and_copy_id(document, collection)
    else:
        output = update_by_id(result['id'], document, collection)

    return output


# util functions
def _id_query(id):
    return {'_id': bson.ObjectId(str(id))}


def _drop_id(doc: [dict, None], id_field='_id'):
    try:
        doc.pop(id_field)
    except (KeyError, AttributeError):
        pass

    return doc
