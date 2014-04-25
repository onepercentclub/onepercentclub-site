# TODO: not sure why but we need to include the SECRET_KEY here - importing from the test_runner file doesn't work
SECRET_KEY = 'hbqnTEq+m7Tk61bvRV/TLANr3i0WZ6hgBXDh3aYpSU8m+E1iCtlU3Q=='

from .test_runner import *


# Use firefox for running tests on Travis
SELENIUM_WEBDRIVER = 'firefox'
