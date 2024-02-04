# Django Tutorial - locallibrary
From [https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Deployment](https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Deployment)

## Steps to test run
```django-admin runserver```

## Steps to deploy
1. Install venv - ```sudo apt install python3-venv```
2. Create venv directory - ```python3.6 -m venv django_env```
3. Setup ```.env``` file with credentials
4. Setup systemctl service if necessary
5. Enable service to start at boot```sudo systemctl enable django_tutorial_locallibrary```

## Some useful commands
- Check if setting ready for deployment - ```python3 manage.py check --deploy ```
- Activate venv - ```source ./django_env/bin/activate```
- Start nginx service - ```sudo systemctl start nginx.service```


## Start project on local
~~~bash
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py runserver   
~~~

## Sample service file
Located at ```/etc/systemd/system/django_tutorial_locallibrary.service```
~~~bash
[Unit]
Description=Gunicorn instance to serve django_tutorial_locallibrary
After=network.target

[Service]
User=your_user_name
Group=www-data
WorkingDirectory=/var/www/django_tutorial_locallibrary
# Environment="PATH=/var/www/django_tutorial_locallibrary/django_env/bin"
EnvironmentFile=/var/www/django_tutorial_locallibrary/.env  # Your credentials
ExecStart=/var/www/django_tutorial_locallibrary/django_env/bin/gunicorn -c /var/www/django_tutorial_l>

[Install]
WantedBy=multi-user.target  # Start at boot
~~~


