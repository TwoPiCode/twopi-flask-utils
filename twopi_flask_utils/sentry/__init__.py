from raven import Client 
from raven.contrib.celery import register_signal, register_logger_signal
from raven.contrib.flask import Sentry


def create_client(conf, app_version='__UNKNOWN__'):
    """Creates a sentry client.
    @param app_version (string): App version sent to sentry for making events 
                                 more rich
    @param conf['SENTRY_DSN'] (string, required): DSN of sentry server
    @param conf['SENTRY_SITE'] (string): The site description of the deployment.
    """
    client = Client(
        conf['SENTRY_DSN'],
        site=conf.get('SENTRY_SITE'),
        release=app_version,
    )
    return client

def inject_sentry(app):
    """Injects sentry into a Flask Application
    
    Will only inject if SENTRY_DSN is specified.
    SENTRY_SITE and app.version is used to provide extra context to sentry events.

    @param app (Flask): A flask application to attach sentry to.
    """

    if app.config.get('SENTRY_DSN'):
        client = create_client(app.config, app.version)
        Sentry(app, client=client)


def celery_inject_sentry(celery):
    """Inject Sentry into a celery app. Requires raven.
    
    If SENTRY_DSN is specified in config, a sentry client is created and 
    attached. Additionally uses celery.version and SENTRY_SITE to provide extra
    context to sentry events.
    """
    if celery.conf.get('SENTRY_DSN'):
        client = create_client(celery.conf, 
                               app_version=getattr(celery, 'version', 'UNKNOWN'))

        register_logger_signal(client)
        register_signal(client)
