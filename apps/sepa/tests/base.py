import os
from lxml import etree


class SepaXMLTestMixin(object):
    """ Common base class for SEPA XML export generation """

    def setUp(self):
        # Make sure a validating XML schema is available
        self.directory = os.path.dirname(__file__)
        xsd_file = os.path.join(self.directory, 'pain.001.001.03.xsd')
        self.xmlschema = etree.XMLSchema(file=xsd_file)

        super(SepaXMLTestMixin, self).setUp()
