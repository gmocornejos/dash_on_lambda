
import base64


def unpack_request(event, context):
    path = event["requestContext"]["http"]["path"]
    method = event["requestContext"]["http"]["method"]
    headers = event["headers"]
    try:
        payload = event["body"]
    except KeyError:
        payload = ""

    return {
        "path": path,
        "method": method,
        "headers": headers,
        "payload": payload
    }


def pack_response(response):
    response_headers = dict(response)
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


def dash_response(dash_app_client, event, context):
    request = unpack_request(event, context)
    response = dash_app_client.open(
        path=request["path"],
        method=request["method"],
        headers=request["headers"],
        data=request["payload"]
    )
    return pack_response(response)