#!/bin/sh

set -e

# wait for Postgres to be available
/app/scripts/bash/wait-for-postgres.sh

# check for migrations and apply if necessary
poetry run python manage.py makemigrations --noinput
poetry run python manage.py migrate --noinput

# collect static files
poetry run python manage.py collectstatic --noinput

# start the Django server on port 8000
poetry run python manage.py runserver 0.0.0.0:8000
