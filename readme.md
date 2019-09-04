# Blockchain eVote

Moving forward, the next steps would be to incorporate the Algorand Python SDK and start implementing wallets and accounts.

# Dev Environment Specifications:
-Ubuntu 18.04.03
-Python3

# Flask User Management

[![Build Status](https://travis-ci.org/mjhea0/flask-basic-registration.svg?branch=master)](https://travis-ci.org/mjhea0/flask-basic-registration)

Starter app for managing users - login/logout and registration.

## QuickStart

### Set Environment Variables

```sh
$ export APP_SETTINGS="project.config.DevelopmentConfig"
```

or

```sh
$ export APP_SETTINGS="project.config.ProductionConfig"
```

### Update Settings in Production

1. `SECRET_KEY`
1. `SQLALCHEMY_DATABASE_URI`

### Create DB

```sh
$ python manage.py create_db
$ python manage.py db init
$ python manage.py db migrate
$ python manage.py create_admin
```

### Run

```sh
$ python manage.py runserver
```

### Testing

Without coverage:

```sh
$ python manage.py test
```

With coverage:

```sh
$ python manage.py cov
```
