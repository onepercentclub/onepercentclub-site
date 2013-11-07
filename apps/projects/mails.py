from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context


def mail_project_funded_internal(project):
    context = Context({'project': project,
                       'link': '/go/projects/{0}'.format(project.slug),
                       'site': 'https://{0}'.format(Site.objects.get_current().domain)})
    subject = "A project has been funded"
    text_content = get_template('project_funded_internal.mail.txt').render(context)
    html_content = get_template('project_funded_internal.mail.html').render(context)
    msg = EmailMultiAlternatives(subject=subject, body=text_content, to=['projects@onepercentclub.com'])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
