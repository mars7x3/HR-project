SECRET_KEY = os.environ.get("SECRET_KEY",)

DEBUG = bool(int(os.environ.get("DEBUG", False)))

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "127.0.0.1").split(" ")

CSRF_TRUSTED_ORIGINS = os.environ.get('TRUSTS').split(' ')
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY",)