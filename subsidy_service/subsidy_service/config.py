import configparser
import os
import sys
import pymongo
from bunq.sdk.context import ApiContext, BunqContext
from bunq.sdk.exception import BunqException
import subsidy_service as service


def set_to_default(cls):
    cls.reset_to_default()
    return cls


def _get_mongo_uri(config: configparser.ConfigParser):
    """Get the mongo host, port, and any credentials from the provided
    config object or from the environment.

    Returns a (uri, port) tuple, with the uri in the format
    mongodb://[usr[:pwd]@]host

    Preference is given to the environment. If no host is found,
    returns (None, None).

    """
    try:
        section = config['mongo']
    except KeyError:
        section = dict()

    host = None
    port = None

    usr = None
    pwd = None

    if 'MONGO_HOST' in os.environ:
        host = os.environ['MONGO_HOST']
    elif 'host' in section:
        host = section['host']
    else:
        return (None, None)

    if 'MONGO_PORT' in os.environ:
        port = os.environ['MONGO_PORT']
    elif 'port' in section:
        port = section['port']

    if 'MONGO_USER' in os.environ:
        usr = os.environ['MONGO_USER']
    elif 'user' in section:
        usr = section['user']

    if 'MONGO_PASSWORD' in os.environ:
        pwd = os.environ['MONGO_PASSWORD']
    elif 'password' in section:
        pwd = section['password']

    uri = 'mongodb://'
    if usr:
        uri += usr  # -> mongodb://usr
        if pwd:
            # -> mongodb://usr:pwd
            uri += ':' + pwd
        uri += '@'  # -> mongodb://usr[:pwd]@

    uri += host  # -> mongodb://[usr[:pwd]@]host
    uri += '/subsidieservice?authMechanism=SCRAM-SHA-1'

    service.logging.LOGGER.info(f'Trying to use mongo uri: {uri}')

    if port:
        port = int(port)

    return uri, port


@set_to_default
class Context():
    """
    Loads config files, if they exist. In descending order of
    precedence:
        * The file specified by :config_path: (if any)
        * /etc/subsidy_service/config/subsidy_service.ini
        * subsidy_service/subsidy_service_defaults.ini

    Additional config files can be loaded later using the read() method.
    Based on config files, contexts for other services are loaded.

    :param config_path: the path to the config file. May be a list for
        multiple config files, orders in precedence from highest to lowest.
    :param skip_defaults: don't load the default config
    """

    config = configparser.ConfigParser()
    mongo_client = None
    bunq_ctx = BunqContext
    db = None

    default_paths = [
        os.path.join(service.__path__[0], 'subsidy_service_defaults.ini'),
        '/etc/subsidy_service/config/subsidy_service.ini',
    ]

    _last_read = None

    def __init__(self, *args, **kwargs):
        raise NotImplementedError(
            'Do not initialize this class, '
            + 'use the class methods and properties instead.'
        )

    def __new__(cls):
        return cls

    @classmethod
    def read(cls, config_path, **kwargs):
        """Read config file and reload bunq context and mongo client"""
        cls.config.read(config_path, **kwargs)
        cls._reload_bunq_ctx()
        cls._reload_mongo_client()
        if isinstance(config_path, list):
            for p in config_path:
                if os.path.exists(p):
                    cls._last_read = config_path[-1]
        else:
            if os.path.exists(config_path):
                cls._last_read = config_path
        return cls

    @classmethod
    def _reload_mongo_client(cls):
        try:
            uri, port = _get_mongo_uri(cls.config)
            if uri:
                cls.mongo_client = pymongo.MongoClient(
                    host=uri,
                    port=int(port)
                )
                cls.db = cls.mongo_client.subsidieservice

        except (ValueError, IndexError, KeyError, AttributeError):
            pass

    @classmethod
    def _reload_bunq_ctx(cls, conf_path=None):
        if conf_path is None:
            conf_path = cls.config.get('bunq', 'conf_path', fallback='')

        if not conf_path:
            return

        try:
            api_ctx = ApiContext.restore(conf_path)
            # print('Bunq config loaded from', conf_path, file=sys.stderr)
        except FileNotFoundError:
            basepath = os.getcwd()
            path = os.path.join(basepath, conf_path)
            try:
                api_ctx = ApiContext.restore(path)
                # print('Bunq config loaded from', path, file=sys.stderr)
            except FileNotFoundError:
                raise service.exceptions.NotFoundException(
                    f'Bunq config not found at {path}'
                )

        try:
            cls.bunq_ctx.api_context().close_session()
        except (BunqException, TypeError):
            pass

        try:
            cls.bunq_ctx.load_api_context(api_ctx)
        except AttributeError:
            raise service.exceptions.ConfigException('Bunq config invalid')

    @classmethod
    def reset_to_default(cls):
        cls.replace(cls.default_paths)

    @classmethod
    def replace(cls, config_path):
        cls.config = configparser.ConfigParser()
        cls.mongo_client = None
        cls._last_read = None

        cls.read(config_path)


