import hashlib
from django.contrib.auth.hashers import BasePasswordHasher
from django.utils.crypto import constant_time_compare

class LegacyPasswordHasher(BasePasswordHasher):
    """
    The Legacy password hashing algorithm (not recommended)
    """
    algorithm = "legacy"

    def encode(self, password):
        assert password
        hash = hashlib.sha1(password).hexdigest()
        return "%s$%s" % (self.algorithm, hash)

    def verify(self, password, encoded):
        algorithm, hash = encoded.split('$', 1)
        assert algorithm == self.algorithm
        encoded_2 = self.encode(password)
        return constant_time_compare(encoded, encoded_2)

    def safe_summary(self, encoded):
        algorithm, hash = encoded.split('$', 1)
        assert algorithm == self.algorithm
        return SortedDict([
            (_('algorithm'), algorithm),
            (_('hash'), mask_hash(hash)),
        ])

