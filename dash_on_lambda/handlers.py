
from .utils import simple_response
from .oauth_flow import oauth_flow_response, oauth_validate_response


def simple_handler(dash_app):
    dash_app_client = dash_app.server.test_client()
    return lambda event, context: simple_response(dash_app_client, event, context)


def oauth_flow_handler(public_app, private_app):
    public_app_client = public_app.server.test_client()
    private_app_client = private_app.server.test_client()
    return lambda event, context: oauth_flow_response(public_app_client, private_app_client, event, context)


def oauth_validate_handler(dash_app):
    dash_app = dash_app.server.test_client()
    return lambda event, context: oauth_validate_response(dash_app, event, context)