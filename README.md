# Django Tutorial - locallibrary
From [https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Deployment](https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Deployment)

## Steps to test run
```django-admin runserver```

## Steps to deploy
1. Install venv - ```sudo apt install python3-venv```
2. Create venv directory - ```python3.6 -m venv django_env```
3. Setup ```./.env``` file at root of project with credentials, for example:
~~~env
PGHOST=somewhere.service.database.azure.com
PGUSER=db_username
PGPORT=db_port
PGDATABASE=db_bane
PGPASSWORD=db_password
~~~
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

## Sample nginx.conf
Located at ```/etc/nginx/nginx.conf```
~~~nginx
user www-data;
worker_processes auto;
pid /run/nginx.pid;
include /etc/nginx/modules-enabled/*.conf;

events {
	worker_connections 768;
	# multi_accept on;
	accept_mutex on;
}

http {

	##
	# Basic Settings
	##

	sendfile on;
	tcp_nopush on;
	types_hash_max_size 2048;
	# server_tokens off;

	# server_names_hash_bucket_size 64;
	# server_name_in_redirect off;

	include /etc/nginx/mime.types;
	default_type application/octet-stream;

	##
	# SSL Settings
	##

	ssl_protocols TLSv1 TLSv1.1 TLSv1.2 TLSv1.3; # Dropping SSLv3, ref: POODLE
	ssl_prefer_server_ciphers on;

	##
	# Logging Settings
	##

	access_log /var/log/nginx/access.log;
	error_log /var/log/nginx/error.log;

	##
	# Gzip Settings
	##

	gzip on;

	# gzip_vary on;
	# gzip_proxied any;
	# gzip_comp_level 6;
	# gzip_buffers 16 8k;
	# gzip_http_version 1.1;
	# gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

	##
	# Virtual Host Configs
	##

	# include /etc/nginx/conf.d/*.conf;
	# include /etc/nginx/sites-enabled/*;

	
	upstream app_server {
		# fail_timeout=0 means we always retry an upstream even if it failed
		# to return a good HTTP response

		# for UNIX domain socket setups
		server unix:/var/www/django_tutorial_locallibrary/django_tutorial_locallibrary.sock fail_timeout=0;

		# for a TCP configuration
		# server 192.168.0.7:8000 fail_timeout=0;
	}

	server {
		# if no Host match, close the connection to prevent host spoofing
		listen 80 default_server;
		return 444;
	}

	server {
		# use 'listen 80 deferred;' for Linux
		# use 'listen 80 accept_filter=httpready;' for FreeBSD
		listen 80 deferred;
		client_max_body_size 4G;

		# set the correct host(s) for your site
		server_name 20.172.35.176;

		keepalive_timeout 5;

		# path for status files
		root /var/www/django_tutorial_locallibrary/static;
		
		location / {
			# checks for static file, if not found proxy to app
			try_files $uri @proxy_to_app;
		}

		location @proxy_to_app {
			proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
			proxy_set_header X-Forwarded-Proto $scheme;
			proxy_set_header Host $http_host;
			# we don't want nginx trying to do something clever with
			# redirects, we set the Host: header above already.
			proxy_redirect off;
			proxy_pass http://app_server;
		}

		error_page 500 502 503 504 /500.html;
		location = /500.html {
			root /var/www/django_tutorial_locallibrary/static;
		}		
	}

}


#mail {
#	# See sample authentication script at:
#	# http://wiki.nginx.org/ImapAuthenticateWithApachePhpScript
#
#	# auth_http localhost/auth.php;
#	# pop3_capabilities "TOP" "USER";
#	# imap_capabilities "IMAP4rev1" "UIDPLUS";
#
#	server {
#		listen     localhost:110;
#		protocol   pop3;
#		proxy      on;
#	}
#
#	server {
#		listen     localhost:143;
#		protocol   imap;
#		proxy      on;
#	}
#}
~~~

