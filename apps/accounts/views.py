from apps.bluebottle_drf2.permissions import IsCurrentUserOrReadOnly, IsCurrentUser
from django.contrib.auth import login, get_user_model
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import AnonymousUser
from django.contrib.sites.models import get_current_site
from django.conf import settings
from django.template import loader
from django.contrib.auth.tokens import default_token_generator
from django.http import Http404
from django.utils.http import base36_to_int, int_to_base36
from django.utils import translation

from registration.models import RegistrationProfile
from rest_framework import generics
from rest_framework import response
from rest_framework import status
from rest_framework import views
import re

from .models import BlueBottleUser
from .serializers import (CurrentUserSerializer, UserProfileSerializer, UserSettingsSerializer, UserCreateSerializer,
                          PasswordResetSerializer, PasswordSetSerializer)


# API views

class UserProfileDetail(generics.RetrieveUpdateAPIView):
    model = BlueBottleUser
    serializer_class = UserProfileSerializer
    permission_classes = (IsCurrentUserOrReadOnly,)


class UserSettingsDetail(generics.RetrieveUpdateAPIView):
    model = BlueBottleUser
    serializer_class = UserSettingsSerializer
    permission_classes = (IsCurrentUser,)


class CurrentUser(generics.RetrieveAPIView):
    model = BlueBottleUser
    serializer_class = CurrentUserSerializer

    def get_object(self, queryset=None):
        if isinstance(self.request.user, AnonymousUser):
            raise Http404()
        return self.request.user


class UserCreate(generics.CreateAPIView):
    model = BlueBottleUser
    serializer_class = UserCreateSerializer

    def get_name(self):
        return "Users"

    def post_save(self, obj, created=False):
        # Create a RegistrationProfile and email its activation key to the User.
        registration_profile = RegistrationProfile.objects.create_profile(obj)

        if created:
            current_site = get_current_site(self.request)

            # Check the referer to determine the visitor's language. If not available
            # use the default request language (English)
            referer = self.request.META['HTTP_REFERER']
            if referer:
                referer = re.sub('^https?:\/\/', '', referer).split('/')
                referer_path = u'/' + u'/'.join(referer[1:])
                language = translation.get_language_from_path(referer_path)
            else:
                language = self.request.LANGUAGE_CODE[:2]
            translation.activate(language)
            site_name = current_site.name
            domain = current_site.domain
            site = 'https://' + domain
            c = {
                'email': obj.email,
                'site': site,
                'site_name': site_name,
                'user': obj,
                'activation_key': registration_profile.activation_key,
                'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                'LANGUAGE_CODE': language
            }
            subject_template_name = 'registration/activation_email_subject.txt'

            extension = getattr(settings, 'HTML_ACTIVATION_EMAIL', False) and  'html' or 'txt'
            email_template_name = 'registration/activation_email.' + extension

            subject = loader.render_to_string(subject_template_name, c)
            # Email subject *must not* contain newlines
            subject = ''.join(subject.splitlines())
            email = loader.render_to_string(email_template_name, c)

            obj.email_user(subject, email)
            # Don't forget to deactivate, otherwise we switch the language for subsequent users of this thread!
            translation.deactivate() 

class UserActivate(generics.RetrieveAPIView):
    serializer_class = CurrentUserSerializer

    def login_user(self, request, user):
        # Auto login the user after activation
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        return login(request, user)

    def get(self, request, *args, **kwargs):
        activation_key = self.kwargs.get('activation_key', None)
        activated_user = RegistrationProfile.objects.activate_user(activation_key)
        if activated_user:
            # Log the user in when the user has been activated and return the current user object.
            self.login_user(request, activated_user)
            self.object = activated_user
            serializer = self.get_serializer(self.object)
            return response.Response(serializer.data)
        # Return 400 when the activation didn't work.
        return response.Response(status=status.HTTP_400_BAD_REQUEST)


class PasswordReset(views.APIView):
    """
    Allows a password reset to be initiated for valid users in the system. An email will be sent to the user with a
    password reset link upon successful submission.
    """
    serializer_class = PasswordResetSerializer

    def save(self, password_reset_form, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html', use_https=True,
             token_generator=default_token_generator, from_email=None, request=None):
        """
        Generates a one-use only link for resetting password and sends to the user. This has been ported from the
        Django PasswordResetForm to allow HTML emails instead of plaint text emails.
        """
        # TODO: Create a patch to Django to use user.email_user instead of send_email.
        for user in password_reset_form.users_cache:
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            site = 'https://' + domain
            c = {
                'email': user.email,
                'site': site,
                'site_name': site_name,
                'uid': int_to_base36(user.pk),
                'user': user,
                'token': token_generator.make_token(user),
                'LANGUAGE_CODE': self.request.LANGUAGE_CODE[:2]
            }
            subject = loader.render_to_string(subject_template_name, c)
            # Email subject *must not* contain newlines
            subject = ''.join(subject.splitlines())
            email = loader.render_to_string(email_template_name, c)
            user.email_user(subject, email)

    def put(self, request, *args, **kwargs):
        password_reset_form = PasswordResetForm()
        serializer = PasswordResetSerializer(password_reset_form=password_reset_form, data=request.DATA)
        if serializer.is_valid():
            opts = {
                # Always use https
                'use_https': True,
                'from_email': settings.DEFAULT_FROM_EMAIL,
                'request': request,
            }
            # TODO: When Django Password Reset form uses user.email_user() this can be enabled and the self.save() can
            #       be removed.
            # password_reset_form.save(**opts)  # Sends the email
            self.save(password_reset_form, **opts)  # Sends the email

            return response.Response(status=status.HTTP_200_OK)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordSet(views.APIView):
    """
    Allows a new password to be set in the resource that is a valid password reset hash.
    """
    serializer_class = PasswordSetSerializer

    def put(self, request, *args, **kwargs):
        # The uidb36 and the token are checked by the URLconf.
        uidb36 = self.kwargs.get('uidb36')
        token = self.kwargs.get('token')
        UserModel = get_user_model()
        try:
            uid_int = base36_to_int(uidb36)
            user = UserModel._default_manager.get(pk=uid_int)
        except (ValueError, OverflowError, UserModel.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            password_set_form = SetPasswordForm(user)
            serializer = PasswordSetSerializer(password_set_form=password_set_form, data=request.DATA)
            if serializer.is_valid():
                password_set_form.save()  # Sets the password
                return response.Response(status=status.HTTP_200_OK)
            return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return response.Response(status=status.HTTP_404_NOT_FOUND)
