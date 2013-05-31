import random
import string
from django.core.mail import send_mail
import os
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django_extensions.db.fields import AutoSlugField, ModificationDateTimeField
from djchoices.choices import DjangoChoices, ChoiceItem
from sorl.thumbnail import ImageField
from taggit_autocomplete_modified.managers import TaggableManagerAutocomplete as TaggableManager
from apps.bluebottle_utils.models import Address


# TODO: Make this generic for all user file uploads.
def generate_picture_filename(instance, filename):
    """
    Creates a random directory and file name for uploaded pictures.

    The random directory allows the uploaded images to be evenly spread over
    1296 directories. This allows us to host more files before hitting bad
    performance of the OS filesystem and/or utility programs which can occur
    when a directory has thousands of files.

    An example return value is of this method is:
        'profiles/tw/tws9ea4eqaj37xnu24svp2vwndsytzysa.jpg'
    """

    # Create the upload directory string.
    char_set = string.ascii_lowercase + string.digits
    random_string = ''.join(random.choice(char_set) for i in range(33))
    upload_directory = os.path.join('profiles', random_string[0:2])

    # Get the file extension from the original filename.
    original_filename = os.path.basename(filename)
    file_extension = os.path.splitext(original_filename)[1]

    # Create the normalized path.
    normalized_filename = random_string + file_extension
    return os.path.normpath(os.path.join(upload_directory, normalized_filename))


# Option 3 from Chapter 16: Dealing With the User Model

class BlueBottleUserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        now = timezone.now()
        if not email:
            raise ValueError('The given email address must be set')
        email = BlueBottleUserManager.normalize_email(email)
        user = self.model(email=email, is_staff=False, is_active=True, is_superuser=False,
                          last_login=now, date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        u = self.create_user(email, password, **extra_fields)
        u.is_staff = True
        u.is_active = True
        u.is_superuser = True
        u.save(using=self._db)
        return u


class BlueBottleUser(AbstractBaseUser, PermissionsMixin):
    """
    Inherits from both the AbstractBaseUser and PermissionMixin.
    """
    class Gender(DjangoChoices):
        male = ChoiceItem('male', label=_("Male"))
        female = ChoiceItem('female', label=_("Female"))
        other = ChoiceItem('other', label=_("Other"))

    class Availability(DjangoChoices):
        one_to_four_week = ChoiceItem('1-4_hours_week', label=_("1-4 hours per week"))
        five_to_eight_week = ChoiceItem('5-8_hours_week', label=_("5-8 hours per week"))
        nine_to_sixteen_week = ChoiceItem('9-16_hours_week', label=_("9-16 hours per week"))
        one_to_four_month = ChoiceItem('1-4_hours_month', label=_("1-4 hours per month"))
        five_to_eight_month = ChoiceItem('5-8_hours_month', label=_("5-8 hours per month"))
        nine_to_sixteen_month = ChoiceItem('9-16_hours_month', label=_("9-16 hours per month"))
        lots_of_time = ChoiceItem('lots_of_time', label=_("I have all the time in the world. Bring it on :D"))
        depends_on_task = ChoiceItem('depends', label=_("It depends on the content of the tasks. Challenge me!"))

    class UserType(DjangoChoices):
        person = ChoiceItem('person', label=_("Person"))
        group = ChoiceItem('group', label=_("Group"))
        foundation = ChoiceItem('foundation', label=_("Foundation"))
        school = ChoiceItem('school', label=_("School"))
        company = ChoiceItem('company', label=_("Company"))

    email = models.EmailField(_("email address"), max_length=254, unique=True, db_index=True)
    username = AutoSlugField(_("username"), max_length=30, unique=True, populate_from=('get_username',), db_index=True)
    is_staff = models.BooleanField(_("staff status"), default=False, help_text=_('Designates whether the user can log into this admin site.'))
    is_active = models.BooleanField(_("active"), default=True, help_text=_('Designates whether this user should be treated as active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    updated = ModificationDateTimeField()
    deleted = models.DateTimeField(_("deleted"), null=True, blank=True)
    user_type = models.CharField(_("Member Type"), max_length=25, blank=True, choices=UserType.choices)

    # Public Profile
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    location = models.CharField(_("location"), max_length=100, blank=True)
    website = models.URLField(_("website"), blank=True)
    # TODO Use generate_picture_filename (or something) for upload_to
    picture = ImageField(_("picture"), upload_to='profiles', blank=True)
    about = models.TextField(_("about"), max_length=265, blank=True)
    why = models.TextField(_("why"), max_length=265, blank=True)
    availability = models.CharField(_("availability"), max_length=25, blank=True, choices=Availability.choices)
    # TODO Remove when info has been manually migrated to choice above.
    availability_old = models.CharField(_("availability"), max_length=255, blank=True)

    # Private Settings
    language = models.CharField(_("language"), max_length=5, help_text=_("Language used for website and emails."), choices=settings.LANGUAGES)
    newsletter = models.BooleanField(_("newsletter"), help_text=_("Subscribe to newsletter."), default=False)
    phone_number = models.CharField(_("phone number"), max_length=50, null=True, blank=True)
    gender = models.CharField(_("gender"), max_length=6, blank=True, null=True, choices=Gender.choices)
    birthdate = models.DateField(_("birthdate"), null=True, blank=True)

    # FIXME: These aren't being used. Should they be deleted?
    contribution = models.TextField(_("contribution"), blank=True)
    working_location = models.CharField(_("working location"), max_length=255, blank=True)
    tags = TaggableManager(verbose_name=_("tags"), blank=True)

    objects = BlueBottleUserManager()

    USERNAME_FIELD = 'email'
    # Only email and password is requires to create a user account but this is how you'd require other fields.
    # REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = _('member')
        verbose_name_plural = _('members')

    def clean(self):
        # Automatically set the deleted timestamp.
        if not self.is_active and self.deleted is None:
            self.deleted = timezone.now()
        elif self.is_active and self.deleted is not None:
            self.deleted = None

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """
        The user is identified by their email address.
        """
        return self.email

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])

    def get_username(self):
        """
        Returns text to be used as the username slug.
        """
        if self.first_name or self.last_name:
            # The ideal condition.
            return self.first_name + self.last_name
        if self.email and '@' in self.email:
            # The best we can do if there's no first or last name.
            email_name, domain_part = self.email.strip().rsplit('@', 1)
            return email_name
        else:
            # Valid information isn't in the model but we need to set something so Django doesn't complain.
            return 'x'

    @property
    # For now return the first address found on this user.
    def address(self):
        addresses = self.useraddress_set.all()
        if addresses:
            return addresses[0]
        else:
            return None


class UserAddress(Address):
    class AddressType(DjangoChoices):
        primary = ChoiceItem('primary', label=_("Primary"))
        secondary = ChoiceItem('secondary', label=_("Secondary"))

    address_type = models.CharField(_("address type"), max_length=10, blank=True, choices=AddressType.choices)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("user"))

    class Meta:
        verbose_name = _("user address")
        verbose_name_plural = _("user addresses")

