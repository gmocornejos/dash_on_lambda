
import base64
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class HttpApiRequest:
    method: str
    path: str
    query: Dict[str, str]
    headers: List[str]
    cookies: Dict[str, str]
    payload: str


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

    return HttpApiRequest(
        method,
        path,
        query,
        headers,
        cookies,
        payload
    )


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


def dash_response(dash_app_client, request: HttpApiRequest):
    response = dash_app_client.open(
        path=request.path,
        method=request.method,
        headers=request.headers,
        data=request.payload
    )
    return pack_response(response)


def simple_response(dash_app_client, event, context):
    request = unpack_request(event, context)
    return dash_response(dash_app_client, request)