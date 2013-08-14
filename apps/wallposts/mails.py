from apps.projects.models import Project
from apps.tasks.models import Task
from apps.wallposts.models import TextWallPost, Reaction
from django.contrib.sites.models import Site
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.utils import translation
from django.utils.translation import ugettext_lazy as _


@receiver(post_save, weak=False, sender=TextWallPost)
def new_wallpost_notification(sender, instance, created, **kwargs):
    post = instance

    site = 'https://' + Site.objects.get_current().domain

    # Project Wall Post
    if isinstance(post.content_object, Project):
        project = post.content_object
        receiver = project.owner
        author = post.author
        link = '/go/projects/{0}'.format(project.slug)

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

    site = 'https://' + Site.objects.get_current().domain

    # Project Wall Post
    if isinstance(post.content_object, Project):
        project = post.content_object
        receiver = post.author
        author = reaction.author
        link = '/go/projects/{0}'.format(project.slug)

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

