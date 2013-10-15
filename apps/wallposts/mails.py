"""
The prescribed mail flow is as follows:

1) Wallposts created

    a) send email to Object owner, if Wallpost author is not the Object owner (except if he already got an email via 2c).

2) Reaction created on Wallpost

    a) send email to Object owner, if Reaction author is not the Object ower.
    b) send email to Wallpost author, if Reaction author is not the Wallpost author.
    c) send email to other Reaction authors that are not the Object owner or the Wallpost author (they already get an
       email, see above).

Example::

    Object by A
    |
    +-- Wallpost by B
        |
        +-- Reaction by C


Basically, everyone in the tree gets an email if a new Wallpost or Reaction is created, except the author if the newly
created Wallpost or Reaction. But, every unique person shall receive at most 1 email.

"""
import logging

from django.contrib.sites.models import Site
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from apps.projects.models import Project
from apps.tasks.models import Task
from apps.wallposts.models import TextWallPost, Reaction


logger = logging.getLogger(__name__)


def send_mail(template_name, subject, obj, to, **kwargs):
    translation.activate(to.primary_language)

    kwargs.update({
        'project': obj,
        'receiver': to,
        'link': '/go/projects/{0}'.format(obj.slug),
        'site': 'https://{0}'.format(Site.objects.get_current().domain)
    })

    context = Context(kwargs)
    text_content = get_template('{0}.txt'.format(template_name)).render(context)
    html_content = get_template('{0}.html'.format(template_name)).render(context)

    translation.deactivate()

    msg = EmailMultiAlternatives(subject=subject, body=text_content, to=[to.email])
    msg.attach_alternative(html_content, "text/html")

    return msg.send()


def handle_project_feedback_mails(wallpost_or_reaction):
    if isinstance(wallpost_or_reaction, TextWallPost):
        wallpost = wallpost_or_reaction
        reaction = None
    elif isinstance(wallpost_or_reaction, Reaction):
        wallpost = wallpost_or_reaction.wallpost
        reaction = wallpost_or_reaction
    else:
        logger.critical('Cannot sent out mails: Unknown how to handle object "%s".', wallpost_or_reaction)
        return

    obj = wallpost.content_object
    obj_owner = obj.owner

    wallpost_author = wallpost.author
    reaction_author = reaction.author if reaction is not None else None

    mailed_users = set()

    if reaction_author:
        # Implement 2c: send email to other Reaction authors that are not the Object owner or the Wallpost author.
        reactions = wallpost.reactions.exclude(Q(author=wallpost_author) | Q(author=obj_owner) | Q(author=reaction_author))
        for r in reactions:
            if r.author not in mailed_users:
                send_mail(
                    template_name='project_wallpost_reaction_new.mail',
                    subject=_('%(author)s commented on a wallpost you reacted on.') % {'author': reaction_author.first_name},
                    obj=obj,
                    to=r.author,
                    author=reaction_author
                )
                mailed_users.add(r.author)

        # Implement 2b: send email to Wallpost author, if Reaction author is not the Wallpost author.
        if reaction_author != wallpost_author:
            if reaction_author not in mailed_users:
                send_mail(
                    template_name='project_wallpost_reaction_new.mail',
                    subject=_('%(author)s commented on your wallpost.') % {'author': reaction_author.first_name},
                    obj=obj,
                    to=wallpost_author,
                    author=reaction_author
                )
                mailed_users.add(reaction_author)


    # Implement 1a, 2a: send email to Object owner, if Wallpost/Reaction author is not the Object owner.
    if wallpost_author != obj_owner and reaction_author != obj_owner:
        if obj_owner not in mailed_users:
            send_mail(
                template_name='project_wallpost_new.mail',
                subject=_('%(author)s has left a message on your project page.') % {'author': wallpost_author.first_name},
                obj=obj,
                to=obj_owner,
                author=wallpost_author
            )


@receiver(post_save, weak=False, sender=TextWallPost)
def new_wallpost_notification(sender, instance, created, **kwargs):
    post = instance

    site = 'https://' + Site.objects.get_current().domain

    # Project Wall Post
    if isinstance(post.content_object, Project):
        project = post.content_object
        project_owner = project.owner
    
        post_author = post.author

        # Implement 1a: send email to Object owner, if Wallpost author is not the Object owner.
        if post_author != project_owner:
            send_mail(
                template_name='project_wallpost_new.mail',
                subject=_('%(author)s has left a message on your project page.') % {'author': post_author.first_name},
                obj=project,
                to=project_owner,
                author=post_author
            )

    # Task Wall Post
    if isinstance(post.content_object, Task):
        task = post.content_object
        receiver = task.author
        author = post.author

        link = '/go/projects/{0}/tasks/{1}'.format(task.project.slug, task.id)

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

    # Project Wall Post
    if isinstance(post.content_object, Project):
        project = post.content_object
        project_owner = project.owner

        post_author = post.author
        reaction_author = reaction.author

        # Make sure users only get mailed once!
        mailed_users = set()
    
        # Implement 2c: send email to other Reaction authors that are not the Object owner or the post author.
        reactions = post.reactions.exclude(Q(author=post_author) | Q(author=project_owner) | Q(author=reaction_author))
        for r in reactions:
            if r.author not in mailed_users:
                send_mail(
                    template_name='project_wallpost_reaction_same_wallpost.mail',
                    subject=_('%(author)s commented on a post you reacted on.') % {'author': reaction_author.first_name},
                    obj=project,
                    to=r.author,
                    author=reaction_author
                )
                mailed_users.add(r.author)

        # Implement 2b: send email to post author, if Reaction author is not the post author.
        if reaction_author != post_author:
            if reaction_author not in mailed_users:
                send_mail(
                    template_name='project_wallpost_reaction_new.mail',
                    subject=_('%(author)s commented on your post.') % {'author': reaction_author.first_name},
                    obj=project,
                    to=post_author,
                    author=reaction_author
                )
                mailed_users.add(post_author)

        # Implement 2a: send email to Object owner, if Reaction author is not the Object owner.
        if reaction_author != project_owner:
            if project_owner not in mailed_users:
                send_mail(
                    template_name='project_wallpost_reaction_project.mail',
                    subject=_('%(author)s commented on your project page.') % {'author': reaction_author.first_name},
                    obj=project,
                    to=project_owner,
                    author=post_author
                )
