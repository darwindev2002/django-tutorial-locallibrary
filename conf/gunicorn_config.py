command = '/var/www/django_tutorial_locallibrary/django_env/bin/gunicorn'
pythonpath = '/var/www/django_tutorial_locallibrary/django_env/bin/python3'
bind = 'unix:/var/www/django_tutorial_locallibrary/django_tutorial_locallibrary.sock'
workers = 3
mask = 7