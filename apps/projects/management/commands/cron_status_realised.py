from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import now
from django.utils.translation import ugettext as _


class Command(BaseCommand):
    args = 'No arguments required'
    help = 'Sets projects to "Done Incomplete" and task status to "Realised" when the deadline is passed'

    def handle(self, *args, **options):
        from apps.projects.models import Project
        from bluebottle.bb_projects.models import ProjectPhase
        from apps.tasks.models import Task

        """ 
        Projects which have expired but have been funded will already have their status 
        set to done-complete so these can be ignored. We only need to update projects which 
        haven't been funded but have expired, or they have been overfunded and have expired.
        """
        try:
            done_incomplete_phase = ProjectPhase.objects.get(slug='done-incomplete')
            self.stdout.write("Found ProjectPhase model with name 'Done Incomplete'")
        except ProjectPhase.DoesNotExist:
            raise CommandError("A ProjectPhase with name 'Done Incomplete' does not exist")

        try:
            done_complete_phase = ProjectPhase.objects.get(slug='done-complete')
            self.stdout.write("Found ProjectPhase model with name 'Done Complete'")
        except ProjectPhase.DoesNotExist:
            raise CommandError("A ProjectPhase with name 'Done Complete' does not exist")

        try:
            campaign_phase = ProjectPhase.objects.get(slug='campaign')
            self.stdout.write("Found ProjectPhase model with name 'Campaign'")
        except ProjectPhase.DoesNotExist:
            raise CommandError("A ProjectPhase with name 'Campaign' does not exist")

        """
        Projects which have at least the funds asked, are still in campaign phase and have not expired 
        need the campaign funded date set to now.
        FIXME: this action should be moved into the code where 'amount_needed' is calculated => when 
               the value is lte 0 then set campaign_funded.
        """
        self.stdout.write("Checking Project funded and still running...")
        Project.objects.filter(amount_needed__lte=0, status=campaign_phase, deadline__gt=now()).update(campaign_funded=now())

        """
        Projects which have at least the funds asked, are still in campaign phase but have expired 
        need to be set to 'done complete' and the campaign ended date set to now.
        Iterate over projects and save them one by one so the receivers get a signal
        """
        self.stdout.write("Checking Project overfunded deadlines...")
        for project in Project.objects.filter(amount_needed__lt=0, status=campaign_phase, deadline__lte=now()).all():
            project.status = done_complete_phase
            project.campaign_ended = now()
            project.save()

        """
        Projects which don't have the funds asked, are still in campaign phase but have expired 
        need to be set to 'done incomplete' and the campaign ended date set to now.
        Iterate over projects and save them one by one so the receivers get a signal
        """
        self.stdout.write("Checking Project unfunded deadlines...")
        for project in Project.objects.filter(status=campaign_phase, deadline__lt=now()).all():
            project.status = done_incomplete_phase
            project.campaign_ended = now()
            project.save()

        """
        Iterate over tasks and save them one by one so the receivers get a signal
        """
        self.stdout.write("Checking Task deadlines...\n\n")
        for task in Task.objects.filter(status='in progress', deadline__lt=now()).all():
            task.status = 'realized'
            task.save()

        self.stdout.write("Successfully updated the status of expired Project and Task models.\n\n")