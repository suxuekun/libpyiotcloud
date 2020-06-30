gunicorn --bind 192.168.100.17:8000 rest_api:app
gunicorn --bind 192.168.43.117:8000 rest_api:app

gunicorn --bind localhost:8000 rest_api:app
