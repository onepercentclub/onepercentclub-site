from apps.projects.models import Project
from apps.wallposts.models import TextWallPost
from async.task import Task
from django.contrib.sites.models import Site
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.utils.translation import ugettext as _
from celery import task


@receiver(post_save, weak=False, sender=TextWallPost)
def new_wallpost_notification(sender, instance, created, **kwargs):

    # we only want to send a mail on a newly created wallpost.
    if not created:
        return

    post = instance

    # Project Wall Post
    if isinstance(post.content_object, Project):
        project = post.content_object
        receiver = project.owner
        author = post.author
        domain = Site.objects.get_current().domain
        link = 'https://' + domain + '/#!/projects/' + project.slug

        # Compose the mail
        subject = _('%(author)s has left a message on your project page.') % {'author': author.first_name}
        context = Context({'project': project, 'receiver': receiver, 'author': author, 'link': link})
        text_content = get_template('project_wallpost_new.mail.txt').render(context)
        html_content = get_template('project_wallpost_new.mail.html').render(context)

        msg = EmailMultiAlternatives(subject=subject, body=text_content, to=[receiver.email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

    # Task Wall Post
    if isinstance(post.content_object, Task):
        task = post.content_object
        receiver = task.owner
        author = post.author
        domain = Site.objects.get_current().domain
        link = 'https://' + domain + '/#!/project/' + task.project.slug + '/tasks/' + task.id

        # Compose the mail
        subject = _('%(author)s has left a message on your task page.') % {'author': author.first_name}
        context = Context({'task': task, 'receiver': receiver, 'author': author, 'link': link})
        text_content = get_template('task_wallpost_new.mail.txt').render(context)
        html_content = get_template('task_wallpost_new.mail.html').render(context)

        msg = EmailMultiAlternatives(subject=subject, body=text_content, to=[receiver.email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()


@receiver(post_save, weak=False, sender=TextWallPost)
def new_reaction_notification(sender, instance, created, **kwargs):
    reaction = instance
    post = instance.wallpost

    # we only want to send a mail on a newly created wallpost.
    if not created:
        return

