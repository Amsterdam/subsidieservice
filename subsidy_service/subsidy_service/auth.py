import hashlib
import connexion
import subsidy_service as service
import functools

CONF = service.utils.get_config()
CLIENT = service.mongo.get_client(CONF)
DB = CLIENT.subsidy


def authenticate(func: callable):
    """
    Decorator to require authentication before calling controller function.

    Username and password is extracted from current active request header. If
    no header is available or the header doesn't contain basic authorization,
    the returned function will produce a 401 Unauthorized
    connexion.ProblemException. If basicauth headers are available but the user
    is not in the database collection, the returned function produces a
    403 Forbidden problem. If the user is authorized, then the input
    controller function is returned.

    :param func: The controller function to wrap
    :return: function
    """
    prob401 = connexion.problem(
        401,
        'Unauthorized',
        'Please authenticate with username and password to call '
        + func.__name__
    )

    prob403 = connexion.problem(
        403,
        'Forbidden',
        'User is not authorized to call ' + func.__name__
    )

    @functools.wraps(func)
    def authenticated(*args, **kwargs):
        try:
            auth = connexion.request.authorization
            if auth is None:
                # no login headers available
                return prob401
        except RuntimeError:
            # No headers available at all
            return prob401

        doc = {'username': auth.username,
               'password': password_hash(auth.password)}

        user = service.mongo.find(doc, DB.users)

        if user is None:
            # username/password combo not found in DB.users
            return prob403
        else:
            # successfully authenticated
            return func(*args, **kwargs)

    return authenticated


def add_user(username: str, password: str):
    """
    Add a user to DB.users if the password passes validation by
    password_validate.

    :param username:
    :param password:
    :return: dict (user added)
    """

    output = None
    if password_validate(password):
        user = {
            'username': username,
            'password': password_hash(password)
        }

        output = service.mongo.add_and_copy_id(user, DB.users)

    return output


def password_validate(pwd: str):
    return True


def password_hash(pwd: str):
    return hashlib.sha256(pwd.encode()).hexdigest()
