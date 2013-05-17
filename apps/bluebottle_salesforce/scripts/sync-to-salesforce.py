# Script to sync data to SaleForce.
#
# Run with:
# ./manage.py runscript sync-to-salesforce

# TODO User python logging.
from apps.projects.models import Project
from django.contrib.auth.models import User


def run():
    projects = Project.objects.all()
    for project in projects:
        print project.title
        # Process projects here.
        # You should be able to update the salesforce project model by:
        #   * finding the corresponding salesforce project
        #   * setting all the fields you need to save from the project to the sales force project
        #   * saving the salesforce project

    users = User.objects.all()
    for user in users:
        print user.username
        # Process users here.
        # You should be able to update the salesforce user model by:
        #   * finding the corresponding salesforce user
        #   * setting all the fields you need to save from the user to the sales force user
        #   * saving the salesforce user


    # Add other models you need to process here.
