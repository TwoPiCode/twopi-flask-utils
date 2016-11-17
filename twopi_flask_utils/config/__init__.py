try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

def build_url(url, scheme=None, username=None, password=None, hostname=None, 
              port=None, path=None):
    """
    Parse a URL and override specific segments of it.
    
    :param url: The url to parse/build upon
    :param scheme: 
    :param username: 
    :param password: 
    :param hostname: 
    :param port:
    :param path:
    
    :return: A URL with overridden components

    """
    dsn = urlparse(url)

    if scheme is None: scheme = dsn.scheme
    if username is None: username = dsn.username
    if password is None: password = dsn.password
    if hostname is None: hostname = dsn.hostname
    if port is None: port = dsn.port
    if path is None: path = dsn.path

    def build_auth():
        if username is not None or password is not None:
            return '{}:{}@'.format(username or '', password or '')
        return ''

    def build_port():
        if port is not None:
            return ':{}'.format(port)
        return ''

    return '{scheme}://{auth}{hostname}{port}{path}'.format(
        scheme=scheme,
        auth=build_auth(),
        hostname=hostname or '',
        port=build_port(),
        path=path
    )
