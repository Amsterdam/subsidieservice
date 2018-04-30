import subsidy_service as service

# Globals
CONF = service.utils.get_config()
CLIENT = service.mongo.get_client(CONF)
DB = CLIENT.subsidy

# TODO: Verify this interface (breaks convention but also isn't to be used in
#       the same way)


def add(username: str, password: str):
    """
    Add a user to DB.users if the password passes validation by
    password_validate.

    :param username:
    :param password:
    :return: dict (user added)
    """

    existing = get(username)

    if existing is not None:
        raise service.exceptions.AlreadyExistsException(
            f'User "{username}" already exists.'
        )
    elif not service.auth.validate_password(password):
        raise service.exceptions.BadRequestException(
            'Password does not meet requirements.'
        )
    else:
        user = {
            'username': username,
            'password': service.auth.hash_password(password)
        }
        output = service.mongo.add_and_copy_id(user, DB.users)
        output.pop('password')
        return output


def get(username: str):
    """
    Get a user by username.

    :param username:
    :return: dict with id, username, and password hash
    """
    return service.mongo.find({'username': username}, DB.users)


def update_password(username: str, old_password: str, new_password: str):
    """
    Update the password of a user. Requires verification with the old password.

    :param username:
    :param old_password:
    :param new_password:
    :return: None
    """
    existing = get(username)

    if existing is None:
        raise service.exceptions.NotFoundException(
            f'User "{username}" not found in database.'
        )
    elif not service.auth.validate_password(new_password):
        raise service.exceptions.BadRequestException(
            'New password does not meet requirements.'
        )
    elif not authenticate(username, old_password):
        raise service.exceptions.ForbiddenException(
            'Old password verification failed.'
        )
    else:
        hashed = service.auth.hash_password(new_password)
        service.mongo.update_by_id(
            existing['id'],
            {'password': hashed},
            DB.users
        )


def authenticate(username: str, password: str):
    """
    Verify that a user exists and has the correct password.

    :param username:
    :param password:
    :return: bool
    """
    return service.auth.verify_user(username, password)


def delete(username: str, password: str):
    """
    Remove a user from the database (requires verification).

    :param username:
    :param password:
    :return: dict: success or error
    """
    if not authenticate(username, password):
        return {'Error':'Unauthorized'}
    else:
        user = service.mongo.find({'username': username}, DB.users)
        service.mongo.delete_by_id(user['id'], DB.users)
        return {'Status': 'Success'}
