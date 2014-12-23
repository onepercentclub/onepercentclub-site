import unicodecsv as csv


class DocdataDialect(csv.excel):
    """ Docdata CSV dialect. """
    delimiter = '\t'
