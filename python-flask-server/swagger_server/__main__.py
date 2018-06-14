#!/usr/bin/env python3
import warnings

import connexion

from swagger_server import encoder



def main():
    warnings.filterwarnings('ignore', message='\[bunq SDK')

    app = connexion.App(__name__, specification_dir='./swagger/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('swagger.yaml', arguments={'title': 'subsidy Allocation API'})

    # TODO: Improve SSL by generating and using non-adhoc certificates
    app.run(port=8080, debug=False)


if __name__ == '__main__':
    main()
