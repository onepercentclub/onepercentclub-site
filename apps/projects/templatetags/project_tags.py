from django import template


register = template.Library()


@register.assignment_tag
def get_project(project_id):
    from apps.projects.models import Project
    return Project.objects.get(pk=int(project_id))
