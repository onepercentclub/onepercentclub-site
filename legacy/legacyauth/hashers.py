import hashlib
from django.contrib.auth.hashers import BasePasswordHasher, mask_hash
from django.utils.crypto import constant_time_compare

from django.utils.translation import ugettext_noop as _
from django.utils.datastructures import SortedDict


class LegacyPasswordHasher(BasePasswordHasher):
    """
    The Legacy password hashing algorithm (unsalted SHA1).
    """
    algorithm = "legacy"

    def salt(self):
        return ''

    def encode(self, password, salt):
        assert password
        hash = hashlib.sha1(password).hexdigest()
        return "%s$%s" % (self.algorithm, hash)

    def verify(self, password, encoded):
        algorithm, hash = encoded.split('$', 1)
        assert algorithm == self.algorithm
        encoded_2 = self.encode(password, '')
        return constant_time_compare(encoded, encoded_2)

    def safe_summary(self, encoded):
        algorithm, hash = encoded.split('$', 1)
        assert algorithm == self.algorithm
        return SortedDict([
            (_('algorithm'), algorithm),
            (_('hash'), mask_hash(hash)),
        ])

