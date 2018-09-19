try:
    from urlparse import urljoin, urlparse
except ImportError:
    from urllib.parse import urljoin, urlparse

from flask import request


def is_safe_url(target):
    """
    Ensure a relative URL path is on the same domain as this host.
    This protects against the 'Open redirect vulnerability'.

    :param target: Relative url (typically supplied by Flask-Login)
    :type target: str
    :return: str
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc
