import os
import tempfile

# Must happen before importing the app
_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp.close()
os.environ["DB_PATH"] = _tmp.name

import pytest

from app import app, limiter


@pytest.fixture
def client():
    app.config["TESTING"] = True
    limiter.enabled = False  # don't trip the rate limit across tests
    with app.test_client() as c:
        yield c


def shorten(client, **payload):
    return client.post("/api/shorten", json=payload)


def test_home_page_loads(client):
    assert client.get("/").status_code == 200


def test_shorten_and_redirect(client):
    res = shorten(client, url="https://www.python.org")
    assert res.status_code == 201
    code = res.get_json()["code"]

    redirect = client.get("/" + code)
    assert redirect.status_code == 302
    assert redirect.headers["Location"] == "https://www.python.org"


def test_url_without_scheme_gets_https(client):
    res = shorten(client, url="python.org")
    assert res.get_json()["original_url"] == "https://python.org"


def test_missing_url_rejected(client):
    assert shorten(client).status_code == 400


@pytest.mark.parametrize("bad", [
    "javascript:alert(1)",
    "ftp://example.com/file",
    "https://nodots",
    "https://" + "a" * 3000 + ".com",
])
def test_invalid_urls_rejected(client, bad):
    assert shorten(client, url=bad).status_code == 400


def test_custom_alias(client):
    res = shorten(client, url="https://example.com", alias="my-test-link")
    assert res.status_code == 201
    assert res.get_json()["code"] == "my-test-link"


def test_duplicate_alias_returns_409(client):
    shorten(client, url="https://example.com", alias="dup-alias")
    res = shorten(client, url="https://example.org", alias="dup-alias")
    assert res.status_code == 409


@pytest.mark.parametrize("alias", ["ab", "api", "has space", "bad!char"])
def test_invalid_alias_rejected(client, alias):
    assert shorten(client, url="https://example.com", alias=alias).status_code == 400


def test_unknown_code_returns_404(client):
    assert client.get("/doesnotexist").status_code == 404


def test_click_counting(client):
    code = shorten(client, url="https://example.com").get_json()["code"]
    client.get("/" + code)
    client.get("/" + code)
    stats = client.get("/api/stats/" + code).get_json()
    assert stats["clicks"] == 2