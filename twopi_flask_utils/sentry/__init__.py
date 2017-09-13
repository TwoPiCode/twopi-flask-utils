from raven import Client
from raven.contrib.celery import register_signal, register_logger_signal
from raven.contrib.flask import Sentry

def create_client(conf, app_version='__UNKNOWN__', ignore_common_http=True):
    """Creates a sentry client.

    :param app_version: (string): App version sent to sentry for making events more rich
    :param conf['SENTRY_DSN']: (string, required): DSN of sentry server
    :param conf['SENTRY_SITE']: (string): The site description of the deployment.
    :returns: An initialized ``raven.Client`` instance.
    """
    ignore_exceptions = []
    if ignore_common_http:
        ignore_exceptions = [
            'werkzeug.exceptions.BadRequest', # 400
            'werkzeug.exceptions.Unauthorized', # 401
            'werkzeug.exceptions.Forbidden', # 403
            'werkzeug.exceptions.NotFound', # 404
            'werkzeug.exceptions.MethodNotAllowed', # 405
            'marshmallow.exceptions.ValidationError', # Marshmallow Validation Error.
            'webargs.core.ValidationError', # Webargs Validation Error
        ]

    client = Client(
        conf['SENTRY_DSN'],
        site=conf.get('SENTRY_SITE'),
        release=app_version,
        ignore_exceptions=ignore_exceptions
    )
    return client

def inject_sentry(app, ignore_common_http=True):
    """Injects sentry into a Flask Application

    Will only inject if ``SENTRY_DSN`` is specified. ``SENTRY_SITE`` and
    ``app.version`` are used to provide extra context to sentry events.

    :param app: (Flask Instance): A flask application to attach raven to.
    """

    if app.config.get('SENTRY_DSN'):
        client = create_client(app.config, app.version,
                               ignore_common_http=ignore_common_http)
        Sentry(app, client=client)
        return client

    return None


def celery_inject_sentry(celery):
    """Inject Sentry into a celery app. Requires ``raven``.

    If ``SENTRY_DSN`` is specified in config, a sentry client is created and
    attached. Additionally uses ``celery.version`` and ``SENTRY_SITE`` to
    provide extra context to sentry events.

    :param celery: The celery instance to attach raven to.

    """
    if celery.conf.get('SENTRY_DSN'):
        client = create_client(celery.conf,
                               app_version=getattr(celery, 'version', 'UNKNOWN'),
                               ignore_common_http=False)

        register_logger_signal(client)
        register_signal(client)
        return client

    return None
