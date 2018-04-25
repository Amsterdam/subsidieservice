import logging
import os
import pprint
import json

import subsidy_service as service

# globals
CONF = service.utils.get_config()
LOGGER = logging.getLogger('audit')


def audit(user: str, action: str, result=None):
    msg = audit_log_message(user, action, result)
    LOGGER.info(msg)


def audit_log_message(user: str, action: str, result=None):

    obj = _convert_obj(result)

    try:
        msg = f'User "{user}" took action "{action}" with the following '\
              + 'result: ' + json.dumps(obj,
                                        indent=None,
                                        ensure_ascii=False)
    except TypeError:
        msg = f'User "{user}" took action "{action}" with the following ' \
              + 'result: ' + pprint.pformat(obj, width=999999999, compact=True)

    except:
        try:
            msg = f'User "{user}" took action "{action}" with the following ' \
                  + 'result: ' + str(obj)
        except:
            msg = f'User "{user}" took action "{action}"'

    return msg


def _convert_obj(obj):
    """
    Attempt to convert the object to a json.dumps-friendly form.

    :param obj:
    :return:
    """
    if type(obj) is list:
        return [_convert_obj(item) for item in obj]

    if obj is None:
        return None
    try:
        # Swagger model
        return obj.to_dict()
    except AttributeError:
        pass

    try:
        # something "dict-able"
        return dict(obj)
    except:
        pass

    return obj







def _setup_logger():
    LOGGER.setLevel(logging.DEBUG)

    # setup logger
    audit_log_path = os.path.realpath(CONF['logging']['audit_path'])

    # touch log file if doesn't exist
    if not os.path.isfile(audit_log_path):
        open(audit_log_path, 'a').close()

    # message format
    # TODO: Make this pure json?
    fmt = '%(asctime)s - Audit Log - %(message)s'
    fmtr = logging.Formatter(fmt=fmt)

    # write to file
    fh = logging.FileHandler(audit_log_path)
    fh.setFormatter(fmtr)
    LOGGER.addHandler(fh)

    # # write to stderr
    # sh = logging.StreamHandler()
    # sh.setFormatter(fmtr)
    # LOGGER.addHandler(sh)


_setup_logger()