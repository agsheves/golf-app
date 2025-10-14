DJANGO_SUPERUSER_PASSWORD=$(openssl rand -base64 20) python manage.py changepassword admin
