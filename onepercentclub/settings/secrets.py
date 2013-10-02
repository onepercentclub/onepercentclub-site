"""
secrets.py

Add passwords, API keys and other secrets in this file.
"""

# Make this unique, and don't share it with anybody.
SECRET_KEY = '5BVKwYL0OKMS+mXdF/TO2y9FEBNU5EhqvAnSU61m74UnSy415kTxaQ=='
COWRY_DOCDATA_TEST_MERCHANT_PASSWORD = 'pH2spEPe'
COWRY_DOCDATA_TEST_MERCHANT_NAME = '1procentclub_nw'

# Database authentication
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'onepercentsite',
        'USER': '',
        'PASSWORD': None
    },
}
