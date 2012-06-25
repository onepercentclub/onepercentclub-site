from django.utils import unittest

from ..models import Member


""" Data integrity checks. """

class DataTests(unittest.TestCase):
    """ Test whether all expected fields are available for reading. """

    def testBasic(self):
        """
        1. Get all the member fields.
        1. Pick a random member.
        2. Check whether all fields are actually readable from the database.
        """
        field_names = Member._meta.get_all_field_names()
        
        # Pick a random member
        member = Member.objects.all().order_by('?')[0]
        
        # Check all fields
        for field_name in field_names:
            self.assertTrue(hasattr(field_name, member))
