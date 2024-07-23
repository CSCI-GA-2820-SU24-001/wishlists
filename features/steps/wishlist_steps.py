import os
import requests
from behave import given, when, then

@given('the server is started')
def step_impl(context):
    context.base_url = os.getenv(
        'BASE_URL', 
        'http://localhost:8080'
    )

    context.resp = requests.get(context.base_url + '/')
    assert context.resp.status_code == 200