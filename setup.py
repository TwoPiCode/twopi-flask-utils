from setuptools import setup
import os

PACKAGE_PATH = './twopi_flask_utils'

packages = []

for item in os.listdir(PACKAGE_PATH):
    path = os.path.join(PACKAGE_PATH, item)
    if not item.startswith('_') and os.path.isdir(path):
        packages.append(('twopi_flask_utils.' + item, path))

extras = {
    'ldap': [],
    'restful': ['flask-restful'],
    'celery': ['celery'],
    'sentry': ['raven[flask]']
}


tests_require = []
for x in extras.values():
    tests_require.extend(x)

setup(
    name='twopi-flask-utils',
    version="1.0.4",
    package_dir=dict(packages),
    packages=list(map(lambda x: x[0], packages)),
    extras_require=extras,
    tests_require=tests_require,
    test_suite='tests'
)
