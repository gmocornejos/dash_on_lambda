
import os
import base64
import jwt
from jwt import PyJWKClient
from jwt.exceptions import (DecodeError,
                            ExpiredSignatureError,
                            InvalidAudienceError,
                            InvalidIssuerError,
                            InvalidSignatureError,
                            PyJWKClientError
                            )


issuer_url = f"https://cognito-idp.{os.environ['COGNITO_REGION']}.amazonaws.com/{os.environ['COGNITO_USERPOOL_ID']}"
jwks_client = PyJWKClient(f"{issuer_url}/.well-known/jwks.json")


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


def cognito_signup_url():
    login_url_params = {
        "client_id": os.environ["COGNITO_CLIENT_ID"],
        "response_type": "code",
        "scope": "email+openid+profile",
        "redirect_uri": os.environ["APP_URL"]
    }
    login_url_base = f"https://{os.environ['COGNITO_DOMAIN']}.auth.{os.environ['COGNITO_REGION']}.amazoncognito.com/signup"
    login_url_query = '&'.join([f"{k}={v}" for k, v in login_url_params.items()])
    return login_url_base + '?' + login_url_query


def cognito_logout_url():
    logout_url_params = {
        "client_id": os.environ["COGNITO_CLIENT_ID"],
        "logout_uri": os.environ["APP_URL"] + "logout"
    }
    logout_url_base = f"https://{os.environ['COGNITO_DOMAIN']}.auth.{os.environ['COGNITO_REGION']}.amazoncognito.com/logout"
    logout_url_query = '&'.join([f"{k}={v}" for k, v in logout_url_params.items()])
    return logout_url_base + '?' + logout_url_query


def decode_tokens(access_token, id_token):
    try:
        access_key = jwks_client.get_signing_key_from_jwt(access_token)
        id_key = jwks_client.get_signing_key_from_jwt(id_token)
    except PyJWKClientError:
        return {}

    try:
        access_token_payload = jwt.decode(
            access_token,
            access_key.key,
            issuer=issuer_url,
            algorithms=["RS256"]
        )
    except InvalidSignatureError:
        print(f"Access token invalid signature")
        return {}
    except DecodeError:
        print(f"Error decoding Access tokens")
        return {}
    except ExpiredSignatureError:
        print(f"Access token expired")
        return {}
    except InvalidIssuerError:
        print(f"Access token claimed issuer does not match")
        return {}
    
    try:
        id_token_payload = jwt.decode(
            id_token,
            id_key.key,
            audience=os.environ["COGNITO_CLIENT_ID"],
            issuer=issuer_url,
            algorithms=["RS256"]
        )
    except InvalidSignatureError:
        print(f"ID token invalid signature")
        return {}
    except DecodeError:
        print(f"Error decoding ID token")
        return {}
    except ExpiredSignatureError:
        print(f"ID token expired")
        return {}
    except InvalidAudienceError:
        print(f"ID token claimed audience does not match")
        return {}
    except InvalidIssuerError:
        print(f"ID token claimed issuer does not match")
        return {}
    
    # Check at_hash claim
    rs256_hash = jwt.get_algorithm_by_name("RS256")
    access_token_rs256 = rs256_hash.compute_hash_digest(access_token.encode("ASCII"))
    at_hash = base64.urlsafe_b64encode(access_token_rs256[: (len(access_token_rs256)//2)])
    at_hash = at_hash.decode().rstrip('=')
    if id_token_payload["at_hash"] != at_hash:
        print("At hash claim failed")
        return {}

    return {
        "access_token": access_token_payload,
        "id_token": id_token_payload
    }


def validate_tokens(access_token, id_token):
    tokens = decode_tokens(access_token, id_token)
    if tokens == {}:
        return False
    else:
        return True
    

def id_token_to_header(request, fields=["sub", "nickname", "email"]):
    tokens = decode_tokens(request.cookies["access_token"], request.cookies["id_token"])
    for field in fields:
        request.headers[field] = tokens["id_token"][field]
    return request