from django.core.exceptions import ValidationError
from django.utils.unittest import TestCase

from .models import Region, SubRegion, Country


class GeoTestCase(TestCase):
    """ Tests for models in the geo app. """

    def setUp(self):
        # Start with a clean database for each test.
        Country.objects.all().delete()
        SubRegion.objects.all().delete()
        Region.objects.all().delete()

        # A test Region that is needed by the test SubRegion.
        region = Region()
        region.name = "Test Region"
        region.numeric_code = "001"
        region.save()

        # A test SubRegion that is needed by the test Country.
        subregion = SubRegion()
        subregion.name = "Test SubRegion"
        subregion.numeric_code = "002"
        subregion.region = region
        subregion.save()

        # Setup the test Country.
        self.country = Country()
        self.country.name = "Test"
        self.country.subregion = subregion
        self.country.save()

    def test_numberic_code_validation(self):
        """
        Test the numeric code validation.
        """

        # Test a numeric code with letter (capital 'O').
        self.country.numeric_code = "9O1"
        self.assertRaises(ValidationError, self.country.full_clean)

        # Test a numeric code that's too short.
        self.country.numeric_code = "91"
        self.assertRaises(ValidationError, self.country.full_clean)

        # Test a numeric code that's too long.
        self.country.numeric_code = "9198"
        self.assertRaises(ValidationError, self.country.full_clean)

        # Set a correct value and confirm there's no problem.
        self.country.numeric_code = "901"
        self.country.full_clean()

    def test_alpha2_code_validation(self):
        """
        Test the alpha2 code validation.
        """

        # Set a required field.
        self.country.numeric_code = "901"

        # Test an alpha2 code with a number.
        self.country.alpha2_code = "X6"
        self.assertRaises(ValidationError, self.country.full_clean)

        # Test an alpha2 code that's too short.
        self.country.alpha2_code = "X"
        self.assertRaises(ValidationError, self.country.full_clean)

        # Test an alpha2 code that's too long.
        self.country.alpha2_code = "XFF"
        self.assertRaises(ValidationError, self.country.full_clean)

        # Set a correct value and confirm there's no problem.
        self.country.alpha2_code = "XF"
        self.country.full_clean()
        self.country.save()

    def test_alpha3_code_validation(self):
        """
        Test the alpha3 code validation.
        """

        # Set and clear some fields.
        self.country.numeric_code = "901"
        self.country.alpha2_code = ""

        # Test an alpha3 code with a number.
        self.country.alpha3_code = "XX6"
        self.assertRaises(ValidationError, self.country.full_clean)

        # Test an alpha3 code that's too short.
        self.country.alpha3_code = "XF"
        self.assertRaises(ValidationError, self.country.full_clean)

        # Test an alpha3 code that's too long.
        self.country.alpha3_code = "XFFF"
        self.assertRaises(ValidationError, self.country.full_clean)

        # Set a correct value and confirm there's no problem.
        self.country.alpha3_code = "XFF"
        self.country.full_clean()
        self.country.save()
