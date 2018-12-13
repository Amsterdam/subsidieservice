"""
Subsidy initiatives business logic
"""
import subsidy_service as service
import time

# Globals                                                                                                                     

CTX = service.config.Context
# CRUD functionality                                                                                                          

def create(initiative: dict):
    """
    Create a new initiative, e.g. MaaS. The name is the unique identifier and case
    matters. In case the new initiative is requested as default but a default
    initiative already exists, the request is discarded. Also, the very first
    initiative will be flagged as default.

    :return: dict: the created object
    """

    initiative = service.utils.drop_nones(initiative.copy())

    if 'name' not in initiative:
        raise service.exceptions.BadRequestException("Initiatives must have a name")

    if not initiative['name']:
        raise service.exceptions.BadRequestException("Name cannot be empty")

    name = initiative['name']

    if 'default' in initiative and initiative['default']:
        existing = service.mongo.find({'default': True}, CTX.db.initiatives)
        if existing:
            raise service.exceptions.BadRequestException("Initiative is requested to be the default, but a default initiative already exists: %s" % existing['name'])
        else:
            default = True
    else:
        initiatives = read_all()
        if initiatives == []:
            default = True
        else:
            default = False

    init = {}
    init['name'] = name
    init['default'] = default
    
    output = service.mongo.add_and_copy_id(init, CTX.db.initiatives)

    return service.utils.drop_nones(output)

def read_all():
    """
    Returns all initiatives.

    :return: dict
    """

    initiatives = service.mongo.get_collection(CTX.db.initiatives)

    if not initiatives:
        return []
    else:
        return initiatives
