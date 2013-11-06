from django.db import models
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django_extensions.db.fields import ModificationDateTimeField, CreationDateTimeField
from django.conf import settings
from apps.fund.models import Donation, DonationStatuses
from polymorphic import PolymorphicModel
from .managers import ReactionManager, WallPostManager


WALLPOST_TEXT_MAX_LENGTH = getattr(settings, 'WALLPOST_TEXT_MAX_LENGTH', 300)
WALLPOST_REACTION_MAX_LENGTH = getattr(settings, 'WALLPOST_REACTION_MAX_LENGTH', 300)


class WallPost(PolymorphicModel):
    """
    The WallPost base class. This class will never be used directly because the content of a WallPost is always defined
    in the child classes.

    Implementation Note: Normally this would be an abstract class but it's not possible to make this an abstract class
    and have the polymorphic behaviour of sorting on the common fields.
    """

    # The user who wrote the wall post. This can be empty to support wall posts without users (e.g. anonymous
    # TextWallPosts, system WallPosts for donations etc.)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('author'), related_name="%(class)s_wallpost", blank=True, null=True)
    editor = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('editor'), blank=True, null=True, help_text=_("The last user to edit this wallpost."))

    # The metadata for the wall post.
    created = CreationDateTimeField(_('created'))
    updated = ModificationDateTimeField(_('updated'))
    deleted = models.DateTimeField(_('deleted'), blank=True, null=True)
    ip_address = models.IPAddressField(_('IP address'), blank=True, null=True, default=None)

    # Generic foreign key so we can connect it to any object.
    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'), related_name="content_type_set_for_%(class)s")
    object_id = models.PositiveIntegerField(_('object ID'))
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    # Manager
    objects = WallPostManager()

    class Meta:
        ordering = ('created',)

    def __unicode__(self):
        return str(self.id)


class MediaWallPost(WallPost):
    # The content of the wall post.
    title = models.CharField(max_length=60)
    text = models.TextField(max_length=WALLPOST_REACTION_MAX_LENGTH, blank=True, default='')
    video_url = models.URLField(max_length=100, blank=True, default='')

    def __unicode__(self):
        return Truncator(self.text).words(10)

    def save(self, *args, **kwargs):
        super(MediaWallPost, self).save(*args, **kwargs)

        # Mark the photos as deleted when the MediaWallPost is deleted.
        if self.deleted:
            for photo in self.photos.all():
                if not photo.deleted:
                    photo.deleted = self.deleted
                    photo.save()


class MediaWallPostPhoto(models.Model):
    mediawallpost = models.ForeignKey(MediaWallPost, related_name='photos', null=True, blank=True)
    photo = models.ImageField(upload_to='mediawallpostphotos')
    deleted = models.DateTimeField(_('deleted'), blank=True, null=True)
    ip_address = models.IPAddressField(_('IP address'), blank=True, null=True, default=None)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('author'), related_name="%(class)s_wallpost_photo", blank=True, null=True)
    editor = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('editor'), blank=True, null=True, help_text=_("The last user to edit this wallpost photo."))


class TextWallPost(WallPost):
    # The content of the wall post.
    text = models.TextField(max_length=WALLPOST_REACTION_MAX_LENGTH)

    def __unicode__(self):
        return Truncator(self.text).words(10)


class SystemWallPost(WallPost):
    # The content of the wall post.
    text = models.TextField(max_length=WALLPOST_REACTION_MAX_LENGTH, blank=True)

    # Generic foreign key so we can connect any object to it.
    related_type = models.ForeignKey(ContentType, verbose_name=_('related type'))
    related_id = models.PositiveIntegerField(_('related ID'))
    related_object = generic.GenericForeignKey('related_type', 'related_id')

    def __unicode__(self):
        return Truncator(self.text).words(10)


class Reaction(models.Model):
    """
    A user reaction or comment to a WallPost. This model is based on the Comments model from django.contrib.comments.
    """

    # Who posted this reaction. User will need to be logged in to make a reaction.
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('author'), related_name='wallpost_reactions')
    editor = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('editor'), blank=True, null=True, related_name='+', help_text=_("The last user to edit this reaction."))

    # The reaction text and the wallpost it's a reaction to.
    text = models.TextField(_('reaction text'), max_length=WALLPOST_REACTION_MAX_LENGTH)
    wallpost = models.ForeignKey(WallPost, related_name='reactions')

    # Metadata for the reaction.
    created = CreationDateTimeField(_('created'))
    updated = ModificationDateTimeField(_('updated'))
    deleted = models.DateTimeField(_('deleted'), blank=True, null=True)
    ip_address = models.IPAddressField(_('IP address'), blank=True, null=True, default=None)

    # Manager
    objects = ReactionManager()
    objects_with_deleted = models.Manager()

    class Meta:
        ordering = ('created',)
        verbose_name = _('Reaction')
        verbose_name_plural = _('Reactions')

    def __unicode__(self):
        s = "{0}: {1}".format(self.author.get_full_name(), self.text)
        return Truncator(s).words(10)


@receiver(post_save, weak=False, sender=Donation)
def create_donation_post(sender, instance, **kwargs):
    donation = instance
    if donation.status in [DonationStatuses.paid, DonationStatuses.pending]:
        try:
            donation_type = ContentType.objects.get_for_model(donation)
            post = SystemWallPost.objects.filter(related_id=donation.id).filter(related_type=donation_type).get()
        except SystemWallPost.DoesNotExist:
            if donation.donation_type == Donation.DonationTypes.one_off:
                post = SystemWallPost()
                post.content_object = donation.project
                post.related_object = donation
                post.author = donation.user
                post.ip = '127.0.0.1'
                post.save()

