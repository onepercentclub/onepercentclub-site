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
                                               SalesforceProjectBudget, SalesforceTask,
                                               SalesforceTaskMembers, SalesforceProject)


def sync_organizations():
    organizations = Organization.objects.all()
    for organization in organizations:
        # Find the corresponding SF organization.
        try:
            sforganization = SalesforceOrganization.objects.filter(external_id=organization.id).get()
        except SalesforceOrganization.DoesNotExist:
            sforganization = SalesforceOrganization()

        # SF Layout: Account details section.
        sforganization.name = organization.name
        sforganization.legal_status = organization.legal_status
        # Unkown (Business/Funds/1%IDEA): - sforganization.organization_type =

        # # SF Layout: Address Information section.
        sforganization.external_id = organization.id
        # if organization.address:
        #     sforganization.billing_city = organization.organizationaddress.country.name
            # sforganization.billing_street =
            # sforganization.billing_postal_code =
        # else:
        #     sforganization.billing_city = ''
        #     sforganization.billing_street = ''
        #     sforganization.billing_postal_code = ''
        # sforganization.email_address =
        # sforganization.phone =
        # sforganization.website =
        #
        # # SF Layout: Bank Account section.
        sforganization.address_bank = organization.account_bank_address
        sforganization.bank_account_name = organization.account_bank_name
        sforganization.bank_account_number = organization.account_number
        sforganization.bank_name = organization.name
        sforganization.bic_swift = organization.account_bic
        sforganization.country_bank = str(organization.account_bank_country)
        sforganization.iban_number = organization.account_iban

        # # SF Layout: Description section.
        sforganization.description = organization.description

        # # SF Layout: System Information.
        sforganization.created_date = organization.created

        # Save the SF project.
        sforganization.save()

        # # Delete SalesforceOrganization if the correspondig Organization doesn't exist.
        # sf_organizations = SalesforceOrganization.objects.all()
        # for sf_organization in sf_organizations:
        #     try:
        #         Organization.objects.filter(id=sf_organization.external_id).get()
        #     except Organization.DoesNotExist:
        #         sf_organization.delete()


def sync_users():
    users = BlueBottleUser.objects.all()
    for user in users:
        # Find the corresponding SF user.
        try:
            contact = SalesforceContact.objects.filter(external_id=user.id).get()
        except SalesforceContact.DoesNotExist:
            contact = SalesforceContact()

        # SF Layout: Subscription section - Set all the fields needed to save the user to the SF user.
        contact.category1 = user.user_type  # Selectable type in Salesforce english
        contact.email = user.email
        contact.user_name = user.username
        contact.is_active = user.is_active

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
        #contact.organization_account = SalesforceOrganization.objects.filter(external_id=contact.organization.id).get()
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
            contact.mailing_street = user.address.line1 + '\n' + user.address.line2
            if user.address.country:
                contact.mailing_country = user.address.country.name
            else:
                contact.mailing_country = ''
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
        contact.receive_newsletter = user.newsletter
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
        contact.save()

        # Delete SalesforceContact if the correspondig BlueBottleUser doesn't exist.
        # sf_users = SalesforceContact.objects.all()
        # for sf_user in sf_users:
        #     try:
        #         BlueBottleUser.objects.filter(id=sf_user.external_id).get()
        #     except BlueBottleUser.DoesNotExist:
        #         sf_user.delete()


def sync_donations():
    donations = Donation.objects.all()
    for donation in donations:
        # Find the corresponding SF donation.
        try:
            sfdonation = SalesforceDonation.objects.filter(external_id=donation.id).get()
        except SalesforceDonation.DoesNotExist:
            sfdonation = SalesforceDonation()

        # SF Layout: Donation Information section.
        sfdonation.amount = donation.amount
        # Unknown - sfdonation.close_date =
        sfdonation.name = str(donation.user.last_name) + " " + str(donation.user.first_name) + " - " + str(donation.donation_type)
        # Unknown - sfdonation.payment_method =
        # Unknown - sfdonation.organization = SalesforceOrganization.objects.filter(external_id=donation.organization.id).get()
        sfdonation.project = SalesforceProject.objects.filter(external_id=donation.project.id).get()
        # Unknown - sfdonation.stage_name =
        sfdonation.donation_type = donation.donation_type

        # SF Layout: Additional Information section.

        # SF Layout: Description Information section.

        # SF Layout: System Information section.
        sfdonation.donation_created_date = donation.created

        # SF: Other.
        sfdonation.donation_external_id = donation.id
        sfdonation.receiver = SalesforceContact.objects.filter(external_id=donation.user.id).get()

        # # Delete SalesforceDonation if the correspondig Donation doesn't exist.
        # sf_donations = SalesforceDonation.objects.all()
        # for sf_donation in sf_donations:
        #     try:
        #         Donation.objects.filter(id=sf_donation.external_id).get()
        #     except Donation.DoesNotExist:
        #         sf_donation.delete()


