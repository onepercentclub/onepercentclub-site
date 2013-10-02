from .tags import TestTags

# test bluebottle apps
from bluebottle.accounts.tests.functional import AccountSeleniumTests
from bluebottle.accounts.tests.unittests import UserApiIntegrationTest


# test templatetags
from bluebottle.common.tests.templatetags import BlockVerbatimTestCase