#!/usr/bin/env python3

import connexion

from swagger_server import encoder

import ssl


def main():
    # ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    # ctx.load_cert_chain('20009081_188.166.29.174.cert',
    #                     '20009081_188.166.29.174.key')

    app = connexion.App(__name__, specification_dir='./swagger/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('swagger.yaml', arguments={'title': 'subsidy Allocation API'})
    app.run(port=8080)


if __name__ == '__main__':
    main()
