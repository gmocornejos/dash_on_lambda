
import os
import requests

from .utils import unpack_request, dash_response, HttpApiRequest
from .oauth_utils import validate_tokens, id_token_to_header


def exchange_code_for_tokens(code, cookies):
    cognito_domain = f"{os.environ['COGNITO_DOMAIN']}.auth.{os.environ['COGNITO_REGION']}.amazoncognito.com"
    token_endpoint = f"https://{cognito_domain}/oauth2/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": os.environ["COGNITO_CLIENT_ID"],
        "redirect_uri": os.environ["APP_URL"],
        "code": code
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = requests.post(token_endpoint, data, headers=headers)
    response_body = response.json()

    # Check response code and it tokens valid
    if response.status_code != 200:
        return f"Authentication error. Error response from OAuth client: {response_body['error']}"
    if not validate_tokens(response_body["access_token"], response_body["id_token"]):
        return "Authenthication error: invalid tokens"

    # Set redirect URL 
    if "oauth_redirect_to" in cookies:
        redirect_path = cookies["oauth_redirect_to"].split(';')[0]
        path_token = [f"oauth_redirect_to=/; HttpOnly; Secure; SameSite=Lax; expires=Thu, 01 Jan 1970 00:00:00 GMT"]
    else:
        redirect_path = "/"
        path_token = []
    
    return {
        "cookies": [
            f"id_token={response_body['id_token']}; HttpOnly; Secure; SameSite=Lax",
            f"access_token={response_body['access_token']}; HttpOnly; Secure; SameSite=Lax",
            f"refresh_token={response_body['refresh_token']}; HttpOnly; Secure; SameSite=Lax"
        ] + path_token,
        "isBase64Encoded": False,
        "statusCode": 302,
        "headers": {"Location": redirect_path},
        "body": ""
    }


def unauthorized_response(public_app_client, request: HttpApiRequest):
    if "code" in request.query:
        return exchange_code_for_tokens(request.query["code"], request.cookies)
    else:
        return dash_response(public_app_client, request)


def oauth_flow_response(public_app_client, private_app_client, event, context):
    request = unpack_request(event, context)
    if "access_token" in request.cookies:
        if validate_tokens(request.cookies["access_token"], request.cookies["id_token"]):
            request = id_token_to_header(request)
            return dash_response(private_app_client, request)
        else:
            return unauthorized_response(public_app_client, request)
    else:
        return unauthorized_response(public_app_client, request)


def redirect_to_index(after_oauth_flow_path):
    return {
        "cookies": [
            f"oauth_redirect_to={after_oauth_flow_path}; HttpOnly; Secure; SameSite=Lax; path=/"
        ],
        "isBase64Encoded": False,
        "statusCode": 302,
        "headers": {"Location": "/"},
        "body": "" 
    }


def oauth_validate_response(app_client, event, context):
    request = unpack_request(event, context)
    if "access_token" in request.cookies:
        if validate_tokens(request.cookies["access_token"], request.cookies["id_token"]):
            request = id_token_to_header(request)
            return dash_response(app_client, request)
        else:
            return redirect_to_index(request.path)
    else:
        return redirect_to_index(request.path)