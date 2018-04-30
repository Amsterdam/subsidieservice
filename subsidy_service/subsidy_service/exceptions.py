import connexion
import functools
import bunq.sdk.exception


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


def exceptionHTTPencode(func: callable):
    """
    Decorator to encode exceptions as HTTP status codes. If during its execution
    func raises...
    * NotFoundException: return 404 problem
    * BadRequestException: return 400 problem
    * ForbiddenException: return 403 problem
    * UnauthorizedException: return 401 problem with WWW-Authenticate header
    * RateLimitExceptino: return 429 problem
    * NotImplementedException: return 501 problem
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
            return connexion.problem(404, 'Not Found', e.message)

        except BadRequestException as e:
            return connexion.problem(400, 'Bad request', e.message)

        except ForbiddenException as e:
            return connexion.problem(403, 'Forbidden', e.message)

        except UnauthorizedException as e:
            auth_header = {
                'WWW-Authenticate': 'Basic realm="Subsidy Service API"',
            }
            return connexion.problem(
                401, 'Unauthorized', e.message, headers=auth_header
            )

        except RateLimitException as e:
            return connexion.problem(429, 'Too many requests', e.message)

        except NotImplementedException as e:
            return connexion.problem(501, 'Not Implemented', e.message)

        except Exception as e:
            return connexion.problem(
                500, 'Internal Server Error',
                'Something has gone wrong on our server. '
                + 'Please contact the administrators.'
            )

    return wrapper
