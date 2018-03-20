import subsidy_service as service

# Globals
CONF = service.utils.get_config()
CLIENT = service.mongo.get_client(CONF)
DB = CLIENT.subsidy

# CRUD functionality
def create(subsidy: dict):
    new_doc = service.mongo.add_and_copy_id({}, DB.subsidies)

    recip = service.utils.drop_nones(subsidy['recipient'])

    recip_full = service.mongo.find(recip, DB.citizens)

    if recip_full:
        subsidy['recipient'] = recip_full
    else:
        service.citizens.create(subsidy['recipient'])

    item = log_item(frm=new_doc, to=subsidy)

    new_doc['log'] = []
    new_doc['log'].append(item)
    new_doc['mutation_pending'] = True

    return service.mongo.update_by_id(new_doc['id'], new_doc, DB.subsidies)


def read(id: str):
    return service.mongo.get_by_id(id, DB.subsidies)


def read_all():
    return service.mongo.get_collection(DB.subsidies)


def update(id: str, subsidy: dict):
    pass


def delete(id: str, subsidy: dict):
    return service.mongo.delete_by_id(id)


def replace(id: str, subsidy: dict):
    pass

# Mutation log processing
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
