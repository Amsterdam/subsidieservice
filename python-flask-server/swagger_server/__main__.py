#!/usr/bin/env python3
import warnings

import connexion
import requests

from swagger_server import encoder

from flask import redirect



def main():
    warnings.filterwarnings('ignore', message='\[bunq SDK')

    app = connexion.App(__name__, specification_dir='./swagger/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('swagger.yaml', arguments={'title': 'subsidy Allocation API'})

    # @app.route('/<path:path>/', methods=['GET'])
    # def catch_all(path):
    #     return connexion.problem(
    #         400,
    #         'Bad Request',
    #         'Trailing slashes not supported'
    #     )

    # allow trailing slashes
    # app.app.url_map.strict_slashes = False

    app.run(port=8080, debug=False, )


if __name__ == '__main__':
    main()
