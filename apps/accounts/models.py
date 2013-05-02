import random
import string
from django.utils import timezone
import os
from django.conf import settings, global_settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils.translation import ugettext_lazy as _
from djchoices.choices import DjangoChoices, ChoiceItem
from sorl.thumbnail import ImageField
from taggit_autocomplete_modified.managers import TaggableManagerAutocomplete as TaggableManager
from apps.bluebottle_utils.models import Address


class Language(models.Model):
    """
    A Language that user can speak write. This is separate from the user
    interface language.
    """

    # TODO: Pre-populate this model with the languages from global_settings.
    language = models.CharField(_("language"), max_length=5, unique=True, choices=global_settings.LANGUAGES)

    def __unicode__(self):
        return self.get_language_display()


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


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, username=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=UserManager.normalize_email(email),
        )

        user.set_password(password)
        user.username = username
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email,
            password=password,
        )
        user.is_admin = True
        user.username = email
        user.save(using=self._db)
        return user


# http://procrastinatingdev.com/django/using-configurable-user-models-in-django-1-5/
class User(AbstractBaseUser):
    """
    User model
    """
    class Gender(DjangoChoices):
        male = ChoiceItem('male', label=_("Male"))
        female = ChoiceItem('female', label=_("Female"))
        other = ChoiceItem('other', label=_("Other"))

    email = models.EmailField(max_length=254, unique=True, db_index=True)
    username = models.CharField(_('User name'), max_length=254, null=True)

    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    is_active = models.BooleanField(_('active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    # Settings
    interface_language = models.CharField(_("interface language"), max_length=5, null=True, blank=True, choices=settings.LANGUAGES)
    newsletter = models.BooleanField(_("newsletter"), help_text=_("Subscribe to newsletter."), default=False)

    # Basic profile information
    birthdate = models.DateField(_("birthdate"), null=True, blank=True)
    gender = models.CharField(_("gender"), max_length=6, blank=True, null=True, choices=Gender.choices)
    location = models.CharField(_("location"), max_length=100, blank=True)
    website = models.URLField(_("website"), blank=True, max_length=255)
    # TODO Use generate_picture_filename (or something) for upload_to
    picture = ImageField(_("picture"), upload_to='profiles', null=True, blank=True)
    languages = models.ManyToManyField(Language, blank=True, verbose_name=_("languages"))
    deleted = models.DateTimeField(_("deleted"), null=True, blank=True)

    # In-depth profile information
    about = models.TextField(_("about"), blank=True)
    why = models.TextField(_("why"), blank=True)
    contribution = models.TextField(_("contribution"), blank=True)
    availability = models.CharField(_("availability"), max_length=255, blank=True)
    working_location = models.CharField(_("working location"), max_length=255, blank=True)

    tags = TaggableManager(verbose_name=_("tags"), blank=True)

    objects = UserManager()
    USERNAME_FIELD = 'email'

    def __unicode__(self):
        return self.email

    @property
    # for now return the first address found on this user.
    def address(self):
        addresses = self.useraddress_set.all()
        if addresses:
            return addresses[0]
        else:
            return None

    @models.permalink
    def get_absolute_url(self):
        """ Get the URL for the current user's profile. """

        return ('user_detail', (), {
            'slug': self.slug
        })


class UserAddress(Address):
    class AddressType(DjangoChoices):
        home = ChoiceItem('home', label=_("Home"))
        other = ChoiceItem('other', label=_("Other"))

    type = models.CharField(_("address type"), max_length=6, blank=True, choices=AddressType.choices)
    user_profile = models.ForeignKey(User, verbose_name=_("user profile"))

    class Meta:
        verbose_name = _("user address")
        verbose_name_plural = _("user addresses")

