from apps.projects.models import Project
from apps.tasks.models import Task
from django.contrib.sites.models import Site
from django.db import models
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django_extensions.db.fields import ModificationDateTimeField, CreationDateTimeField
from django.conf import settings
from polymorphic import PolymorphicModel
from .managers import ReactionManager, WallPostManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.utils.translation import ugettext as _
from django.utils import translation


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
    # TODO: When this is set to 'deleted' set connected MediaWallPostPhotos to deleted too.
    title = models.CharField(max_length=60)
    text = models.TextField(max_length=WALLPOST_REACTION_MAX_LENGTH, blank=True, default='')
    video_url = models.URLField(max_length=100, blank=True, default='')

    def __unicode__(self):
        return Truncator(self.text).words(10)


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



@receiver(post_save, weak=False, sender=TextWallPost)
def new_wallpost_notification(sender, instance, created, **kwargs):
    post = instance

    # FIXME: Find a better solution for this.
    if Site.objects.get_current().domain in ['localhost:8000', '127.0.0.1:8000']:
        site = 'http://' + Site.objects.get_current().domain
    else:
        site = 'https://' + Site.objects.get_current().domain

    # Project Wall Post
    if isinstance(post.content_object, Project):
        project = post.content_object
        receiver = project.owner
        author = post.author
        link = '/#!/projects/{0}'.format(project.slug)

        # Compose the mail
        # Set the language for the receiver
        translation.activate(receiver.primary_language)
        subject = _('%(author)s has left a message on your project page.') % {'author': author.first_name}
        context = Context({'project': project, 'receiver': receiver, 'author': author, 'link': link, 'site': site})
        text_content = get_template('project_wallpost_new.mail.txt').render(context)
        html_content = get_template('project_wallpost_new.mail.html').render(context)
        translation.deactivate()
        msg = EmailMultiAlternatives(subject=subject, body=text_content, to=[receiver.email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

    # Task Wall Post
    if isinstance(post.content_object, Task):
        task = post.content_object
        receiver = task.author
        author = post.author

        link = '/#!/projects/{0}/tasks/{1}'.format(task.project.slug, task.id)

        # Compose the mail
        translation.activate(receiver.primary_language)
        subject = _('%(author)s has left a message on your task page.') % {'author': author.first_name}
        context = Context({'task': task, 'receiver': receiver, 'author': author, 'link': link, 'site': site})
        text_content = get_template('task_wallpost_new.mail.txt').render(context)
        html_content = get_template('task_wallpost_new.mail.html').render(context)
        translation.deactivate()

        msg = EmailMultiAlternatives(subject=subject, body=text_content, to=[receiver.email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()



@receiver(post_save, weak=False, sender=Reaction)
def new_reaction_notification(sender, instance, created, **kwargs):
    reaction = instance
    post = instance.wallpost

    # FIXME: Find a better solution for this.
    if Site.objects.get_current().domain in ['localhost:8000', '127.0.0.1:8000']:
        site = 'http://' + Site.objects.get_current().domain
    else:
        site = 'https://' + Site.objects.get_current().domain

    # Project Wall Post
    if isinstance(post.content_object, Project):
        project = post.content_object
        receiver = post.author
        author = reaction.author
        link = '/#!/projects/{0}'.format(project.slug)

        # Compose the mail
        # Set the language for the receiver
        translation.activate(receiver.primary_language)
        subject = _('%(author)s commented on your wallpost.') % {'author': author.first_name}
        context = Context({'project': project, 'receiver': receiver, 'author': author, 'link': link, 'site': site})
        text_content = get_template('project_wallpost_reaction_new.mail.txt').render(context)
        html_content = get_template('project_wallpost_reaction_new.mail.html').render(context)
        translation.deactivate()
        msg = EmailMultiAlternatives(subject=subject, body=text_content, to=[receiver.email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