#def sync_tasks():
#    tasks = Task.objects.all()
#    for task in tasks:
#        # Find the corresponding SF task.
#        try:
#            sftask = SalesforceTask.objects.filter(external_id=task.id).get()
#        except SalesforceTask.DoesNotExist:
#            sftask = SalesforceTask()

        # # Delete SalesforceTask if the correspondig Task doesn't exist.
        # sf_tasks = SalesforceTask.objects.all()
        # for sf_task in sf_tasks:
        #     try:
        #         Task.objects.filter(id=sf_task.external_id).get()
        #     except Task.DoesNotExist:
        #         sf_task.delete()


def sync_projects():
    projects = Project.objects.all()
    for project in projects:
        # Find the corresponding SF project.
        try:
            sfproject = SalesforceProject.objects.filter(external_id=project.id).get()
        except SalesforceProject.DoesNotExist:
            sfproject = SalesforceProject()

        # SF Layout: 1%CLUB Project Detail section.
        sfproject.amount_at_the_moment = project.money_safe
        sfproject.amount_requested = project.money_asked
        sfproject.amount_still_needed = project.money_needed
        sfproject.project_name = project.title
        sfproject.project_owner = SalesforceContact.objects.filter(external_id=project.owner.id).get()
        # -- Not the same as (closed,created, done validated)
        #  -- fund, idea,act, result (if ...else...?)
        sfproject.status_project = project.phase
        # Unknown: sfproject.target_group_s_of_the_project =

        # SF Layout: Summary Project Details section.
        #sfproject.country_in_which_the_project_is_located = project.country
        sfproject.describe_the_project_in_one_sentence = project.description
        # Unknown error: sfproject.describe_where_the_money_is_needed_for =
        # Unknown error: sfproject.project_url = project.get_absolute_url

        # SF Layout: Extensive project information section.
        # Unknown: sfproject.third_half_project =
        sfproject.organization_account = SalesforceOrganization.objects.filter(external_id=project.organization.id).get()
        # Unknown: sfproject.comments =
        # Unknown: sfproject.contribution_project_in_reducing_poverty =
        # Unknown: sfproject.earth_charther_project =
        # Unknown: sfproject.extensive_project_description =
        # Unknown: sfproject.project_goals =
        # Unknown: sfproject.sustainability =

        # SF Layout: Project planning and budget section.
        # Unknown: sfproject.additional_explanation_of_budget =
        sfproject.end_date_of_the_project = project.planned_end_date
        # Unknown: sfproject.expected_funding_through_other_resources =
        # Unknown: sfproject.expected_project_results =
        # Unknown: sfproject.funding_received_through_other_resources =
        # Unknown: sfproject.need_for_volunteers =
        # Unknown: sfproject.other_way_people_can_contribute =
        # Unknown: sfproject.project_activities_and_timetable =
        sfproject.starting_date_of_the_project = project.planned_start_date

        # SF Layout: Millennium Goals section.
        # Unknown - Multipicklist: ?? - sfproject.millennium_goals =

        # SF Layout: Tags section.
        # Note: Not used like contact?-  sfproject.tags =

        # SF Layout: Referrals section.
        # Unknown: sfproject.name_referral_1 = project.referral.name
        # Unknown: sfproject.name_referral_2 =
        # Unknown: sfproject.name_referral_3 =
        # Unknown: sfproject.description_referral_1 = project.referral.description
        # Unknown: sfproject.description_referral_2 =
        # Unknown: sfproject.description_referral_3 =
        # Unknown: sfproject.email_address_referral_1 = project.referral.email
        # Unknown: sfproject.email_address_referral_2 =
        # Unknown: sfproject.email_address_referral_3 =
        # Unknown: sfproject.relation_referral_1_with_project_org =
        # Unknown: sfproject.relation_referral_2_with_project_org =
        # Unknown: sfproject.relation_referral_3_with_project_org =

        # SF Layout: Project Team Information section.
        sfproject.project_created_date = project.created

        # SF Layout: International Payment section.

        # SF Layout: Other section.
        sfproject.external_id = project.id

        # Save the SF project.
        sfproject.save()

        # # Delete SalesforceProject if the correspondig Project doesn't exist.
        # sf_projects = SalesforceProject.objects.all()
        # for sf_project in sf_projects:
        #     try:
        #         Project.objects.filter(id=sf_project.external_id).get()
        #     except Project.DoesNotExist:
        #         sf_project.delete()


# def sync_vouchers():
#     vouchers = Voucher.objects.all()
#     for voucher in vouchers:
#         # Find the corresponding SF voucher.
#         try:
#             sfvoucher = SalesforceVoucher.objects.filter(external_id=voucher.id).get()
#         except SalesforceVoucher.DoesNotExist:
#             sfvoucher = SalesforceVoucher()

        # # Delete SalesforceVoucher if the correspondig Voucher doesn't exist.
        # sf_vouchers = SalesforceVoucher.objects.all()
        # for sf_voucher in sf_vouchers:
        #     try:
        #         Voucher.objects.filter(id=sf_voucher.external_id).get()
        #     except Voucher.DoesNotExist:
        #         sf_voucher.delete()


def run():
    """
    This is run when the script is executed with 'runscript'. The sections need to be run in a specific order
    because of foreign key dependencies.
    """
    sync_organizations()
    sync_users()
    sync_projects()
    # sync_donations()
    # sync_project_budgets()
    # sync_tasks()
    # sync_task_members()
    # sync_vouchers()