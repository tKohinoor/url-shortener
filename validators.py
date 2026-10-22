from urllib.parse import urlparse
import re

MAX_URL_LENGTH = 2048
ALIAS_PATTERN = re.compile(r"^[A-Za-z0-9_-]{3,32}$")
RESERVED = {"api", "static", "admin"}


def normalize_url(url):
    """Trim whitespace and add https:// if no scheme was given."""
    url = url.strip()
    if "://" not in url:
        url = "https://" + url
    return url


def is_valid_url(url):
    if len(url) > MAX_URL_LENGTH:
        return False
    parsed = urlparse(url)
    # Only allow http/https. Blocking javascript:, data:, file: etc. matters for security.
    if parsed.scheme not in ("http", "https"):
        return False
    # Must have a host with at least one dot (or be localhost)
    host = parsed.hostname
    if not host:
        return False
    return "." in host or host == "localhost"


def is_valid_alias(alias):
    return bool(ALIAS_PATTERN.match(alias)) and alias.lower() not in RESERVED