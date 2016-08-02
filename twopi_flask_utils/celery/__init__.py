from celery import Celery
from twopi_flask_utils.deployment_release import get_release

def create_celery(name, config_obj, inject_version=True, **kwargs):
    """Creates a celery app."""
    celery = Celery(name, broker=config_obj.CELERY_BROKER_URL, **kwargs)
    celery.config_from_object(config_obj)
    if inject_version:
        celery.version = get_release()

    return celery


def create_db_session(celery):
    """Creates an SQLA Database scoped session. Requires SQLAlchemy.

    Uses SQLALCHEMY_DATABASE_URI and SQLALCHEMY_POOL_RECYCLE to create an 
    apropriate engine. 

    If you are using MySQL and SQLALCHEMY_POOL_RECYCLE is not specified, 
    you'll have a bad time - this is required, as MySQL kills old sessions.
    """

    from sqlalchemy import create_engine
    from sqlalchemy.orm import scoped_session
    from sqlalchemy.orm import sessionmaker

    kwargs = {}
    if celery.conf.get('SQLALCHEMY_POOL_RECYCLE'):
        kwargs['pool_recycle'] = celery.conf.get('SQLALCHEMY_POOL_RECYCLE')

    engine = create_engine(
        celery.conf.get('SQLALCHEMY_DATABASE_URI'), 
        **kwargs
    )
    return scoped_session(sessionmaker(
        autocommit=False, autoflush=False, bind=engine))
