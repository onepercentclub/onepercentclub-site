# TODO: not sure why but we need to include the SECRET_KEY here - importing from the test_runner file doesn't work
SECRET_KEY = 'hbqnTEq+dfhdfhgdfh/TLANr3ipSU8m+E1iCtlU3Q=='

from .test_runner import *

# Use firefox for running tests on Shippable
SELENIUM_WEBDRIVER = 'firefox'

ROOT_URLCONF = 'onepercentclub.urls'
