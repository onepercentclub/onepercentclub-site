import hashlib
from apps.reactions.managers import ReactionManager
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.conf import settings


REACTION_MAX_LENGTH = getattr(settings, 'REACTION_MAX_LENGTH', 500)


class Reaction(models.Model):
    """
    A user reaction about some object. This model is based on the Comments model
    from django.contrib.comments.
    """

    # Content-object field.
    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'), related_name="content_type_set_for_%(class)s")
    object_pk = models.TextField(_('object ID'))
    content_object = generic.GenericForeignKey(ct_field="content_type", fk_field="object_pk")

    # Who posted this reaction. User will need to be logged in to make re
    author = models.ForeignKey(User, verbose_name=_('author'), blank=True, null=True, related_name="%(class)s_reactions")
    reaction = models.TextField(_('reaction'), max_length=REACTION_MAX_LENGTH)

    # Metadata about the reaction.
    created = models.DateTimeField(_('date/time submitted'), default=None)
    deleted = models.DateTimeField(_('date/time deleted'), blank=True, null=True)
    ip_address = models.IPAddressField(_('IP address'))

    # TODO do we want this?
    site = models.ForeignKey(Site)

    slug = models.SlugField(editable=False, max_length=40)

    # Manager
    objects = ReactionManager()

    class Meta:
        ordering = ('created',)
        verbose_name = _('reaction')
        verbose_name_plural = _('reactions')

    def __unicode__(self):
        return "{0} {1}: {2}...".format(self.author.first_name, self.author.last_name, self.reaction[:50])

    def save(self, *args, **kwargs):
        if self.created is None:
            self.created = timezone.now()
        if self.slug == '':
            # TODO Ensure unique slug.
            self.slug = hashlib.sha1(str(self.content_type) + str(self.object_pk) + str(self.created) + self.ip_address + self.author.username + self.reaction).hexdigest()
        super(Reaction, self).save(*args, **kwargs)
