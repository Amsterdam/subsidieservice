import connexion
import functools
import bunq.sdk.exception

import subsidy_service as service


class BaseSubsidyServiceException(Exception):
    def __init__(self, message=''):
        self.message = message


class NotFoundException(BaseSubsidyServiceException):
    pass


class BadRequestException(BaseSubsidyServiceException):
    pass


class NotImplementedException(BaseSubsidyServiceException):
    pass


class ForbiddenException(BaseSubsidyServiceException):
    pass


class UnauthorizedException(BaseSubsidyServiceException):
    pass


class RateLimitException(BaseSubsidyServiceException):
    pass


class AlreadyExistsException(BaseSubsidyServiceException):
    pass


class ConfigException(BaseSubsidyServiceException):
    pass


def exceptionHTTPencode(func: callable):
    """
    Decorator to encode exceptions as HTTP status codes. If during its execution
    func raises...
    * NotFoundException: return 404 problem
    * BadRequestException: return 400 problem
    * ForbiddenException: return 403 problem
    * UnauthorizedException: return 401 problem with WWW-Authenticate header
    * RateLimitException: return 429 problem
    * NotImplementedException: return 501 problem
    * AlreadyExistsException: return 409 problem
    * Any other exception: return 500 problem

    The description of the problem (if any) will be equal to the message of the
    exception.

    :param func:
    :return: output of func or connexion.Problem
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except NotFoundException as e:
            service.logging.exception(e)
            return connexion.problem(404, 'Not Found', e.message)

        except BadRequestException as e:
            service.logging.exception(e)
            return connexion.problem(400, 'Bad request', e.message)

        except ForbiddenException as e:
            service.logging.exception(e)
            return connexion.problem(403, 'Forbidden', e.message)

        except UnauthorizedException as e:
            service.logging.exception(e)
            auth_header = {
                'WWW-Authenticate': 'Basic realm="Subsidy Service API"',
            }
            return connexion.problem(
                401, 'Unauthorized', e.message, headers=auth_header
            )

        except RateLimitException as e:
            service.logging.exception(e)
            return connexion.problem(429, 'Too many requests', e.message)

        except NotImplementedException as e:
            service.logging.exception(e)
            return connexion.problem(501, 'Not Implemented', e.message)

        except AlreadyExistsException as e:
            service.logging.exception(e)
            return connexion.problem(409, 'Conflict', e.message)

        except Exception as e:
            service.logging.exception(e)
            return connexion.problem(
                500,
                'Internal Server Error',
                'Something has gone wrong on the server. '
                + 'Please contact the administrators.'
            )

    return wrapper
