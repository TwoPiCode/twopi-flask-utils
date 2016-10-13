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
    'sentry': ['raven[flask]'],
    'pagination': ['webargs', 'marshmallow'],
    'webargs': ['webargs']
}


tests_require = []
for x in extras.values():
    tests_require.extend(x)


def get_version():
    version_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'VERSION')
    v = open(version_path).read()
    if type(v) == str:
        return v.strip()
    return v.decode('UTF-8').strip()


readme_path = os.path.join(os.path.dirname(
  os.path.abspath(__file__)),
  'README.rst',
)
long_description = open(readme_path).read()

try:
    version = get_version()
except Exception as e:
    version = '0.0.0-dev'

setup(
    name='twopi-flask-utils',
    version=version,
    package_dir=dict(packages),
    packages=list(map(lambda x: x[0], packages)),
    extras_require=extras,
    tests_require=tests_require,
    test_suite='tests',
    url='https://github.com/TwoPiCode/twopi-flask-utils',
    author='Nick Whyte',
    author_email='nick@twopicode.com',
    description=('A set of utilities to make working with flask web '
                 'applications easier.'),
    long_description=long_description
)
