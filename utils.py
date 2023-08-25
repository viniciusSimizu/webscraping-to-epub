from urllib.parse import urlparse


def uri_path(url: str) -> str:
    uri = urlparse(url)
    return uri.path
