#!/usr/bin/env python3
import logging
import os

import connexion

from swagger_server import encoder
# from subsidy_service.utils import get_config
#
# CONF = get_config()
# server_log_path = os.path.realpath(CONF['logging']['server_path'])
#
# def configure_logger():
#     CONF = get_config()
#     server_log_path = os.path.realpath(CONF['logging']['server_path'])
#
#     # ensure file exists
#     with open(server_log_path, 'a') as h:
#         pass
#
#     fh = logging.FileHandler(server_log_path)
#     fh.setLevel(logging.DEBUG)
#
#     for name in logging.Logger.manager.loggerDict: #['werkzeug', 'connexion.app', 'flask']:
#         print(name)
#         logger = logging.getLogger(name)
#         logger.addHandler(fh)
#

def main():
    # configure_logger()
    app = connexion.App(__name__, specification_dir='./swagger/', debug=False)
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('swagger.yaml', arguments={'title': 'subsidy Allocation API'})

    # fh = logging.FileHandler(server_log_path)
    # fh.setLevel(logging.DEBUG)
    # app.app.logger.setLevel(logging.DEBUG)
    # app.app.logger.addHandler(fh)

    # TODO: Improve SSL by generating and using non-adhoc certificates
    app.run(port=8080, ssl_context='adhoc')


if __name__ == '__main__':
    main()
