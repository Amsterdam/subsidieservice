import connexion
import functools
import bunq.sdk.exception


class BaseSubsidyServiceException(Exception):
    def __init__(self, message=''):
        self.message = message


class NotFoundException(BaseSubsidyServiceException):
    def __init__(self, msg='', other_stuff=None):
        super(NotFoundException, self).__init__(msg)
        # do other stuff


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
    * badRequestException: return 400 problem
    * NotImplementedException: return 501 problem

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

        except NotImplementedException as e:
            return connexion.problem(501, 'Not Implemented', e.message)

        except ForbiddenException as e:
            return connexion.problem(403, 'Forbidden', e.message)

        except UnauthorizedException as e:
            return connexion.problem(401, 'Unauthorized', e.message)

        except RateLimitException as e:
            return connexion.problem(429, 'Too many requests', e.message)

        except Exception as other_exception:
            raise other_exception

    return wrapper
