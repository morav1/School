import json
from os import environ

REDIS_HOST = environ.get('REDIS_HOST', 'redis')
REDIS_PORT = environ.get('REDIS_PORT', '6379')

MYSQL_HOST = environ.get('MYSQL_HOST', 'mysql')
MYSQL_DATABASE = environ.get('MYSQL_DATABASE', 'db')
MYSQL_USER = environ.get('MYSQL_USER', 'user')
MYSQL_PASSWORD = environ.get('MYSQL_PASSWORD', '12345678')
MYSQL_ROOT_PASSWORD = environ.get('MYSQL_ROOT_PASSWORD', '12345678')

SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:3306/{MYSQL_DATABASE}'

default_credentials = {'johnc': 'eggs',
                       'erici': 'spam',
                       'grahmc': 'sousage'}

ALLOWED_CREDENTIALS = environ.get('ALLOWED_CREDENTIALS',json.dumps(default_credentials))