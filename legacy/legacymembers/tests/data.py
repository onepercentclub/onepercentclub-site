import fileinput

from django.utils import unittest
from django.conf import settings
from django.db import connection

from members.models import Member


""" Data integrity checks. """

class DataTests(unittest.TestCase):
    """ Test whether all expected fields are available for reading. """

    sql_dump_path = settings.SQL_DUMP_PATH

    def setUp(self):
        """ Make sure we import the existing data. """
        # Grab a SQL cursor
        cursor = connection.cursor()
    
        sql_dump = fileinput.hook_compressed(self.sql_dump_path, 'rU')
    
        statement = ''
        for line in sql_dump:
            # Only execute non-empty lines which are not comments
            if len(line) > 2 and not line.lstrip()[:2] == '--':
                statement += line
    
                # Is this the end of a statement?
                if line.rstrip()[-1:] == ';':
    
                    cursor.execute(statement)
                    statement = ''

    def testBasic(self):
        """
        1. Get all the member fields.
        1. Pick a random member.
        2. Check whether all fields are actually readable from the database.
        """
        # Assert the existence of legacymembers
        self.assertTrue(Member.objects.all().exists())

        field_names = Member._meta.get_all_field_names()

        # Pick a random member
        member = Member.objects.all().order_by('?')[0]

        # Check all fields
        for field_name in field_names:
            self.assertTrue(hasattr(field_name, member))
