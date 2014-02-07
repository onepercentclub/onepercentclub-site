from django import template


register = template.Library()


@register.assignment_tag
def get_project(project_id):
    from apps.onepercent_projects.models import Project
    return Project.objects.get(pk=int(project_id))
