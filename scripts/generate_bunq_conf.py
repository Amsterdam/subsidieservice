from bunq.sdk import context
from bunq.sdk.json import converter
import click


@click.command()
@click.argument('api_key')#, help='The API key of the account in use')
@click.option('--output_path', '-o', default='./bunq.conf',
              help="Filename of output bunq conf file",
              type=click.Path(writable=True, resolve_path=True))
@click.option('--sandbox', '-s', is_flag=True, default=False,
              help='Crete the bunq conf for the sandbox environment')
def generate_bunq_conf(api_key, output_path, sandbox):
    """
    Generate a bunq conf file from an API key and save it.

    See github.com/bunq/sdk_python/blob/develop/examples/api_context_save_example.py
    for more details.
    """
    if sandbox:
        env = context.ApiEnvironmentType.SANDBOX
    else:
        env = context.ApiEnvironmentType.PRODUCTION

    ctx = context.ApiContext(
        env,
        api_key,
        'Subsidy Service'
    )
    ctx.save(output_path)
    click.echo(f'Bunq conf saved to {output_path}')


if __name__ == '__main__':
    generate_bunq_conf()