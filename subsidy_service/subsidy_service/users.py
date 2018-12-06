import subsidy_service as service

# Globals
CTX = service.config.Context

# TODO: Verify this interface (breaks convention but also isn't to be used in
#       the same way)


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
        if users is []:
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

def update(id, modified_user: dict):
    """
    Update a user. At the moment, ignore everything but the password and the admin flag.
    
    :param id:
    :param user:
    :return: dict
    """
    user = service.mongo.get_by_id(id, CTX.db.users)
    if not user:
        raise service.exceptions.NotFoundException(
            f'User "{id}" not found in database.'
        )
    elif 'password' not in modified_user and 'is_admin' not in modified_user:
        raise service.exception.BadRequestException(
            "Current implementation only supports password change and giving admin rights, please provide either."
        )
    else:
        if 'password' in modified_user and 'is_admin' in modified_user:
            update_password(modified_user['username'], modified_user['password'])
            user['password'] = modified_user['password']
            user['is_admin'] = modified_user['is_admin']
            return user
        elif 'password' in modified_user:
            update_password(modified_user['username'], modified_user['password'])
            user['password'] = modified_user['password']
            return user
        elif 'is_admin' in modified_user:
            user['is_admin'] = modified_user['is_admin']
            return user

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


def authenticate(username: str, password: str):
    """
    Verify that a user exists and has the correct password.

    :param username:
    :param password:
    :return: bool
    """
    return service.auth.verify_user(username, password)


def delete(username: str):
    """
    Remove a user from the database. Does not require verification but this is only callable as admin (see controller).

    :param username:
    :return: dict: success or error
    """
    user = service.mongo.get_by_id(id, CTX.db.users)
    if not user:
        raise service.exceptions.NotFoundException(
            f'User "{id}" not found in database.'
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
        return users
