import connexion
import subsidy_service as service
import functools
import passlib.context
import getpass

# Globals
CTX = service.config.Context
CRYPT_CTX = passlib.context.CryptContext(schemes=['bcrypt_sha256'])

# decorator with argument
def authenticate(as_admin: bool = False):

    def authenticate(func: callable): # decorator implementation
        """
        Decorator to require authentication before calling controller function.

        Username and password is extracted from current active request header. If
        no header is available or the header doesn't contain basic authorization,
        the returned function will raise a
        subsidy_service.exceptions.UnauthorizedException. If basicauth headers are
        available but the user is not in the database collection or the password is
        incorrect, the returned raises an exceptions.ForbiddenException. If the user
        is authorized, then the input controller function is returned unchanged.

        :param func: The controller function to wrap
        :return: function
        """

        @functools.wraps(func)  # wrapper; propagate docstring etc
        def authenticated(*args, **kwargs):
            try:
                auth = connexion.request.authorization
            except RuntimeError:
                # No active request -> no headers at all
                raise service.exceptions.UnauthorizedException(
                    'Please authenticate with username and password to call '
                    + func.__name__
                )
            if auth is None:
            # no login headers provided
                raise service.exceptions.UnauthorizedException(
                    'Please authenticate with username and password to call '
                    + func.__name__
                )

            if not verify_user(auth.username, auth.password, as_admin):
                # user not found/password incorrect, or admin-only endpoint
                raise service.exceptions.ForbiddenException(
                    "Username/password incorrect or admin rights required."
                )
            else:
                # successfully authenticated
                output = func(*args, **kwargs)
                service.logging.audit(auth.username, func.__name__, output)
                return output
        return authenticated
    return authenticate


def authenticate_promt(func: callable):
    """
    Decorator to require authentication before calling command line function.

    Username and password are requested in the prompt. If username is not in the
    database collection or the password is incorrect, the returned raises an
    exceptions.ForbiddenException. If the user is authorized, then the input
    function is executed unchanged.

    :param func: The controller function to wrap
    :return: function
    """

    @functools.wraps(func)  # propagate docstring etc
    def authenticated(*args, **kwargs):
        print('Please authenticate to call '+func.__name__)
        username = input('Username: ')
        password = getpass.getpass('Password: ')

        if not verify_user(username, password):
            # user not found/password incorrect
            raise service.exceptions.ForbiddenException(
                'User is not authorized to call ' + func.__name__
            )
        else:
            # successfully authenticated
            output = func(*args, **kwargs)
            service.logging.audit(username, func.__name__, output)
            return output

    return authenticated


def verify_user(username: str, password: str, as_admin: bool=False):
    """
    Verify that a user exists in the database and that the password is correct, checking admin rights if requested.

    :param username:
    :param password:
    :param as_admin:
    :return: bool
    """
    user = service.mongo.find({'username': username}, CTX.db.users)
    if user is None:
        # username not found
        return False
    else:
        if as_admin and 'is_admin' in user and user['is_admin'] is not as_admin:
            # username found but not admin
            return False
        else:
            return verify_password(password, user['password'])


def validate_password(pwd: str):
    # TODO: Determine if we want this (length, complexity, lists, etc).
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
