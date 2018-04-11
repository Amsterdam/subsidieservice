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
        return {'Error': f'User "{username}" already exists'}
    elif not service.auth.password_validate(password):
        return {'Error': 'Password does not meet requirements'}
    else:
        user = {
            'username': username,
            'password': service.auth.password_hash(password)
        }
        output = service.mongo.add_and_copy_id(user, DB.users)
        output.pop('password')
        return output


def get(username: str):
    """
    Get a user by username.

    :param username:
    :return: dict with id, username, and password
    """
    return service.mongo.find({'username': username}, DB.users)


def update_password(username: str, old_password: str, new_password: str):
    """
    Update the password of a user. Requires verification with the old password.

    :param username:
    :param old_password:
    :param new_password:
    :return: dict indicating success or error
    """
    existing = get(username)

    if existing is None:
        return {'Error': f'User "{username}" does not exist'}
    elif not service.auth.password_validate(new_password):
        return {'Error': 'Password does not meet requirements'}
    elif not authenticate(username, old_password):
        return {'Error': 'Unauthorized'}
    else:
        hashed = service.auth.password_hash(new_password)
        service.mongo.update_by_id(
            existing['id'],
            {'password': hashed},
            DB.users
        )
        return {'Status': 'Success'}


def authenticate(username: str, password: str):
    """
    Verify that a user exists and has the correct password.

    :param username:
    :param password:
    :return: bool
    """
    return service.auth.user_verify(username, password)


def delete(username: str, password: str):
    """
    Remove a user from the databse (requires verification).

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
