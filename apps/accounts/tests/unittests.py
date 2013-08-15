import json
import re
from django.core import mail
from django.test import TestCase
from apps.bluebottle_utils.tests import UserTestsMixin
from registration.models import RegistrationProfile
from rest_framework import status
from apps.geo.tests import GeoTestsMixin


class UserApiIntegrationTest(UserTestsMixin, GeoTestsMixin, TestCase):
    """
    Integration tests for the User API.
    """
    def setUp(self):
        self.some_user = self.create_user(email='nijntje@hetkonijnje.nl', first_name='Nijntje')
        self.another_user = self.create_user()
        self.current_user_api_url = '/api/users/current'
        self.user_create_api_url = '/api/users/'
        self.user_profile_api_url = '/api/users/profiles/'
        self.user_settings_api_url = '/api/users/settings/'
        self.user_activation_api_url = '/api/users/activate/'
        self.user_password_reset_api_url = '/api/users/passwordreset'
        self.user_password_set_api_url = '/api/users/passwordset/'

    def test_user_profile_retrieve_and_update(self):
        """
        Test retrieving a public user profile by id.
        """
        user_profile_url = "{0}{1}".format(self.user_profile_api_url, self.some_user.id)
        response = self.client.get(user_profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.some_user.id)

        # Profile should not be able to be updated by anonymous users.
        full_name = {'first_name': 'Nijntje', 'last_name': 'het Konijntje'}
        response = self.client.put(user_profile_url, json.dumps(full_name), 'application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)

        # Profile should be able to be updated by logged in user.
        self.client.login(username=self.some_user.email, password='password')
        response = self.client.put(user_profile_url, json.dumps(full_name), 'application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['first_name'], full_name.get('first_name'))
        self.assertEqual(response.data['last_name'], full_name.get('last_name'))

        self.client.logout()

    def test_unauthenticated_user(self):
        """
        Test retrieving the currently logged in user while not logged in.
        """
        # Test unauthenticated user doesn't return 500 error.
        response = self.client.get(self.current_user_api_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, response.data)

    def test_current_user(self):
        """
        Test retrieving the currently logged in user after login.
        """
        self.client.login(username=self.some_user.email, password='password')
        response = self.client.get(self.current_user_api_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['first_name'], self.some_user.first_name)

        self.client.logout()

    def test_user_settings(self):
        """
        Test retrieving and updating a user's settings by id.
        """
        # Settings shouldn't be accessible until a user is logged in.
        user_settings_url = "{0}{1}".format(self.user_settings_api_url, self.some_user.id)
        response = self.client.get(user_settings_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)

        # Settings should be accessible after a user is logged in.
        self.client.login(username=self.some_user.email, password='password')
        some_user_settings_url = "{0}{1}".format(self.user_settings_api_url, self.some_user.id)
        response = self.client.get(some_user_settings_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['email'], self.some_user.email)
        self.assertFalse(response.data['newsletter'])

        # Test that the settings can be updated.
        response = self.client.put(some_user_settings_url, json.dumps({'newsletter': True}), 'application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertTrue(response.data['newsletter'])

        self.client.logout()

    def test_user_settings_country(self):
        """
        Regression test: BB-1333 (Country is not saved).
        """
        # Make sure there is a country.
        country = self.create_country('Netherlands', '1', alpha2_code='NL')

        self.client.login(username=self.some_user.email, password='password')

        # Retrieve current settings.
        some_user_settings_url = "{0}{1}".format(self.user_settings_api_url, self.some_user.id)
        response = self.client.get(some_user_settings_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['country'], None)

        # Test that the settings can be updated.
        response = self.client.put(some_user_settings_url, json.dumps({'country': country.alpha2_code}), 'application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['country'], country.alpha2_code)

        self.client.logout()

    def test_user_create(self):
        """
        Test creating a user with the api, activating the new user and updating the settings once logged in.
        """
        # Create a user.
        new_user_email = 'nijntje27@hetkonijntje.nl'
        new_user_password = 'password'
        response = self.client.post(self.user_create_api_url, {'email': new_user_email,
                                                               'password': new_user_password})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        user_id = response.data['id']
        self.assertEqual(len(mail.outbox), 1)

        # Logging in before activation shouldn't work. Test this by trying to access the settings page.
        self.client.login(username=new_user_email, password=new_user_password)
        new_user_settings_url = "{0}{1}".format(self.user_settings_api_url, user_id)
        response = self.client.get(new_user_settings_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)

        # Activate the newly created user.
        activation_key = RegistrationProfile.objects.filter(user__email=new_user_email).get().activation_key
        new_user_activation_url = "{0}{1}".format(self.user_activation_api_url, activation_key)
        response = self.client.get(new_user_activation_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # User should be auto-logged in after activation and settings should be able to be updated.
        response = self.client.get(new_user_settings_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['email'], new_user_email)
        self.assertFalse(response.data['newsletter'])

        # Test that the settings can be updated.
        response = self.client.put(new_user_settings_url, json.dumps({'newsletter': True}), 'application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertTrue(response.data['newsletter'])

        self.client.logout()

        # A second activation of a used activation code shouldn't work.
        response = self.client.get(new_user_activation_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # User should not be logged in after second activation attempt.
        new_user_settings_url = "{0}{1}".format(self.user_settings_api_url, user_id)
        response = self.client.get(new_user_settings_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)

        # Test that the email field is required on user create.
        response = self.client.post(self.user_create_api_url, {'password': new_user_password})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
        self.assertEqual(response.data['email'][0], 'This field is required.')

    def test_generate_username(self):
        new_user1_email = 'nijntje74@hetkonijntje.nl'
        new_user2_email = 'nijntje89@hetkonijntje.nl'
        new_user3_email = 'nijntje21@hetkonijntje.nl'
        new_user4_email = 'nijntje45@hetkonijntje.nl'
        first_name = 'Nijntje'
        last_name = 'het Konijntje'
        new_user_password = 'password'

        # Test username generation with duplicates.
        response = self.client.post(self.user_create_api_url, {'first_name': first_name,
                                                               'last_name': last_name,
                                                               'email': new_user1_email,
                                                               'password': new_user_password})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['username'], 'nijntjehetkonijntje')

        response = self.client.post(self.user_create_api_url, {'first_name': first_name,
                                                               'last_name': last_name,
                                                               'email': new_user2_email,
                                                               'password': new_user_password})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['username'], 'nijntjehetkonijntje2')

        response = self.client.post(self.user_create_api_url, {'first_name': first_name,
                                                               'last_name': last_name,
                                                               'email': new_user3_email,
                                                               'password': new_user_password})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['username'], 'nijntjehetkonijntje3')

        # Test username generation with no first name or lastname.
        response = self.client.post(self.user_create_api_url, {'email': new_user4_email,
                                                               'password': new_user_password})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['username'], 'nijntje45')

    def test_password_reset(self):
        # Setup: create a user.
        new_user_email = 'nijntje94@hetkonijntje.nl'
        new_user_password = 'password'
        response = self.client.post(self.user_create_api_url, {'email': new_user_email,
                                                               'password': new_user_password})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        user_id = response.data['id']
        self.assertEqual(len(mail.outbox), 1)

        # Test: resetting a password for an inactive user shouldn't be allowed.
        response = self.client.put(self.user_password_reset_api_url, json.dumps({'email': new_user_email}), 'application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)

        # Setup: activate the newly created user and logout.
        activation_key = RegistrationProfile.objects.filter(user__email=new_user_email).get().activation_key
        new_user_activation_url = "{0}{1}".format(self.user_activation_api_url, activation_key)
        response = self.client.get(new_user_activation_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.logout()
        
        # Test: resetting the password should now be allowed.
        response = self.client.put(self.user_password_reset_api_url, json.dumps({'email': new_user_email}), 'application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(len(mail.outbox), 2)

        # Setup: get the password reset token and url.
        c = re.compile('.*\/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})\".*', re.DOTALL)
        m = c.match(mail.outbox[1].body)
        password_set_url = '{0}{1}-{2}'.format(self.user_password_set_api_url, m.group(1), m.group(2))

        # Test: check that non-matching passwords produce a validation error.
        passwords = {'new_password1': 'rabbit', 'new_password2': 'rabbitt'}
        response = self.client.put(password_set_url, json.dumps(passwords), 'application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
        self.assertEqual(response.data['new_password2'][0], "The two password fields didn't match.")

        # Test: check that updating the password works when the passwords match.
        passwords['new_password2'] = 'rabbit'
        response = self.client.put(password_set_url, json.dumps(passwords), 'application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        # Test: check that the user can login with the new password.
        self.client.login(username=new_user_email, password=passwords['new_password1'])
        new_user_settings_url = "{0}{1}".format(self.user_settings_api_url, user_id)
        response = self.client.get(new_user_settings_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['email'], new_user_email)

        # Test: check that trying to reuse the password reset link doesn't work.
        response = self.client.put(password_set_url, json.dumps(passwords), 'application/json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, response.data)