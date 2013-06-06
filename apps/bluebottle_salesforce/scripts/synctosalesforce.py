# Script to sync data to SaleForce.
#
# Run with:
# ./manage.py runscript sync-to-salesforce
# TODO User python logging.
from apps.accounts.models import BlueBottleUser, UserAddress
from apps.projects.models import Project
from apps.organizations.models import Organization
from apps.tasks.models import Task
from apps.fund.models import Donation, Voucher
from apps.bluebottle_salesforce.models import (SalesforceContact, SalesforceDonation, SalesforceOrganization,
                                               SalesforceProject, SalesforceProjectBudget, SalesforceTask,
                                               SalesforceTaskMembers) #, SalesforceVoucher)


def sync_users(test_run):
    users = BlueBottleUser.objects.all()
    for user in users:
        # Find the corresponding SF user.
        try:
            contact = SalesforceContact.objects.filter(external_id=user.id).get()
        except SalesforceContact.DoesNotExist:
            contact = SalesforceContact()

        # SF Layout: Subscription section - Set all the fields needed to save the user to the SF user.
        contact.category1 = user.user_type
        contact.email = user.email
        contact.user_name = user.username

        # SF Layout: Profile section.
        # Note: SF last_name is required.
        if user.last_name:
            contact.last_name = user.last_name
        else:
            contact.last_name = "1%MEMBER"

        contact.first_name = user.first_name
        contact.member_since = user.date_joined
        contact.why_one_percent_member = user.why
        contact.about_me_us = user.about
        contact.location = user.location
        # The default: Organization(Account) will be 'Individual' as current.
        # Future purpose deactivate and put the Organization website group value
        #contact.Account = "ORG_INDIVIDUAL"
        contact.website = user.website

        # SF Layout: Contact Information section.
        # Note: Fill with the number of activities of a member
        #contact.activity_number =

        # SF Layout: Contact Activity section.
        # -- back-end calculations with Ben
        #contact.amount_of_single_donations
        # -- 20130530 - Not used: discussed with Suzanne,Ben
        #contact.has_n_friends
        #contact.has_given_n_vouchers
        #contact.is_doing_n_tasks
        #contact.number_of_donations
        #contact.support_n_projects
        #contact.total_amount_of_donations
        # -- 20130530 - Not used: discussed with Suzanne,Ben
        #contact.total_number_of_received_messages
        # -- 20130530 - Not used: discussed with Suzanne,Ben
        #contact.total_number_of_sent_messages

        # SF Layout: Administrative (private) section.
        contact.birth_date = user.birthdate

        # Salesforce: needs to be updated to male/female/<empty string> instead m/f
        contact.gender = user.gender

        if user.address:
            contact.mailing_city = user.address.city
            contact.mailing_street = user.address.line1 + ' ' + user.address.line2
            contact.mailing_country = user.address.country.name
            contact.mailing_postal_code = user.address.postal_code
            contact.mailing_state = user.address.state
        else:
            contact.mailing_city = ''
            contact.mailing_street = ''
            contact.mailing_country = ''
            contact.mailing_postal_code = ''
            contact.mailing_state = ''

        # SF Layout: My Skills section.
        # -- Unknown:
        #contact.which_1_would_you_like_to_contribute =
        # -- Unknown:
        #contact.available_time =
        # -- 20130530 - Not used: discussed with Suzanne,Ben
        #contact.where

        # SF Layout: My Settings section.
        # TODO delete: 20130530 - Not used: discussed with Suzanne,Ben
        #contact.receive_emails_for_friend_invitations
        contact.receive_newsletter = user.newsletter
        # TODO delete: 20130530 - Not used: discussed with Suzanne,Ben
        #contact.email_after_a_new_message
        # TODO delete: 20130530 - Not used: discussed with Suzanne,Ben
        #contact.email_after_a_new_public_message
        contact.primary_language = user.primary_language

        # SF Layout: All expertise section. -> 20130530 - TODO website by web-team
        #contact.administration_finance =
        #contact.agriculture_environment
        #contact.architecture
        #contact.computer_ict
        #contact.design
        #contact.economy_business
        #contact.education
        #contact.fund_raising
        #contact.graphic_design
        #contact.health
        #contact.internet_research
        #contact.law_and_politics
        #contact.marketing_pr
        #contact.online_marketing
        #contact.photo_video
        #contact.physics_technique
        #contact.presentations
        #contact.project_management
        #contact.psychology
        #contact.social_work
        #contact.sport_and_development
        #contact.tourism
        #contact.trade_transport
        #contact.translating_writing
        #contact.web_development
        #contact.writing_proposals

        # SF: Other
        contact.external_id = user.id
        # -- 20130530 - discussed with Suzanne, check at Liane
        #contact.tags = user.tags.get()

        # Save the SF user.
        if not test_run:
            contact.save()


# def sync_donations():
#     donations = Donation.objects.all()
#     for donation in donations:
#         # Find the corresponding SF donation.
#         try:
#             sfdonation = SalesforceDonation.objects.filter(external_id=donation.id).get()
#         except SalesforceDonation.DoesNotExist:
#             sfdonation = SalesforceDonation()


