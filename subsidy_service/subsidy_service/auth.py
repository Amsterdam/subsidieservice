import connexion
import subsidy_service as service
import functools
import passlib.context

# Globals
CONF = service.utils.get_config()
CLIENT = service.mongo.get_client(CONF)
DB = CLIENT.subsidy

CRYPT_CTX = passlib.context.CryptContext(schemes=['bcrypt_sha256'])


def authenticate(func: callable):
    """
    Decorator to require authentication before calling controller function.

    Username and password is extracted from current active request header. If
    no header is available or the header doesn't contain basic authorization,
    the returned function will produce a 401 Unauthorized
    connexion.ProblemException. If basicauth headers are available but the user
    is not in the database collection or the password is incorrect, the returned
    function produces a 403 Forbidden problem. If the user is authorized, then
    the input controller function is returned unchanged.

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

    @functools.wraps(func)  # propagate docstring etc
    def authenticated(*args, **kwargs):
        try:
            auth = connexion.request.authorization
        except RuntimeError:
            # No active request -> no headers at all
            return prob401

        if auth is None:
            # no login headers provided
            return prob401

        if not verify_user(auth.username, auth.password):
            # user not found/password incorrect
            return prob403
        else:
            # successfully authenticated
            output = func(*args, **kwargs)
            service.logging.audit(auth.username, func.__name__, output)
            return output

    return authenticated


def verify_user(username: str, password: str):
    """
    Verify that a user exists in the database and that the password is correct.

    :param username:
    :param password:
    :return: bool
    """
    user = service.mongo.find({'username': username}, DB.users)
    if user is None:
        # username not found
        return False

    return verify_password(password, user['password'])


def validate_password(pwd: str):
    # TODO: Determine if we want this (length, complexity, etc).
    return True


def hash_password(pwd: str):
    """
    Create passlib hash of password.

    :param pwd:
    :return: str: the hash of pwd (see passlib.hash)
    """
    return CRYPT_CTX.hash(pwd)


def verify_password(pwd: str, hash: str):
    """
    Verify that a password matches the given hash.

    :param pwd:
    :param hash: passlib hash
    :return: bool
    """
    return CRYPT_CTX.verify(pwd, hash)
