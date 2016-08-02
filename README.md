# TwoPi-Flask-Utils

![travis result image](https://travis-ci.org/TwoPiCode/twopi-flask-utils.svg)

A set of utilities to make working with flask web applications easier. 

This repository contains a collection of web utilities that are common across many of our projects.

It makes the most sense to keep these in a common repository to promote code re-use and modularity. 

## Useful Links:
- [PyPi](https://pypi.python.org/pypi/twopi-flask-utils/1.0.6)


## Unit Tests
Contributions to this repository must be unit tested. Please write appropriate tests for the code you are contributing. 


## Usage

See individual package README.md files for package readme. Each package must be imported using it's full namespace. This prevents loading unnecessary libraries when using this package.

```python
from twopi_flask_utils.config import build_url
# ...use build_url()
```

### Available Packages
- [celery](twopi_flask_utils/celery): Helpers to create celery apps that share flask application configuration
- [config](twopi_flask_utils/config)
- [deployment_release](twopi_flask_utils/deployment_release)
- [restful](twopi_flask_utils/restful): Helpers for use with flask-restful
- [sentry](twopi_flask_utils/sentry): Helpers for instantiating and using sentry with both Flask applications and Celery workers.
- [testing](twopi_flask_utils/testing): Helpers to assist with testing Flask applications.
- [token_auth](twopi_flask_utils/token_auth)

