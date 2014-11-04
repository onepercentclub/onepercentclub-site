from django.db import connection


def reset_db_sequence(table_name):
    """
    Reset set the sequence for an ID.
    Typically used after migration where we specify IDs when creating records.
    """
    cursor = connection.cursor()
    cursor.execute("SELECT setval('{0}_id_seq', (SELECT COALESCE(MAX(id),0)+1 FROM {0}));".format(table_name))


def reset_db_sequences(table_names):
    """
    See 'reset_db_sequence'
    """
    for table_name in table_names:
        reset_db_sequence(table_name)

