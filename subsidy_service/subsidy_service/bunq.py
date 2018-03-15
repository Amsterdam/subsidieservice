from bunq.sdk import client, context
from bunq.sdk.model.generated import endpoint, object_
from bunq.sdk.context import ApiContext
from bunq.sdk.model.generated import endpoint


def get_context(path: str):
    return ApiContext.restore(path)


def create_new_account(ctx: ApiContext,):
    endpoint.MonetaryAccountBank.create(

    )

    return True