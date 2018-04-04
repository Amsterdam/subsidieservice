import subsidy_service as service

# Globals
CONF = service.utils.get_config()
CLIENT = service.mongo.get_client(CONF)
DB = CLIENT.subsidy


# CRUD functionality
def create(subsidy: dict):
    """
    Create a new subsidy for a citizen. If the citizen is not yet in the
    database, they are added.

    :param subsidy: Subsidy to create
    :return: The created subsidy
    """
    # new_doc = service.mongo.add_and_copy_id({}, DB.subsidies)

    recip = service.utils.drop_nones(subsidy['recipient'])

    recip_full = service.mongo.find(recip, DB.citizens)

    if recip_full:
        subsidy['recipient'] = recip_full
    else:
        #TODO: Determine if this is desirable
        service.citizens.create(subsidy['recipient'])

    new_acct = service.bunq.create_account()

    new_share = service.bunq.create_share(new_acct['id'], recip['phone_number'])

    subsidy['account'] = new_acct

    # item = log_item(frm=new_doc, to=subsidy)

    # new_doc['log'] = []
    # new_doc['log'].append(item)
    # new_doc['mutation_pending'] = True

    return service.mongo.add_and_copy_id(subsidy, DB.subsidies)


def read(id):
    """
    Get a subsidy by ID

    :param id: the subsidy's ID
    :return: dict
    """
    return service.mongo.get_by_id(id, DB.subsidies)


def read_all():
    """
    Get all available subsidies

    :return: dict
    """
    return service.mongo.get_collection(DB.subsidies)


def update(id, subsidy: dict):
    """
    Update a subsidy's information.

    :param id: the subsidy's id
    :param subsidy: the fields to update. Nones will be ignored.
    :return: the updated subsidy
    """
    document = service.utils.drop_nones(subsidy)
    obj = service.mongo.update_by_id(id, document, DB.subsidies)
    return obj


def replace(id, subsidy: dict):
    """
    Replace a subsidy in the database with the provided subsidy, preserving ID.

    :param id: the subsidy's id
    :param subsidy: the new details
    :return: the new subsidy's details
    """
    document = subsidy
    document['id'] = str(id)
    obj = service.mongo.replace_by_id(id, document, DB.subsidies)
    return obj


def delete(id):
    """
    Delete a subsidy from the database.

    :param id: the id of the subsidy to delete.
    :return: None
    """
    service.mongo.delete_by_id(id, DB.subsidies)
    return None


###############################
# TODO: Mutation log processing
def base_mutation(subsidy: dict):
    props = ['approver1', 'approver2', 'approve_date1', 'approve_date2',
             'description']
    log_entry = {p: None for p in props}
    s = subsidy
    s.pop('')
    mut = {'from': subsidy}


def log_item(frm={}, to={}):
    f = frm.copy()
    t = to.copy()

    if 'log' in f:
        f.pop('log')
    if 'log' in t:
        t.pop('log')

    out = {
        'mutation':{
            'from': f,
            'to': t,
        },
        'create_date': service.utils.now()
    }

    return out

def approve_mutation():
    pass

def add_mutation(id: str, mut: dict):
    subsidy = service.mongo.get_by_id(id, DB.subsidies)
