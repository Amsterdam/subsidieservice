import click
import time
import warnings
warnings.filterwarnings('ignore', '[bunq SDK beta]*')

import subsidy_service as service

from bunq.sdk.model.generated import endpoint
from bunq.sdk.model.generated.object_ import Pointer, Amount


@click.command()
@click.option('-c', '--conf',
              help='The path to an alternative bunq.conf file to use '
                   '(default taken from subsidy service config)')
@click.option('-a', '--amount',
              help='The amount of Euros to top up by (default 1000)',
              default=1000, type=float)
def top_up(conf=None, amount=1000.):
    """Top up a sandbox bunq account by the specified amount"""
    CTX = service.config.Context

    if conf:
        CTX._reload_bunq_ctx(conf)

    acct = service.bunq.list_accounts()[0]

    acct_id = acct['id']
    balance = float(acct['balance'])
    click.echo(f'Current balance: {balance:.2f}')
    time.sleep(1.5)

    amount_to_add = amount
    max_request_amount = 500

    while amount_to_add > 0:
        if amount_to_add > max_request_amount:
            request_amount = max_request_amount
        else:
            request_amount = amount_to_add

        amount_to_add -= request_amount

        endpoint.RequestInquiry.create(
            amount_inquired=Amount(str(request_amount), 'EUR'),
            counterparty_alias=Pointer('EMAIL', 'sugardaddy@bunq.com'),
            description='Requesting some spending money.',
            allow_bunqme=False,
            monetary_account_id=acct_id
        )

        click.echo(f'\rTotal added: {amount-amount_to_add:.2f}')
        time.sleep(1.5)

    acct = service.bunq.list_accounts()[0]
    balance = float(acct['balance'])
    click.echo(f'New balance: {balance:.2f}')

if __name__ == '__main__':
    top_up()




