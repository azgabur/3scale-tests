"""
Test that http routes will be created and managed by zync
Regression test for https://issues.redhat.com/browse/THREESCALE-3545
"""
from urllib.parse import urlparse

import pytest

from testsuite.gateways.gateways import Capability

# This test can be done only with system apicast
pytestmark = [pytest.mark.skipif("TESTED_VERSION < Version('2.9')"),
              pytest.mark.required_capabilities(Capability.SAME_CLUSTER, Capability.PRODUCTION_GATEWAY),
              pytest.mark.disruptive]


@pytest.fixture(scope='module')
def service(service):
    """Change staging and production url to http:// with port 80"""
    stage_base = urlparse(service.proxy.list()['sandbox_endpoint']).hostname
    prod_base = urlparse(service.proxy.list()['endpoint']).hostname
    service.proxy.list().update({
        "sandbox_endpoint": f"http://{stage_base}:80",
        "endpoint": f"http://{prod_base}:80"
    })
    return service


def test_successful_requests(api_client, prod_client, application):
    """
    Test that apicast routes with http will be created by zync
    """
    # staging
    response = api_client.get('/get')
    assert response.status_code == 200

    request_url = urlparse(response.url)
    assert request_url.scheme == 'http'
    assert request_url.port == 80

    # production
    response = prod_client(application).get('/get')
    assert response.status_code == 200

    request_url = urlparse(response.url)
    assert request_url.scheme == 'http'
    assert request_url.port == 80