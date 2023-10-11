#!/bin/bash

alembic upgrade head

cd src

gunicorn -c /code/gunicorn/gunicorn.conf.py main:app