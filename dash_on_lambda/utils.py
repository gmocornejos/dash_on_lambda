
import os
import base64

def cognito_login_url():
    login_url_params = {
        "client_id": os.environ["COGNITO_CLIENT_ID"],
        "response_type": "code",
        "scope": "email+openid+profile",
        "redirect_uri": os.environ["APP_URL"]
    }
    login_url_base = f"https://{os.environ['COGNITO_DOMAIN']}.auth.{os.environ['COGNITO_REGION']}.amazoncognito.com/oauth2/authorize"
    login_url_query = '&'.join([f"{k}={v}" for k, v in login_url_params.items()])
    return login_url_base + '?' + login_url_query


def unpack_request(event, context):
    method = event["requestContext"]["http"]["method"]
    path = event["requestContext"]["http"]["path"]
    headers = event["headers"]
    try:
        query = event["queryStringParameters"]
    except KeyError:
        query = {}
    try:
        cookies = {k: v for k, v in [cookie.split('=') for cookie in event["cookies"]]}
    except KeyError:
        cookies = {}
    try:
        payload = event["body"]
    except KeyError:
        payload = ""

    return {
        "method": method,
        "path": path,
        "query": query,
        "headers": headers,
        "cookies": cookies,
        "payload": payload
    }


def pack_response(response):
    response_headers = dict(response.headers)
    # Json-like not serialized response
    if "Content-Type" not in response_headers:
        return{
            "cookies": [],
            "isBase64Encoded": False,
            "statusCode": response.status_code,
            "headers": response_headers,
            "body": response.data
        }
    # HTML-like response
    if response_headers["Content-Type"] == "text/html":
        return {
            "cookies": [],
            "isBase64Encoded": False,
            "statusCode": response.status_code,
            "headers": response_headers,
            "body": response.data
        }
    else: # HTML-like, but serialized response (e.g., images)
        return {
            "cookies": [],
            "isBase64Encoded": True,
            "statusCode": response.status_code,
            "headers": response_headers,
            "body": base64.b64encode(response.data).decode("utf-8")
        }


def dash_response(dash_app_client, request):
    response = dash_app_client.open(
        path=request["path"],
        method=request["method"],
        headers=request["headers"],
        data=request["payload"]
    )
    return pack_response(response)


def simple_response(dash_app_client, event, context):
    request = unpack_request(event, context)
    return dash_response(dash_app_client, request)