#def sync_organizations():
#    organizations = Organization.objects.all()
#    for sforganization in organizations:
#        # Find the corresponding SF organization.
#        try:
#            sforganization = SalesforceOrganization.objects.filter(external_id=sforganization.id).get()
#        except SalesforceOrganization.DoesNotExist:
#            sforganization = SalesforceOrganization()


#def sync_tasks():
#    tasks = Task.objects.all()
#    for task in tasks:
#        # Find the corresponding SF task.
#        try:
#            sftask = SalesforceTask.objects.filter(external_id=task.id).get()
#        except SalesforceTask.DoesNotExist:
#            sftask = SalesforceTask()


# def sync_projects():
#     projects = Project.objects.all()
#     for project in projects:
#         # Find the corresponding SF project.
#         try:
#             sfproject = SalesforceProject.objects.filter(external_id=project.id).get()
#         except SalesforceProject.DoesNotExist:
#             sfproject = SalesforceProject()
#
#         # SF Layout: 1%CLUB Project Detail section.
#         sfproject.amount_at_the_moment = project.money_safe
#         sfproject.amount_requested = project.money_asked
#         sfproject.amount_still_needed = project.money_needed
#         sfproject.project_name = project.title
#         # Reference: sfproject.project_owner = project.owner
#         # -- Not the same as (closed,created, done validated)
#         #  -- fund, idea,act, result (if ...else...?)
#         # sfproject.status_project = project.phase
#         # Unknown: sfproject.target_group_s_of_the_project =
#
#         # SF Layout: Summary Project Details section.
#         # Unknown error: sfproject.country_in_which_the_project_is_located = project.country
#         sfproject.describe_the_project_in_one_sentence = project.description
#         # Unknown error: sfproject.describe_where_the_money_is_needed_for =
#         # Unknown error: sfproject.project_url = project.get_absolute_url
#
#         # SF Layout: Extensive project information section.
#         # Unknown: sfproject.third_half_project =
#         # Reference: sfproject.account =
#         # Reference:??? - sfproject.organization =
#         # Unknown: sfproject.comments =
#         # Unknown: sfproject.contribution_project_in_reducing_poverty =
#         # Unknown: sfproject.earth_charther_project =
#         # Unknown: sfproject.extensive_project_description =
#         # Unknown: sfproject.project_goals =
#         # Unknown: sfproject.sustainability =
#
#         # SF Layout: Project planning and budget section.
#         # Unknown: sfproject.additional_explanation_of_budget =
#         sfproject.end_date_of_the_project = project.planned_end_date
#         # Unknown: sfproject.expected_funding_through_other_resources =
#         # Unknown: sfproject.expected_project_results =
#         # Unknown: sfproject.funding_received_through_other_resources =
#         # Unknown: sfproject.need_for_volunteers =
#         # Unknown: sfproject.other_way_people_can_contribute =
#         # Unknown: sfproject.project_activities_and_timetable =
#         sfproject.starting_date_of_the_project = project.planned_start_date
#
#         # SF Layout: Millennium Goals section.
#         # Multipicklist: ?? - sfproject.millennium_goals =
#
#         # SF Layout: Tags section.
#         # Note: Not used like contact?-  sfproject.tags =
#
#         # SF Layout: Referrals section.
#         # Unknown: sfproject.name_referral_1 = project.referral.name
#         # Unknown: sfproject.name_referral_2 =
#         # Unknown: sfproject.name_referral_3 =
#         # Unknown: sfproject.description_referral_1 = project.referral.description
#         # Unknown: sfproject.description_referral_2 =
#         # Unknown: sfproject.description_referral_3 =
#         # Unknown: sfproject.email_address_referral_1 = project.referral.email
#         # Unknown: sfproject.email_address_referral_2 =
#         # Unknown: sfproject.email_address_referral_3 =
#         # Unknown: sfproject.relation_referral_1_with_project_org =
#         # Unknown: sfproject.relation_referral_2_with_project_org =
#         # Unknown: sfproject.relation_referral_3_with_project_org =
#
#         # SF Layout: Project Team Information section.
#         sfproject.project_created_date = project.created
#
#         # SF Layout: International Payment section.
#
#         # SF Layout: Other section.
#         sfproject.external_id = project.id
#
#         # Save the SF project.
#         sfproject.save()


# def sync_vouchers():
#     vouchers = Voucher.objects.all()
#     for voucher in vouchers:
#         # Find the corresponding SF voucher.
#         try:
#             sfvoucher = SalesforceVoucher.objects.filter(external_id=voucher.id).get()
#         except SalesforceVoucher.DoesNotExist:
#             sfvoucher = SalesforceVoucher()

# This is run when the script is executed with 'runscript'.
def run(test_run=False):
    sync_users(test_run)
    # sync_donations(test_run)
    # sync_organizations(test_run)
    # sync_projects(test_run)
    # sync_project_budgets(test_run)
    # sync_tasks(test_run)
    # sync_task_members(test_run)
    # sync_vouchers(test_run)
