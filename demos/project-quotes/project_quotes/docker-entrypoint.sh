#!/bin/bash

python manage.py migrate
uvicorn project_quotes.asgi:application --host 0.0.0.0 --port 8048 --log-level info
