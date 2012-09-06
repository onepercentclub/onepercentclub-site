import os
import random
import string

from django.conf import settings, global_settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

from django_extensions.db.fields import AutoSlugField
from djchoices.choices import DjangoChoices, ChoiceItem
from sorl.thumbnail import ImageField
from taggit.managers import TaggableManager

from apps.bluebottle_utils.models import Address


class Language(models.Model):
    """
    A Language that user can speak write. This is separate from the user
    interface language.
    """

    # TODO: Pre-populate this model with the languages from global_settings.
    language = models.CharField(_("language"), max_length=5, unique=True,
                                choices=global_settings.LANGUAGES)

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


class UserProfileCreationError(Exception):
    """ The UserPofile could not be created. """

    pass


# The UserProfile class is setup as per the recommendations in the Django
# documentation:
# https://docs.djangoproject.com/en/1.4/topics/auth/#storing-additional-information-about-users
class UserProfile(models.Model):
    """
    Additional information about a user.
    """

    class Gender(DjangoChoices):
        male = ChoiceItem('male', label=_("Male"))
        female = ChoiceItem('female', label=_("Female"))
        other = ChoiceItem('other', label=_("Other"))

    # The Django User model
    user = models.OneToOneField(User, verbose_name=_("user"))
    slug = AutoSlugField(_("slug"), max_length=30, unique=True,
                         populate_from=('get_username',), overwrite=True)

    # Settings
    interface_language = models.CharField(_("interface language"),
        max_length=5, null=True, blank=True, choices=settings.LANGUAGES
    )
    newsletter = models.BooleanField(
        _("newsletter"), help_text=_("Subscribe to newsletter."),
        default=False
    )

    # Basic profile information
    birthdate = models.DateField(_("birthdate"), null=True, blank=True)
    gender = models.CharField(_("gender"),
        max_length=6, blank=True,
        null=True, choices=Gender.choices
    )
    location = models.CharField(_("location"), max_length=100, blank=True)
    website = models.URLField(_("website"), blank=True, max_length=255)
    # TODO Use generate_picture_filename (or something) for upload_to
    picture = ImageField(_("picture"),
        upload_to='profiles', null=True, blank=True
    )
    languages = models.ManyToManyField(Language,
        blank=True, verbose_name=_("languages")
    )
    deleted = models.DateTimeField(_("deleted"), null=True, blank=True)

    # In-depth profile information
    about = models.TextField(_("about"), blank=True)
    why = models.TextField(_("why"), blank=True)
    contribution = models.TextField(_("contribution"), blank=True)
    availability = models.CharField(_("availability"),
        max_length=255, blank=True
    )
    working_location = models.CharField(_("working location"),
        max_length=255, blank=True
    )

    tags = TaggableManager(verbose_name=_("tags"), blank=True)

    def __unicode__(self):
        try:
            return self.user.username
        except User.DoesNotExist:
            return str(self.pk)

    @property
    def get_username(self):
        return self.user.username

    # Override save() to prevent UserProfiles from being created
    # without a corresponding User.
    # http://stackoverflow.com/questions/2307943/django-overriding-the-model-create-method
    def save(self, *args, **kwargs):
        if not self.pk:
            # The object is not in the database yet because it doesn't have a pk.
            if not hasattr(self, 'user'):
                raise UserProfileCreationError(
                    "A UserProfile cannot be created without a User. "
                    "Creating a User will automatically create the UserProfile."
                )

        super(UserProfile, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        """ Get the URL for the current user's profile. """

        return ('userprofile_detail', (), {
            'slug': self.slug
        })

    class Meta:
        verbose_name = _("user profile")
        verbose_name_plural = _("user profiles")


# Ensures that UserProfile and User instances stay in sync.
def sync_user_profile(sender, instance, created, **kwargs):
    if created:
        # Create a UserProfile whenever a User is created
        UserProfile.objects.create(user=instance)
    else:
        # Save the UserProfile to update the AutoSlugField when a User is saved.
        user_profile = instance.get_profile()
        # TODO In Django 1.5 this can be changed to only save the 'slug' field:
        # https://docs.djangoproject.com/en/dev/ref/models/instances/#the-pk-property
        user_profile.save()

post_save.connect(sync_user_profile, sender=User)


class UserAddress(Address):
    class AddressType(DjangoChoices):
        home = ChoiceItem('home', label=_("Home"))
        other = ChoiceItem('other', label=_("Other"))

    type = models.CharField(_("address type"), max_length=6, blank=True,
                            choices=AddressType.choices)
    user_profile = models.ForeignKey(UserProfile,
        verbose_name=_("user profile")
    )

    class Meta:
        verbose_name = _("user address")
        verbose_name_plural = _("user addresses")
