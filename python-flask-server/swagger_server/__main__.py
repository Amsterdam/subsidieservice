#!/usr/bin/env python3
import connexion

from swagger_server import encoder

def main():
    app = connexion.App(__name__, specification_dir='./swagger/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('swagger.yaml', arguments={'title': 'subsidy Allocation API'})

    # TODO: Improve SSL by generating and using non-adhoc certificates
    app.run(port=8080, ssl_context='adhoc', debug=False)


if __name__ == '__main__':
    main()
