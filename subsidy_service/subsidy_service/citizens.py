"""
Business logic for working with citizens.
"""
import subsidy_service as service

# Globals
CTX = service.config.Context



# CRUD functionality
def create(citizen: dict):
    """
    Create a new citizen.

    Each citizen has a unique phone number, so only create the new citizen if
    the phone number is not yet in the db.

    :param citizen: The citizen to be added
    :type citizen: dict
    :return: True if the operation was successful, else False
    """

    if 'phone_number' not in citizen:
        raise service.exceptions.BadRequestException('Phone number required')
    if not citizen['phone_number']:
        raise service.exceptions.BadRequestException('Phone number required')

    citizen['phone_number'] = service.utils.format_phone_number(
        citizen['phone_number']
    )

    existing = service.mongo.find(
        {'phone_number': citizen['phone_number']},
        CTX.db.citizens
    )

    if existing:
        msg = 'A Citizen with that phone_number already exists. '
        if 'id' in existing:
            id = existing['id']
            msg += f'The id is "{id}".'

        raise service.exceptions.AlreadyExistsException(msg)

    obj = service.mongo.add_and_copy_id(citizen, CTX.db.citizens)

    return obj


def read(id):
    """
    Get a citizen by ID

    :param id: the citizen's ID
    :return: dict
    """
    output = service.mongo.get_by_id(id, CTX.db.citizens)
    if not output:
        raise service.exceptions.NotFoundException('Citizen not found')
    return output


def read_all():
    """
    Get all available citizens

    :return: list[dict]
    """
    return service.mongo.get_collection(CTX.db.citizens)


def update(id, citizen: dict):
    """
    Update a citizen's information.

    :param id: the citizen's id
    :param citizen: the fields to update. Nones will be ignored.
    :return: the updated citizen
    """
    raise service.exceptions.NotImplementedException('Not yet implemented')
    document = service.utils.drop_nones(citizen)
    obj = service.mongo.update_by_id(id, document, CTX.db.citizens)
    return obj


def replace(id, citizen: dict):
    """
    Replace a citizen in the database with the provided citizen, preserving ID.

    :param id: the citizen's id
    :param citizen: the new details
    :return: the new citizen's details
    """
    raise service.exceptions.NotImplementedException('Not yet implemented')
    document = citizen
    document['id'] = str(id)
    obj = service.mongo.replace_by_id(id, document, CTX.db.citizens)
    return obj


def delete(id):
    """
    Delete a citizen from the database.

    :param id: the id of the citizen to delete.
    :return: None
    """
    citizen = service.mongo.get_by_id(id, CTX.db.citizens)
    if citizen is None:
        raise service.exceptions.NotFoundException('Citizen not found')

    subsidies = service.subsidies.read_all()
    citizen_subsidies = [sub for sub in subsidies
                         if sub['recipient']['id'] == citizen['id']]
    if citizen_subsidies:
        ids = ', '.join([sub['id'] for sub in citizen_subsidies])

        raise service.exceptions.BadRequestException(
            f'Citizen has active subsidies with ids: {ids}'
        )

    service.mongo.delete_by_id(id, CTX.db.citizens)
    return None

