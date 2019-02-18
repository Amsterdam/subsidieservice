import subsidy_service as service

# Globals
CTX = service.config.Context

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
    return create({"username": username, "password": password})

def create(user: dict):
    """
    Add a user to DB.users if the password passes validation by
    password_validate.

    :param user:
    :return: dict (user added)
    """
    if 'username' not in user or 'password' not in user:
        raise service.exceptions.BadRequestException(
            'Please provide both a username and a password'
        )

    username = user['username']
    password = user['password']

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
        users = service.mongo.get_collection(CTX.db.users)
        # The very first user we create gets admin rights.
        if users == [] or user['is_admin']:
            is_admin = True
        else:
            is_admin = False
        user = {
            'username': username,
            'password': service.auth.hash_password(password),
            'is_admin': is_admin,
            'real_name': user.get('real_name', None),
            'email': user.get('email', None),
            'phone_number': user.get('phone_number', None)
        }
        output = service.mongo.add_and_copy_id(user, CTX.db.users)
        output.pop('password')
        return output


def get(username: str):
    """
    Get a user by username.

    :param username:
    :return: dict with id, username, and password hash
    """
    return service.mongo.find({'username': username}, CTX.db.users)

def update(user_id, modified_user: dict):
    """
    Update a user. At the moment, ignore everything but the username, password and admin flag.
    Username is not strictly needed since we verify the id, but we add it for clarity.

    :param id:
    :param user:
    :return: dict
    """
    if 'username' in modified_user and modified_user['username'] == None:
        modified_user.pop('username')
    if 'password' in modified_user and modified_user['password'] == None:
        modified_user.pop('password')
    if 'is_admin' in modified_user and modified_user['is_admin'] == None:
        modified_user.pop('is_admin')
    user = service.mongo.get_by_id(user_id, CTX.db.users)
    if not user:
        raise service.exceptions.NotFoundException(
            f'User "{user_id}" not found in database.'
        )
    elif 'username' not in modified_user:
        raise service.exceptions.BadRequestException(
            "No username specified."
        )
    elif 'password' not in modified_user and 'is_admin' not in modified_user:
        raise service.exceptions.BadRequestException(
            "Current implementation only supports password change and giving admin rights, please provide either."
        )
    elif modified_user['username'] != user['username']:
        raise service.exceptions.BadRequestException(
            "User ID does not match request username"
        )
    else:
        if 'password' in modified_user and 'is_admin' in modified_user:
            update_password(modified_user['username'], modified_user['password'])
            update_admin_rights(modified_user['username'], modified_user['is_admin'])
            return modified_user
        elif 'password' in modified_user:
            update_password(modified_user['username'], modified_user['password'])
            return modified_user
        elif 'is_admin' in modified_user:
            update_admin_rights(modified_user['username'], modified_user['is_admin'])
            return modified_user

def update_password(username: str, new_password: str):
    """
    Update the password of a user. Does not require verification with the old password but this is only callable as admin (see controller).

    :param username:
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
    else:
        hashed = service.auth.hash_password(new_password)
        service.mongo.update_by_id(
            existing['id'],
            {'password': hashed},
            CTX.db.users
        )

def update_admin_rights(username: str, new_admin_rights: bool):
    """
    Update the admin rights of a user. Does not require verification with the old password but this is only callable as admin (see controller).

    :param username:
    :param new_admin_rights:
    :return: None
    """
    existing = get(username)

    if existing is None:
        raise service.exceptions.NotFoundException(
            f'User "{username}" not found in database.'
        )
    else:
        service.mongo.update_by_id(
            existing['id'],
            {'is_admin': new_admin_rights},
            CTX.db.users
        )

def authenticate(username: str, password: str):
    """
    Verify that a user exists and has the correct password.

    :param username:
    :param password:
    :return: bool
    """
    return service.auth.verify_user(username, password)


def delete(user_id: str):
    """
    Remove a user from the database. Does not require verification but this is only callable as admin (see controller).

    :param username:
    :return: dict: success or error
    """
    user = service.mongo.get_by_id(user_id, CTX.db.users)
    if not user:
        raise service.exceptions.NotFoundException(
            f'User "{user_id}" not found in database.'
        )
    elif 'is_admin' in user and user['is_admin']:
        raise service.exceptions.ForbiddenException('Admin user may not be removed')
    else:
        service.mongo.delete_by_id(user['id'], CTX.db.users)
        return None

def read_all():
    """
    Get all available users

    :return: dict
    """
    users = service.mongo.get_collection(CTX.db.users)
    if not users:
        return []
    else:
        output = []
        for u in users:
            u.pop('password')
            output.append(u)
        return output
