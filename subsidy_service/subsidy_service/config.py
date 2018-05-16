import configparser
import os
import sys
import pymongo
from bunq.sdk.context import ApiContext, BunqContext
import subsidy_service as service


def set_to_default(cls):
    cls.reset_to_default()
    return cls


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
    bunq_ctx = None
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
            cls.mongo_client = pymongo.MongoClient(
                host=cls.config['mongo']['host'],
                port=int(cls.config['mongo']['port'])
            )
            cls.db = cls.mongo_client.subsidy
        except (ValueError, IndexError, KeyError):
            pass

    @classmethod
    def _reload_bunq_ctx(cls):
        conf_path = cls.config.get('bunq', 'conf_path', fallback='')
        try:
            ctx = ApiContext.restore(conf_path)
            # print('Bunq config loaded from', conf_path, file=sys.stderr)
        except FileNotFoundError:
            basepath = os.getcwd()
            path = os.path.join(basepath, conf_path)
            try:
                ctx = ApiContext.restore(path)
                # print('Bunq config loaded from', path, file=sys.stderr)
            except:
                ctx = None

        cls.bunq_ctx = ctx

        try:
            BunqContext.load_api_context(ctx)
        except AttributeError:
            raise service.exceptions.ConfigException('Bunq config invalid')

    @classmethod
    def reset_to_default(cls):
        cls.replace(cls.default_paths)

    @classmethod
    def replace(cls, config_path):
        cls.config = configparser.ConfigParser()
        cls.mongo_client = None
        cls.bunq_ctx = None
        cls._last_read = None

        cls.read(config_path)
