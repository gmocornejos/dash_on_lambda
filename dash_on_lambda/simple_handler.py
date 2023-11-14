
from .utils import dash_response


def simple_hander(dash_app):
    dash_app_client = dash_app.server.test_client()
    return lambda event, context: dash_response(dash_app_client, event, context)