
from .utils import unpack_request, dash_response

def decode_validate_tokens(access_token, id_token):
    return []

def authorized_response(public_app_client, request):
    return dash_response(public_app_client, request)


def oauth_flow_response(public_app_client, private_app_client, event, context):
    request = unpack_request(event, context)
    if "access_token" in request["cookies"]:
        tokens = decode_validate_tokens(request["cookies"]["access_token"], request["cookies"]["id_token"])