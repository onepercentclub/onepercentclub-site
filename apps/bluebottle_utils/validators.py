from django.core.exceptions import ValidationError
from localflavor.be.forms import BEPostalCodeField
from localflavor.ca.forms import CAPostalCodeField
from localflavor.de.forms import DEZipCodeField
from localflavor.fr.forms import FRZipCodeField
from localflavor.nl.forms import NLZipCodeField


# Can safely add more post code form fields here.
postal_code_mapping = {
    'BE': BEPostalCodeField(),
    'CA': CAPostalCodeField(),
    'DE': DEZipCodeField(),
    'FR': FRZipCodeField(),
    'NL': NLZipCodeField(),
}


def validate_postal_code(value, country_code):
    if country_code in postal_code_mapping:
        field = postal_code_mapping[country_code]
        field.clean(value)