from apps.projects.models import Project, ProjectPhase
from apps.projects.serializers import ProjectPreviewSerializer


def prepare_money_donated():
    projects = Project.objects.filter(status__in=[ProjectPhase.objects.get(slug="campaign"),
                                                  ProjectPhase.objects.get(slug="done-complete")]).all()

    for project in projects:
        try:
            # TODO: fix donation
            project.projectcampaign.update_money_donated()
            project.update_popularity()
        except Exception:
            pass


def prepare_project_images():
    projects = Project.objects.exclude(status__in=[ProjectPhase.objects.get(slug="plan-new"),
                                                   ProjectPhase.objects.get(slug="done-stopped")]).all()

    for project in projects:
        try:
            ProjectPreviewSerializer().to_native(project)
        except Exception:
            # Don't raise errors on corrupt or missing images
            pass

