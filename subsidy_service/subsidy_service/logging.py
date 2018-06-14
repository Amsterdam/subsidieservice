import logging
import os
import pprint
import json
import graypy
import traceback

import subsidy_service as service

# globals
CTX = service.config.Context
LOGGER = logging.getLogger('audit')

# kibana
# TODO: Move to config
LOGSTASH_HOST = os.getenv('LOGSTASH_HOST', '127.0.0.1')
LOGSTASH_PORT = int(os.getenv('LOGSTASH_GELF_UDP_PORT', 12201))


def audit(user: str, action: str, result=None):
    msg = audit_log_message(user, action, result)
    LOGGER.info(msg)


def exception(e, message=''):
    LOGGER.exception(message)


def audit_log_message(user: str, action: str, result=None):
    if not result:
        return f'User "{user}" took action "{action}"'

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
    global LOGGER

    LOGGER.setLevel(logging.DEBUG)

    # setup logger
    audit_log_path = os.path.realpath(CTX.config['logging']['audit_path'])

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

    gh = graypy.GELFHandler(LOGSTASH_HOST, LOGSTASH_PORT)
    gh.setFormatter(fmtr)
    LOGGER.addHandler(gh)

    # write to stderr
    sh = logging.StreamHandler()
    sh.setFormatter(fmtr)
    LOGGER.addHandler(sh)


_setup_logger()
