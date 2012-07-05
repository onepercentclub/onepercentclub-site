import os
import random
import string

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django_extensions.db.fields import AutoSlugField
from sorl.thumbnail import ImageField
from djchoices.choices import DjangoChoices, ChoiceItem

from apps.bluebottle_utils.models import Address


# TODO Add a list of Languages with translations.
# list of languages here but it seems like a personal project:
# https://github.com/exalted/djangomissing
LANGUAGES = (
    ('en', "English"),
    ('fr', "French"),
    ('nl', "Dutch"),
)


class Language(models.Model):
    """
    A spoken / written Language.
    """
    language = models.CharField(max_length=2, unique=True, choices=LANGUAGES)

    def __unicode__(self):
        return dict(LANGUAGES)[self.language]


def generate_picture_filename(instance, filename):
    """
    Creates a random directory and file name for uploaded pictures.

    The random directory allows the uploaded images to be evenly spread over
    1296 directories. This allows us to host more files before hitting bad
    performance of the OS filesystem and/or utility programs which can occur
    when a directory has thousands of files.

    An example return value is of this method is:
        'profiles/tw/s9ea4eqaj37xnu24svp2vwndsytzysa.jpg'
    """
    # Create the upload directory string.
    char_set = string.ascii_lowercase + string.digits
    random_string = ''.join(random.choice(char_set) for i in range(33))
    dir_length = 2
    upload_directory = os.path.join('profiles', random_string[0:dir_length])

    # Get the file extension from the original filename.
    original_filename = os.path.basename(filename)
    file_extension = os.path.splitext(original_filename)[1]

    # Create the normalized path.
    normalized_filename = random_string[dir_length:] + file_extension
    return os.path.normpath(os.path.join(upload_directory, normalized_filename))


# The UserProfile class is setup as per the recommendations in the Django
# documentation:
# https://docs.djangoproject.com/en/1.4/topics/auth/#storing-additional-information-about-users
class UserProfile(models.Model):
    """
    Additional information about a user.
    """
    class Gender(DjangoChoices):
        male = ChoiceItem('male', label="Male")
        female = ChoiceItem('female', label="Female")
        other = ChoiceItem('other', label="Other")

    # The Django User model
    user = models.OneToOneField(User)
    slug = AutoSlugField(max_length=30, unique=True,
                         populate_from=('get_username',), overwrite=True)

    # Settings
    # TODO This should show a list of all the translations we have.
    interface_language = models.CharField(max_length=5)
    newsletter = models.BooleanField('Send Newsletter', default=False)

    # Basic profile information
    birthdate = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=6, blank=True, choices=Gender.choices)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True, max_length=255)
    picture = ImageField(upload_to=generate_picture_filename,
                         null=True, blank=True)
    languages = models.ManyToManyField(Language, blank=True)
    deleted = models.DateTimeField(null=True, blank=True)

    # In-depth profile information
    about = models.TextField(blank=True)
    why = models.TextField(blank=True)
    contribution = models.CharField(max_length=255, blank=True)
    availability = models.CharField(max_length=255, blank=True)
    working_location = models.CharField(max_length=255, blank=True)

    def __unicode__(self):
        return self.user.username

    @property
    def get_username(self):
        return self.user.username

    class Meta:
        verbose_name_plural = "User Profiles"


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
        home = ChoiceItem('home', label="Home")
        other = ChoiceItem('other', label="Other")

    type = models.CharField(max_length=6, blank=True, choices=AddressType.choices)
    user_profile = models.ForeignKey(UserProfile)

    class Meta:
        verbose_name_plural = "User Addresses"
