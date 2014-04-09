from .tags import TestTags

# test bluebottle apps
from bluebottle.bb_accounts.tests.functional import AccountSeleniumTests
from bluebottle.bb_accounts.tests.unittests import UserApiIntegrationTest
#

# test templatetags
from bluebottle.common.tests.templatetags import BlockVerbatimTestCase